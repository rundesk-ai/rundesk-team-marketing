#!/usr/bin/env python3
"""Offline tests for google-search-console."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import socket
import struct
import subprocess
import sys
import time
import tempfile
import datetime as dt
import unittest
import urllib.error
import zoneinfo
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "google-search-console.py"
LAUNCHER = HERE.parent / "google-search-console"


def load_module():
    spec = importlib.util.spec_from_file_location("google_search_console_module", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


class RawResponse(Response):
    """A response body Google never should have sent, kept exactly as received."""

    def read(self):
        return self.payload


class StubAccess:
    """An account Rundesk has already granted, so a case can start at the Google boundary."""

    name = "example"

    def token(self):
        return "access"


class SearchConsoleTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.access = StubAccess()

    def test_request_error_exposes_google_message_but_not_authorization(self):
        error = urllib.error.HTTPError(
            "https://www.googleapis.com/example", 403, "Forbidden", {},
            io.BytesIO(json.dumps({"error": {"message": "Permission denied"}}).encode()),
        )
        with self.assertRaises(self.module.SearchConsoleError) as raised:
            self.module.request_json(
                "https://www.googleapis.com/example",
                headers={"Authorization": "Bearer hidden"},
                opener=lambda *args, **kwargs: (_ for _ in ()).throw(error),
            )
        self.assertIn("Permission denied", str(raised.exception))
        self.assertNotIn("hidden", str(raised.exception))

    def test_redirects_are_refused(self):
        handler = self.module.RejectRedirectHandler()
        request = self.module.urllib.request.Request(
            self.module.WEBMASTERS_API + "/sites",
            headers={"Authorization": "Bearer secret"},
        )
        self.assertIsNone(
            handler.redirect_request(
                request, None, 302, "Found", {}, "https://example.test/intercept"
            )
        )

    def test_sites_uses_exact_api_and_bounds_output(self):
        args = SimpleNamespace(profile="example", limit=1, json=False)
        payload = {"siteEntry": [
            {"siteUrl": "sc-domain:example.test", "permissionLevel": "siteOwner"},
            {"siteUrl": "https://www.example.test/", "permissionLevel": "siteRestrictedUser"},
        ]}
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", return_value=payload
        ) as call, redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            self.module.cmd_sites(args)
        call.assert_called_once_with(self.access, "/sites")
        self.assertIn("sc-domain:example.test", output.getvalue())
        self.assertNotIn("www.example.test", output.getvalue())
        self.assertIn("truncated", error.getvalue())

    def test_performance_encodes_property_and_posts_requested_dimensions(self):
        args = SimpleNamespace(
            profile="example", site="https://www.example.test/", days=28,
            start_date="2026-07-01", end_date="2026-07-31",
            dimension=["query", "page"], search_type="web", filter=[], limit=10, json=True,
        )
        payload = {"rows": [{"keys": ["example", "https://www.example.test/page"], "clicks": 3, "impressions": 20, "ctr": 0.15, "position": 4.2}]}
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", return_value=payload
        ) as call, redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
            self.module.cmd_performance(args)
        path = call.call_args.args[1]
        body = call.call_args.kwargs["body"]
        self.assertIn("https%3A%2F%2Fwww.example.test%2F", path)
        self.assertEqual(body["dimensions"], ["query", "page"])
        self.assertEqual(body["rowLimit"], 10)
        self.assertEqual(json.loads(output.getvalue())[0]["clicks"], 3)

    def test_performance_warns_when_row_limit_is_reached(self):
        args = SimpleNamespace(
            profile="example", site="sc-domain:example.test", days=28,
            start_date="2026-07-01", end_date="2026-07-31",
            dimension=["query"], search_type=None, filter=[], limit=1, json=False,
        )
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", return_value={"rows": [{"keys": ["example"]}]}
        ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as error:
            self.module.cmd_performance(args)
        self.assertIn("may be truncated", error.getvalue())

    def test_inspect_url_uses_inspection_api_and_normalizes_result(self):
        args = SimpleNamespace(profile="example", site="sc-domain:example.test", url="https://example.test/page", json=True)
        payload = {"inspectionResult": {"indexStatusResult": {"verdict": "PASS", "coverageState": "Submitted and indexed", "lastCrawlTime": "2026-08-01T12:00:00Z"}}}
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", return_value=payload
        ) as call, redirect_stdout(io.StringIO()) as output:
            self.module.cmd_inspect(args)
        self.assertEqual(call.call_args.kwargs["base"], self.module.INSPECTION_API)
        self.assertEqual(call.call_args.kwargs["body"]["inspectionUrl"], args.url)
        self.assertEqual(json.loads(output.getvalue())[0]["verdict"], "PASS")

    def test_inspect_url_refuses_an_empty_success_response(self):
        args = SimpleNamespace(
            profile="example",
            site="sc-domain:example.test",
            url="https://example.test/page",
            json=True,
        )
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", return_value={}
        ):
            with self.assertRaisesRegex(self.module.SearchConsoleError, "no URL inspection result"):
                self.module.cmd_inspect(args)

    def test_sitemaps_lists_compact_fields(self):
        args = SimpleNamespace(profile="example", site="sc-domain:example.test", limit=2, json=False)
        payload = {"sitemap": [{"path": "https://example.test/sitemap.xml", "type": "sitemap", "isPending": False, "errors": "0", "warnings": "1"}]}
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", return_value=payload
        ), redirect_stdout(io.StringIO()) as output:
            self.module.cmd_sitemaps(args)
        self.assertIn("sitemap.xml", output.getvalue())
        self.assertIn("warnings", output.getvalue())

    def test_date_range_rejects_partial_or_reversed_dates(self):
        base = {"days": 28, "start_date": "2026-08-02", "end_date": None}
        with self.assertRaises(self.module.SearchConsoleError):
            self.module.date_range(SimpleNamespace(**base))
        with self.assertRaises(self.module.SearchConsoleError):
            self.module.date_range(SimpleNamespace(days=28, start_date="2026-08-02", end_date="2026-08-01"))

    def test_default_range_uses_complete_pacific_days_not_utc_days(self):
        # Google buckets Search Console rows by Pacific day. Late UTC evening is still the prior
        # Pacific day, so a UTC clock would report one day too many as complete.
        cases = (
            ("2026-08-17T06:59:59+00:00", "2026-07-19", "2026-08-15"),
            ("2026-08-17T07:00:00+00:00", "2026-07-20", "2026-08-16"),
            ("2026-01-05T07:59:59+00:00", "2025-12-07", "2026-01-03"),
            ("2026-01-05T08:00:00+00:00", "2025-12-08", "2026-01-04"),
        )
        args = SimpleNamespace(days=28, start_date=None, end_date=None)
        for frozen, start, end in cases:
            with self.subTest(now=frozen):
                with patch.object(
                    self.module, "utc_now", return_value=dt.datetime.fromisoformat(frozen)
                ):
                    self.assertEqual((start, end), self.module.date_range(args))

    def test_pacific_fallback_tracks_the_iana_zone_across_dst_transitions(self):
        try:
            iana = zoneinfo.ZoneInfo(self.module.PACIFIC_ZONE)
        except zoneinfo.ZoneInfoNotFoundError:  # pragma: no cover - depends on the host database
            self.skipTest("no IANA time zone database is installed")
        fallback = self.module.PacificFallback()
        moment = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
        limit = dt.datetime(2028, 1, 1, tzinfo=dt.timezone.utc)
        while moment < limit:
            expected = moment.astimezone(iana)
            actual = moment.astimezone(fallback)
            self.assertEqual(expected.replace(tzinfo=None), actual.replace(tzinfo=None), moment)
            self.assertEqual(expected.date(), actual.date(), moment)
            moment += dt.timedelta(hours=1)

    def test_malformed_and_non_object_payloads_are_refused(self):
        cases = (
            (b"<html>not json</html>", "invalid JSON"),
            (b"[]", "malformed API response"),
            (b'"text"', "malformed API response"),
            (b"7", "malformed API response"),
            (b"null", "malformed API response"),
        )
        for body, expected in cases:
            with self.subTest(body=body):
                with self.assertRaisesRegex(self.module.SearchConsoleError, expected):
                    self.module.request_json(
                        "https://www.googleapis.com/example",
                        opener=lambda *args, **kwargs: RawResponse(body),
                    )

    def test_commands_refuse_wrong_collection_and_object_shapes(self):
        sites = SimpleNamespace(profile="example", limit=5, json=False)
        performance = SimpleNamespace(
            profile="example", site="sc-domain:example.test", days=28, start_date=None,
            end_date=None, dimension=["query"], search_type=None, filter=[], limit=5, json=False,
        )
        sitemaps = SimpleNamespace(profile="example", site="sc-domain:example.test", limit=5, json=False)
        cases = (
            (self.module.cmd_sites, sites, {"siteEntry": {"siteUrl": "sc-domain:example.test"}}, "site entry collection"),
            (self.module.cmd_sites, sites, {"siteEntry": ["sc-domain:example.test"]}, "malformed site entry"),
            (self.module.cmd_performance, performance, {"rows": {"keys": []}}, "performance row collection"),
            (self.module.cmd_performance, performance, {"rows": ["example"]}, "malformed performance row"),
            (self.module.cmd_performance, performance, {"rows": [{"keys": "example"}]}, "performance row key collection"),
            (self.module.cmd_sitemaps, sitemaps, {"sitemap": {"path": "x"}}, "sitemap entry collection"),
            (self.module.cmd_sitemaps, sitemaps, {"sitemap": [7]}, "malformed sitemap entry"),
        )
        for command, args, payload, expected in cases:
            with self.subTest(command=command.__name__, payload=payload):
                with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
                    self.module, "api", return_value=payload
                ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    with self.assertRaisesRegex(self.module.SearchConsoleError, expected):
                        command(args)

    def test_malformed_response_exits_two_instead_of_raising(self):
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "open_url", side_effect=lambda *a, **k: RawResponse(b"<html>not json</html>")
        ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as error:
            code = self.module.main(["sites", "--profile", "example"])
        self.assertEqual(2, code)
        self.assertIn("invalid JSON", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())

    def test_main_rejects_unbounded_limit_before_network(self):
        with patch.dict(os.environ, {}, clear=True), redirect_stderr(io.StringIO()) as error:
            code = self.module.main(["sites", "--profile", "example", "--limit", "1001"])
        self.assertEqual(code, 2)
        self.assertIn("between 1 and 1000", error.getvalue())

    def performance_args(self, **overrides):
        values = dict(
            profile="example", site="https://www.example.test/", days=28, start_date="2026-07-01",
            end_date="2026-07-31", dimension=["query"], search_type=None, filter=[], limit=25, json=True,
        )
        values.update(overrides)
        return SimpleNamespace(**values)

    def performance_body(self, args, payload=None):
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", return_value=payload if payload is not None else {"rows": []}
        ) as call, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.module.cmd_performance(args)
        return call.call_args.kwargs["body"]

    def submit_args(self, **overrides):
        values = dict(
            profile="example", site="https://www.example.test/",
            sitemap="https://www.example.test/sitemap.xml", confirm=False, json=False,
        )
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_unfiltered_performance_body_is_exactly_what_it_was_before_filters(self):
        body = self.performance_body(self.performance_args())
        self.assertEqual(
            {"startDate": "2026-07-01", "endDate": "2026-07-31", "rowLimit": 25, "startRow": 0,
             "dimensions": ["query"]},
            body,
        )
        self.assertNotIn("dimensionFilterGroups", body)

    def test_filters_build_one_official_and_group_in_argument_order(self):
        args = self.performance_args(filter=[
            "query:contains:running shoes",
            "page:equals:https://www.example.test/a:b?x=1&y=2",
            "country:equals:USA",
            "device:equals:mobile",
            "searchAppearance:equals:AMP_BLUE_LINK",
        ])
        self.assertEqual(
            [{"groupType": "and", "filters": [
                {"dimension": "query", "operator": "contains", "expression": "running shoes"},
                {"dimension": "page", "operator": "equals",
                 "expression": "https://www.example.test/a:b?x=1&y=2"},
                {"dimension": "country", "operator": "equals", "expression": "usa"},
                {"dimension": "device", "operator": "equals", "expression": "MOBILE"},
                {"dimension": "searchAppearance", "operator": "equals", "expression": "AMP_BLUE_LINK"},
            ]}],
            self.performance_body(args)["dimensionFilterGroups"],
        )

    def test_substring_and_regex_expressions_are_sent_exactly_as_typed(self):
        args = self.performance_args(filter=[
            "country:contains:US", "device:includingRegex:^MOB", "searchAppearance:contains:amp",
            "query:excludingRegex:(?-i)Brand",
        ])
        filters = self.performance_body(args)["dimensionFilterGroups"][0]["filters"]
        self.assertEqual(
            ["US", "^MOB", "amp", "(?-i)Brand"], [item["expression"] for item in filters]
        )

    def test_filtered_performance_request_reaches_google_as_declared_json(self):
        sent = []

        def opener(request, timeout):
            sent.append(request)
            return Response({"rows": []})

        args = self.performance_args(filter=["page:includingRegex:^/blog/.*$", "query:contains:caf\u00e9 & 100%"])
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "open_url", side_effect=opener
        ), redirect_stdout(
            io.StringIO()
        ), redirect_stderr(io.StringIO()):
            self.module.cmd_performance(args)
        request = sent[0]
        self.assertEqual("POST", request.get_method())
        self.assertEqual(
            "https://www.googleapis.com/webmasters/v3/sites/"
            "https%3A%2F%2Fwww.example.test%2F/searchAnalytics/query",
            request.full_url,
        )
        self.assertEqual("application/json", request.get_header("Content-type"))
        # Filters travel in the JSON body, so nothing in them may arrive percent-encoded.
        self.assertEqual(
            [{"groupType": "and", "filters": [
                {"dimension": "page", "operator": "includingRegex", "expression": "^/blog/.*$"},
                {"dimension": "query", "operator": "contains", "expression": "caf\u00e9 & 100%"},
            ]}],
            json.loads(request.data.decode("utf-8"))["dimensionFilterGroups"],
        )

    def test_malformed_filters_are_refused_before_configuration_or_network(self):
        cases = (
            ("", "must be DIMENSION:OPERATOR:EXPRESSION"),
            ("query", "must be DIMENSION:OPERATOR:EXPRESSION"),
            ("query:contains", "must be DIMENSION:OPERATOR:EXPRESSION"),
            ("date:equals:2026-08-01", "dimension 'date' must be one of"),
            ("hour:equals:5", "dimension 'hour' must be one of"),
            ("QUERY:equals:shoes", "dimension 'QUERY' must be one of"),
            ("query:Equals:shoes", "operator 'Equals' must be one of"),
            ("query:regex:shoes", "operator 'regex' must be one of"),
            ("query:contains:", "needs a non-empty expression"),
            ("country:equals:US", "alpha-3"),
            ("country:equals:united", "alpha-3"),
            ("country:notEquals:12", "alpha-3"),
            ("device:equals:phone", "must be one of: DESKTOP, MOBILE, TABLET"),
            ("device:notEquals:", "needs a non-empty expression"),
            ("query:contains:" + "x" * 4097, "exceeds 4096 characters"),
        )
        for value, expected in cases:
            with self.subTest(filter=value[:40]):
                with patch.object(
                    self.module, "selected_access", side_effect=AssertionError("configuration")
                ), patch.object(self.module, "api", side_effect=AssertionError("network")):
                    with self.assertRaisesRegex(self.module.SearchConsoleError, expected):
                        self.module.cmd_performance(self.performance_args(filter=[value]))

    def test_main_rejects_a_malformed_filter_without_contacting_google(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            self.module.urllib.request, "urlopen", side_effect=AssertionError("network")
        ), redirect_stderr(io.StringIO()) as error:
            code = self.module.main([
                "performance", "--profile", "example", "--site", "sc-domain:example.test",
                "--filter", "query:like:shoes",
            ])
        self.assertEqual(2, code)
        self.assertIn("operator 'like'", error.getvalue())

    def test_submit_sitemap_previews_without_reaching_google_and_refuses(self):
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", side_effect=AssertionError("network")
        ), patch.object(
            self.module, "open_url", side_effect=AssertionError("network")
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
            with self.assertRaisesRegex(self.module.SearchConsoleError, "without --confirm"):
                self.module.cmd_submit_sitemap(self.submit_args())
        printed = output.getvalue()
        self.assertIn("preview", printed)
        self.assertIn("PUT", printed)
        self.assertIn(
            "https://www.googleapis.com/webmasters/v3/sites/https%3A%2F%2Fwww.example.test%2F"
            "/sitemaps/https%3A%2F%2Fwww.example.test%2Fsitemap.xml",
            printed,
        )
        self.assertIn("https://www.googleapis.com/auth/webmasters", printed)

    def test_submit_sitemap_preview_exits_two_in_both_output_modes(self):
        for extra in ([], ["--json"]):
            with self.subTest(json=bool(extra)):
                with patch.dict(os.environ, {}, clear=True), patch.object(
                    self.module.urllib.request, "urlopen", side_effect=AssertionError("network")
                ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
                    code = self.module.main([
                        "submit-sitemap", "--profile", "example", "--site", "https://www.example.test/",
                        "--sitemap", "https://www.example.test/sitemap.xml", *extra,
                    ])
                self.assertEqual(2, code)
                self.assertIn("Refusing to submit", error.getvalue())
                if extra:
                    self.assertEqual("preview", json.loads(output.getvalue())[0]["state"])
                else:
                    self.assertIn("preview", output.getvalue())

    def test_submit_sitemap_puts_the_official_path_then_verifies_by_reading_it_back(self):
        entry = {
            "path": "https://www.example.test/sitemap.xml", "type": "sitemap", "isPending": True,
            "lastSubmitted": "2026-08-17T00:00:00.000Z", "warnings": 0, "errors": 0,
        }
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", side_effect=[{}, entry]
        ) as call, redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
            self.module.cmd_submit_sitemap(self.submit_args(confirm=True, json=True))
        expected = ("/sites/https%3A%2F%2Fwww.example.test%2F"
                    "/sitemaps/https%3A%2F%2Fwww.example.test%2Fsitemap.xml")
        submit, verify = call.call_args_list
        self.assertEqual((self.access, expected), submit.args)
        self.assertEqual({"method": "PUT"}, submit.kwargs)
        self.assertEqual((self.access, expected), verify.args)
        self.assertEqual({}, verify.kwargs)
        row = json.loads(output.getvalue())[0]
        self.assertEqual("submitted", row["state"])
        self.assertEqual("https://www.example.test/sitemap.xml", row["path"])
        self.assertTrue(row["pending"])

    def test_submit_sitemap_refuses_to_report_success_it_cannot_verify(self):
        for payload in ({}, {"path": ""}, {"path": 7}, {"errors": 0}):
            with self.subTest(payload=payload):
                with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
                    self.module, "api", side_effect=[{}, payload]
                ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    with self.assertRaisesRegex(
                        self.module.SearchConsoleError, "did not return the sitemap"
                    ):
                        self.module.cmd_submit_sitemap(self.submit_args(confirm=True))

    def test_submit_sitemap_refuses_a_malformed_verification_response(self):
        for payload in ([], "ok", 7, None):
            with self.subTest(payload=payload):
                with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
                    self.module, "api", side_effect=[{}, payload]
                ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    with self.assertRaisesRegex(
                        self.module.SearchConsoleError, "malformed sitemap entry"
                    ):
                        self.module.cmd_submit_sitemap(self.submit_args(confirm=True))

    def test_submit_sitemap_reports_a_path_google_rewrote(self):
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api", side_effect=[{}, {"path": "https://www.example.test/sitemap_index.xml"}]
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            self.module.cmd_submit_sitemap(self.submit_args(confirm=True))
        self.assertIn("recorded the sitemap as https://www.example.test/sitemap_index.xml", error.getvalue())
        self.assertIn("sitemap_index.xml", output.getvalue())

    def test_submit_sitemap_refuses_anything_that_is_not_an_absolute_web_url(self):
        cases = ("", "sitemap.xml", "/sitemap.xml", "//example.test/sitemap.xml",
                 "ftp://example.test/sitemap.xml", "file:///etc/passwd", "javascript:alert(1)",
                 "https:///sitemap.xml", "https://user@example.test/sitemap.xml",
                 "https://user:password@example.test/sitemap.xml")
        for value in cases:
            with self.subTest(sitemap=value):
                with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
                    self.module, "api", side_effect=AssertionError("network")
                ), redirect_stderr(io.StringIO()):
                    with self.assertRaisesRegex(
                        self.module.SearchConsoleError, "absolute http or https URL without credentials"
                    ):
                        self.module.cmd_submit_sitemap(self.submit_args(sitemap=value, confirm=True))

    def test_submit_sitemap_warns_only_when_a_url_prefix_property_cannot_contain_it(self):
        cases = (
            ("https://www.example.test/", "https://other.test/sitemap.xml", True),
            ("https://www.example.test/", "https://www.example.test/a/sitemap.xml", False),
            ("sc-domain:example.test", "https://blog.example.test/sitemap.xml", False),
        )
        for site, sitemap, warns in cases:
            with self.subTest(site=site, sitemap=sitemap):
                with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
                    self.module, "api", side_effect=[{}, {"path": sitemap}]
                ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as error:
                    self.module.cmd_submit_sitemap(
                        self.submit_args(site=site, sitemap=sitemap, confirm=True)
                    )
                self.assertEqual(warns, "outside the property" in error.getvalue())

    def test_writing_and_filtering_paths_never_print_credentials_or_tokens(self):
        env = {
            "GOOGLE_SEARCH_CONSOLE_CLIENT_ID__EXAMPLE": "leak-client-id",
            "GOOGLE_SEARCH_CONSOLE_CLIENT_SECRET__EXAMPLE": "leak-client-secret",
            "GOOGLE_SEARCH_CONSOLE_REFRESH_TOKEN__EXAMPLE": "leak-refresh-token",
        }
        secrets = ("leak-client-id", "leak-client-secret", "leak-refresh-token",
                   "leak-access-token", "Bearer", "Authorization")

        def opener(request, timeout):
            if request.full_url == self.module.TOKEN_URL:
                return Response({"access_token": "leak-access-token"})
            if request.get_method() == "PUT":
                return RawResponse(b"")
            if "/sitemaps/" in request.full_url:
                return Response({"path": "https://www.example.test/sitemap.xml"})
            return Response({"rows": [{"keys": ["shoes"], "clicks": 1}]})

        base = ["--profile", "example", "--site", "https://www.example.test/"]
        sitemap = ["--sitemap", "https://www.example.test/sitemap.xml"]
        commands = (
            ["submit-sitemap", *base, *sitemap],
            ["submit-sitemap", *base, *sitemap, "--confirm"],
            ["submit-sitemap", *base, *sitemap, "--confirm", "--json"],
            ["performance", *base, "--dimension", "query", "--filter", "query:contains:shoes"],
        )
        for argv in commands:
            with self.subTest(command=" ".join(argv[:1] + argv[5:])):
                with patch.dict(os.environ, env, clear=True), patch.object(
                    self.module, "open_url", side_effect=opener
                ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
                    self.module.main(argv)
                printed = output.getvalue() + error.getvalue()
                for secret in secrets:
                    self.assertNotIn(secret, printed)

    def test_launcher_help_is_credential_free_and_resolves_outside_repo(self):
        result = subprocess.run(
            [str(LAUNCHER), "--help"], cwd="/tmp", env={"PATH": os.environ.get("PATH", "")},
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Google Search Console", result.stdout)


# A stand-in for the Rundesk CLI that answers the hidden `_oauth` bridge exactly as Rundesk
# documents it, including the checks Rundesk makes on the response descriptor before it writes.
# Every case below therefore fails if this package sends the wrong words, the wrong capability, or a
# descriptor Rundesk would refuse.
FAKE_RUNDESK = '''#!{python}
import json
import os
import socket
import stat
import struct
import sys
import time

MAX_FRAME = 65536
PROVIDER = "google"
CAPABILITIES = ("analytics", "merchant", "search-console")
plan = json.loads(os.environ["FAKE_RUNDESK_PLAN"])
argv = sys.argv[1:]
with open(plan["record"], "a", encoding="utf-8") as record:
    record.write(json.dumps(argv) + chr(10))


framed = None


def refuse(said, code=1):
    reason = said.split(" — ", 1)[-1]
    if framed is not None and code == 1:
        answer({{"ok": False, "error": reason}}, stop=False)
    print(said, file=sys.stderr)
    raise SystemExit(code)


def option(name):
    return argv[argv.index(name) + 1] if name in argv else ""


if plan["mode"] in ("orphan-holds-stderr", "hang-with-orphan", "refuse-with-orphan"):
    # **A descendant that inherits this process's stderr and outlives it**, which is what a browser
    # opened by `rundesk login` really is. The pipe the caller is reading never reaches end-of-file
    # while that descendant lives, whatever this process does next.
    import subprocess
    left = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"])
    with open(plan["orphan"], "a", encoding="utf-8") as writing:
        writing.write(str(left.pid) + chr(10))
    if plan["mode"] == "hang-with-orphan":
        time.sleep(600)
    if plan["mode"] == "refuse-with-orphan":
        refuse("login: FAILED — Google login was declined; no profile was changed")
    # Otherwise fall through and behave exactly as a working Rundesk does: this is the successful
    # sign-in whose browser is still open, not a failure.

if plan["mode"] == "old":
    print("usage: rundesk [-h] {{agents,ask,env}} ...", file=sys.stderr)
    print("rundesk: error: argument command: invalid choice: %r (choose from 'agents', 'ask')"
          % argv[0], file=sys.stderr)
    raise SystemExit(2)

if argv[0] == "login":
    if argv[1] != "google":
        refuse("rundesk: error: argument login_provider: invalid choice: %r" % argv[1], 2)
    if plan["mode"] == "login-hang":
        time.sleep(600)
    if plan["mode"] == "login-refused":
        refuse("login: FAILED — Google login was declined; no profile was changed")
    print("Connected owner@example.test")
    raise SystemExit(0)

if argv[0] != "_oauth":
    refuse("rundesk: error: argument command: invalid choice: %r" % argv[0], 2)

fd = int(option("--response-fd"))
if fd in (0, 1, 2) or fd < 0:
    refuse("google: FAILED — the response FD must be inherited and may not be stdin, stdout, or stderr")
try:
    kind = os.fstat(fd).st_mode
    checked = socket.socket(fileno=os.dup(fd))
except OSError:
    refuse("google: FAILED — the response FD is not an open socket")
try:
    if (not stat.S_ISSOCK(kind) or checked.family != socket.AF_UNIX
            or checked.getsockname() not in ("", b"") or checked.getpeername() not in ("", b"")):
        refuse("google: FAILED — the response FD must be a connected anonymous local socket")
except OSError:
    refuse("google: FAILED — the response FD must be a connected anonymous local socket")
finally:
    checked.close()
def answer(payload, stop=True):
    if plan["mode"] == "silent":
        raise SystemExit(0)
    if plan["mode"] == "hang":
        time.sleep(600)
    if plan["mode"] == "garbage":
        body = b"{{not json"
    else:
        body = json.dumps(dict(payload, version=plan.get("version", 1)),
                          separators=(",", ":")).encode("utf-8")
    if len(body) > MAX_FRAME:
        refuse("google: FAILED — the response is too large for the Google protocol")
    os.write(fd, struct.pack(">I", len(body)) + body)
    if plan["mode"] == "frame-then-hang":
        time.sleep(600)
    if stop:
        raise SystemExit(0)


framed = fd

if argv[1] not in ("accounts", "access"):
    refuse("rundesk: error: argument oauth_action: invalid choice: %r" % argv[1], 2)
if argv[2] != PROVIDER:
    refuse("oauth: FAILED — there is no installed OAuth provider called %r (available: %s)"
           % (argv[2], PROVIDER))

held = plan["accounts"].get(option("--profile").strip().upper() or "DEFAULT")
if held is None:
    refuse("google: FAILED — set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET with "
           "`rundesk env set` for this OAuth app profile")


if argv[1] == "accounts":
    answer({{"ok": True, "accounts": sorted(held)}})

if argv[3] not in CAPABILITIES:
    refuse("oauth: FAILED — the google provider declares no capability called %r" % argv[3])
if plan["mode"] == "scope":
    refuse("google: FAILED — Google did not return a reusable grant for every requested scope")

wanted = option("--email")
matched = [name for name in held
           if not wanted or name.casefold() == wanted.casefold()]
if not matched:
    refuse("google: FAILED — no matching Google profile is connected; run `rundesk login google`")
if len(matched) != 1:
    refuse("google: FAILED — more than one Google profile is connected; choose --email from: "
           + ", ".join(sorted(matched)))
# Derived here rather than carried in the plan, so no token this package handles is ever a
# value in the environment the case runs with.
email = matched[0]
expiry = -60 if plan["mode"] == "expired" else 3600
granted = {{"ok": True, "access_token": "access-token-for-" + email, "token_type": "Bearer",
           "expires_at": int(plan["now"]) + expiry, "email": email, "subject": "subject-" + email}}
if plan["mode"] == "wrong-token-type":
    granted["token_type"] = "mac"
if plan["mode"] == "no-subject":
    del granted["subject"]
if plan["mode"] == "other-identity":
    # Rundesk answering for an account other than the one asked for. Rundesk checks this itself;
    # the point of the mode is that this package must not take the answer on trust.
    granted["email"] = "someone-else@example.test"
    granted["subject"] = "subject-someone-else@example.test"
answer(granted)
'''.format(python=sys.executable)


#: What the stand-in above hands back for the account these cases sign in as.
MANAGED_TOKEN = "access-token-for-owner@example.test"


class RundeskBridgeTest(unittest.TestCase):
    """The catalog side of Rundesk-managed Google sign-in, against a faithful stand-in CLI."""

    def setUp(self):
        self.module = load_module()
        home = tempfile.TemporaryDirectory()
        self.addCleanup(home.cleanup)
        self.home = Path(home.name)
        self.record = self.home / "argv.jsonl"
        self.command = self.home / "rundesk"
        self.command.write_text(FAKE_RUNDESK, encoding="utf-8")
        self.command.chmod(0o755)
        self.plan = {
            "record": str(self.record),
            "mode": "ok",
            "now": int(time.time()),
            "accounts": {"DEFAULT": ["owner@example.test"]},
        }
        self.requests = []
        self.payloads = []

    def opener(self, request, timeout=30):
        self.requests.append(request)
        return Response(self.payloads.pop(0) if self.payloads else {})

    def environment(self, **extra):
        env = {
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.home / "config"),
            "PATH": os.environ.get("PATH", os.defpath),
            "RUNDESK_COMMAND": str(self.command),
            "FAKE_RUNDESK_PLAN": json.dumps(self.plan),
        }
        env.update(extra)
        return env

    def invoke(self, argv, **extra):
        out, err = io.StringIO(), io.StringIO()
        with patch.dict(os.environ, self.environment(**extra), clear=True), patch.object(
            self.module, "open_url", self.opener
        ), redirect_stdout(out), redirect_stderr(err):
            code = self.module.main(argv)
        return code, out.getvalue(), err.getvalue()

    def asked(self):
        if not self.record.exists():
            return []
        return [json.loads(line) for line in self.record.read_text(encoding="utf-8").splitlines()]

    def sites_payload(self):
        return {"siteEntry": [{"siteUrl": "https://example.test/", "permissionLevel": "siteOwner"}]}

    def authorization(self):
        return [request.get_header("Authorization") for request in self.requests]

    # --- the protocol itself ------------------------------------------------------------------

    def test_access_is_asked_for_over_an_inherited_pipe_and_used_only_as_a_header(self):
        self.payloads = [self.sites_payload()]
        code, out, err = self.invoke(["sites"])
        self.assertEqual(0, code, err)
        asked = self.asked()
        self.assertEqual(1, len(asked))
        self.assertEqual(["_oauth", "access", "google", "search-console", "--response-fd"],
                         asked[0][:5])
        # The stand-in makes Rundesk's own check, so passing proves an inherited connected unnamed
        # local socket rather than 0, 1, 2, a pipe, a named socket, or a file.
        self.assertGreater(int(asked[0][5]), 2)
        self.assertEqual(["Bearer " + MANAGED_TOKEN], self.authorization())
        self.assertIn("https://example.test/", out)

    def pair(self):
        """One socket pair, closed however the case ends."""
        ours, theirs = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(ours.close)
        self.addCleanup(theirs.close)
        return ours, theirs

    def test_frame_must_be_version_one_json_of_the_documented_size(self):
        for body, expected in (
            (json.dumps({"version": 2, "ok": True}).encode(), "version this package cannot read"),
            (b"{not json", "malformed Google response"),
        ):
            with self.subTest(body=body):
                ours, theirs = self.pair()
                theirs.sendall(struct.pack(">I", len(body)) + body)
                theirs.close()
                with self.assertRaisesRegex(self.module.SearchConsoleError, expected):
                    self.module.read_frame(ours, time.monotonic() + 5)

    def test_a_framed_refusal_carries_its_reason_and_nothing_of_the_frame(self):
        self.assertEqual("no account", self.module.framed_error({"ok": False, "error": "no account"}))
        self.assertEqual("", self.module.framed_error({"ok": False}))
        self.assertEqual("", self.module.framed_error({"ok": False, "error": 7}))
        self.assertEqual(self.module.MAX_REASON,
                         len(self.module.framed_error({"ok": False, "error": "x" * 9000})))

    def test_frame_larger_than_the_protocol_allows_is_refused_before_reading_it(self):
        ours, theirs = self.pair()
        theirs.sendall(struct.pack(">I", self.module.MAX_FRAME + 1))
        theirs.close()
        with self.assertRaisesRegex(self.module.SearchConsoleError, "oversized"):
            self.module.read_frame(ours, time.monotonic() + 5)

    def test_truncated_and_silent_answers_are_refused_rather_than_waited_on(self):
        ours, theirs = self.pair()
        theirs.sendall(struct.pack(">I", 64) + b"{")
        theirs.close()
        with self.assertRaisesRegex(self.module.SearchConsoleError, "closed the Google response"):
            self.module.read_frame(ours, time.monotonic() + 5)
        quiet, _held = self.pair()
        with self.assertRaisesRegex(self.module.SearchConsoleError, "in time"):
            self.module.read_frame(quiet, time.monotonic() + 0.05)

    def test_rundesk_refuses_a_pipe_where_the_protocol_requires_a_socket(self):
        """The stand-in makes Rundesk's own check, which is what the passing cases rely on."""
        read_fd, write_fd = os.pipe()
        self.addCleanup(os.close, read_fd)
        with patch.dict(os.environ, self.environment(), clear=True):
            completed = subprocess.run(
                [str(self.command), "_oauth", "accounts", "google", "--response-fd", str(write_fd)],
                pass_fds=(write_fd,), capture_output=True, text=True, check=False,
            )
        os.close(write_fd)
        self.assertEqual(1, completed.returncode)
        self.assertIn("not an open socket", completed.stderr)

    def gone(self, pid, patience=15.0):
        """Whether that process is really no longer running, waited for rather than assumed."""
        deadline = time.monotonic() + patience
        while time.monotonic() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return True
            except PermissionError:
                return False
            time.sleep(0.05)
        return False

    def orphans(self, where):
        """Every descendant the stand-in left behind, by pid."""
        if not where.exists():
            return []
        return [int(one) for one in where.read_text(encoding="utf-8").split()]

    def stop_orphans(self, where):
        """This suite owns the descendants it asked for, and never leaves one sleeping."""
        for pid in self.orphans(where):
            try:
                os.kill(pid, 9)
            except OSError:
                pass

    def test_a_descendant_holding_stderr_does_not_fail_a_finished_sign_in(self):
        """A successful sign-in leaves the person's browser open, holding the stderr it inherited.

        The pipe never reaches end-of-file, so the wait for it runs out — and that must not become
        a timeout, because nothing timed out: the child exited zero. Its descendants are not this
        command's to kill, and killing them would close the browser somebody just used.
        """
        where = self.home / "sign-in-orphans"
        self.plan["mode"] = "orphan-holds-stderr"
        self.plan["orphan"] = str(where)
        self.addCleanup(self.stop_orphans, where)
        started = time.monotonic()
        with patch.object(self.module, "SIGN_IN_SECONDS", 0.5), \
                patch.object(self.module, "BRIDGE_SECONDS", 0.5):
            code, out, err = self.invoke(["profiles", "--auth"])
        self.assertEqual(0, code, err)
        self.assertLess(time.monotonic() - started, 30)
        left = self.orphans(where)
        self.assertTrue(left, "the stand-in never spawned the descendant")
        # Still running, deliberately: this command does not reach into what it did not start.
        for pid in left:
            self.assertFalse(self.gone(pid, patience=0.1),
                             "a descendant of a successful sign-in was killed")
        self.no_child_is_left()

    def test_a_refusal_survives_a_descendant_that_keeps_the_pipe_open(self):
        """The child exited non-zero *and* left something holding stderr.

        The reason it wrote is already in the pipe; the helper is only keeping that pipe from
        closing afterwards. Losing it here would turn "Google login was declined" into the useless
        `rundesk exited 1`, on the one path where the person most needs to read what Google said.
        """
        where = self.home / "refusal-orphans"
        self.plan["mode"] = "refuse-with-orphan"
        self.plan["orphan"] = str(where)
        self.addCleanup(self.stop_orphans, where)
        started = time.monotonic()
        with patch.object(self.module, "SIGN_IN_SECONDS", 0.5), \
                patch.object(self.module, "BRIDGE_SECONDS", 0.5):
            code, _, err = self.invoke(["profiles", "--auth"])
        self.assertEqual(2, code)
        self.assertIn("Google login was declined", err)
        self.assertNotIn("rundesk exited", err)
        self.assertLess(time.monotonic() - started, 30)
        for pid in self.orphans(where):
            self.assertFalse(self.gone(pid, patience=0.1),
                             "a descendant of a child that answered was killed")
        self.no_child_is_left()

    def test_a_hung_sign_in_and_its_descendants_are_stopped_at_the_deadline(self):
        """The other half: the child itself is still running, so it really is out of time."""
        where = self.home / "hung-sign-in-orphans"
        self.plan["mode"] = "hang-with-orphan"
        self.plan["orphan"] = str(where)
        self.addCleanup(self.stop_orphans, where)
        started = time.monotonic()
        with patch.object(self.module, "SIGN_IN_SECONDS", 0.5):
            code, _, err = self.invoke(["profiles", "--auth"])
        self.assertEqual(2, code)
        self.assertIn("in time", err)
        self.assertLess(time.monotonic() - started, 30)
        left = self.orphans(where)
        self.assertTrue(left, "the stand-in never spawned the descendant")
        for pid in left:
            self.assertTrue(self.gone(pid), "a descendant of a hung child outlived the deadline")
        self.no_child_is_left()

    def test_a_descendant_holding_stderr_does_not_fail_a_finished_bridge_call(self):
        """The same distinction on the `_oauth` path, which no sign-in runs ahead of."""
        where = self.home / "bridge-orphans"
        self.plan["mode"] = "orphan-holds-stderr"
        self.plan["orphan"] = str(where)
        self.addCleanup(self.stop_orphans, where)
        started = time.monotonic()
        with patch.object(self.module, "BRIDGE_SECONDS", 0.5):
            code, _, err = self.invoke(["profiles"])
        self.assertEqual(0, code, err)
        self.assertLess(time.monotonic() - started, 30)
        self.assertEqual("_oauth", self.asked()[0][0])
        for pid in self.orphans(where):
            self.assertFalse(self.gone(pid, patience=0.1),
                             "a descendant of a successful bridge call was killed")
        self.no_child_is_left()

    def test_a_hung_bridge_call_and_its_descendants_are_stopped_at_the_deadline(self):
        where = self.home / "hung-bridge-orphans"
        self.plan["mode"] = "hang-with-orphan"
        self.plan["orphan"] = str(where)
        self.addCleanup(self.stop_orphans, where)
        started = time.monotonic()
        with patch.object(self.module, "BRIDGE_SECONDS", 0.5):
            code, _, err = self.invoke(["profiles"])
        self.assertEqual(2, code)
        self.assertIn("in time", err)
        self.assertLess(time.monotonic() - started, 30)
        left = self.orphans(where)
        self.assertTrue(left, "the stand-in never spawned the descendant")
        for pid in left:
            self.assertTrue(self.gone(pid), "a descendant of a hung child outlived the deadline")
        self.no_child_is_left()

    def no_child_is_left(self):
        """No child of this process survives the call, so nothing was killed without being reaped."""
        with self.assertRaises(ChildProcessError):
            os.waitpid(-1, os.WNOHANG)

    def test_a_child_that_never_answers_is_stopped_at_the_deadline(self):
        self.plan["mode"] = "hang"
        started = time.monotonic()
        with patch.object(self.module, "BRIDGE_SECONDS", 0.3):
            code, _, err = self.invoke(["sites"])
        self.assertEqual(2, code)
        self.assertIn("in time", err)
        # The stand-in would sleep for ten minutes, so this bounds the wait rather than the machine.
        self.assertLess(time.monotonic() - started, 30)
        self.no_child_is_left()

    def test_a_child_that_answers_and_then_hangs_is_still_stopped(self):
        self.plan["mode"] = "frame-then-hang"
        with patch.object(self.module, "BRIDGE_SECONDS", 0.3):
            code, _, err = self.invoke(["sites"])
        self.assertEqual(2, code)
        self.assertIn("in time", err)
        self.no_child_is_left()

    def test_a_sign_in_nobody_completes_is_stopped_at_its_own_deadline(self):
        self.plan["mode"] = "login-hang"
        with patch.object(self.module, "SIGN_IN_SECONDS", 0.3):
            code, _, err = self.invoke(["sites", "--auth"])
        self.assertEqual(2, code)
        self.assertIn("signing in to Google", err)
        self.assertEqual([], self.requests)
        self.no_child_is_left()

    def test_rundesk_answering_nothing_at_all_is_a_refusal_with_the_login_command(self):
        self.plan["mode"] = "silent"
        code, _, err = self.invoke(["sites"])
        self.assertEqual(2, code)
        self.assertIn("rundesk login google", err)

    # --- selecting an app profile and an account -----------------------------------------------

    def test_an_answer_for_another_account_than_email_asked_for_is_refused(self):
        """Checked here as well as inside Rundesk, because this command made the promise.

        A token for a different account would read somebody else's Google data out under the
        address the caller asked for, and every row would look right.
        """
        self.plan["accounts"] = {"ACME": ["one@example.test", "two@example.test"]}
        self.plan["mode"] = "other-identity"
        self.payloads = [self.sites_payload()]
        code, out, err = self.invoke(["sites", "--profile", "acme", "--email", "two@example.test"])
        self.assertEqual(2, code)
        self.assertIn("other than two@example.test", err)
        # Refused before the request, not after: nothing was asked of Google.
        self.assertEqual([], self.requests)
        self.assertEqual("", out)

    def test_the_same_address_in_another_case_is_the_same_account(self):
        self.plan["accounts"] = {"ACME": ["Two@Example.test"]}
        self.payloads = [self.sites_payload()]
        code, _, err = self.invoke(["sites", "--profile", "acme", "--email", "two@example.test"])
        self.assertEqual(0, code, err)

    def test_profile_and_email_are_forwarded_to_rundesk_unchanged(self):
        self.plan["accounts"] = {"ACME": ["one@example.test", "two@example.test"]}
        self.payloads = [self.sites_payload()]
        code, _, err = self.invoke(["sites", "--profile", "acme", "--email", "two@example.test"])
        self.assertEqual(0, code, err)
        self.assertEqual(
            ["_oauth", "access", "google", "search-console", "--profile", "acme",
             "--email", "two@example.test"],
            self.asked()[0][:8],
        )
        self.assertEqual(["Bearer access-token-for-two@example.test"], self.authorization())

    def test_several_accounts_under_one_app_profile_need_an_explicit_email(self):
        self.plan["accounts"] = {"ACME": ["one@example.test", "two@example.test"]}
        code, _, err = self.invoke(["sites", "--profile", "acme"])
        self.assertEqual(2, code)
        self.assertIn("choose --email from: one@example.test, two@example.test", err)
        self.assertIn("rundesk login google --profile acme", err)

    def test_profiles_lists_every_signed_in_account_without_a_network_call(self):
        self.plan["accounts"] = {"DEFAULT": ["one@example.test", "two@example.test"]}
        code, out, err = self.invoke(["profiles"])
        self.assertEqual(0, code, err)
        self.assertIn("default,one@example.test,ready", out)
        self.assertIn("default,two@example.test,ready", out)
        self.assertEqual(["_oauth", "accounts", "google", "--response-fd"], self.asked()[0][:4])
        self.assertEqual([], self.requests)

    def test_profiles_says_what_to_run_when_no_account_is_connected(self):
        self.plan["accounts"] = {"DEFAULT": []}
        code, out, _ = self.invoke(["profiles"])
        self.assertEqual(0, code)
        self.assertIn("run: rundesk login google", out)

    def test_profiles_shows_an_unconfigured_app_profile_and_still_fails(self):
        """A listing that could not be made is not an empty listing, and must not exit like one."""
        code, out, _ = self.invoke(["profiles", "--profile", "missing"])
        self.assertEqual(2, code)
        self.assertIn("GOOGLE_OAUTH_CLIENT_ID", out)

    # --- recovery and the auth shortcut --------------------------------------------------------

    def test_a_missing_scope_names_the_exact_login_command_for_that_app_profile(self):
        self.plan["mode"] = "scope"
        self.plan["accounts"] = {"ACME": ["one@example.test"]}
        code, _, err = self.invoke(["sites", "--profile", "acme"])
        self.assertEqual(2, code)
        self.assertIn("did not return a reusable grant for every requested scope", err)
        self.assertIn("Run: rundesk login google --profile acme", err)

    def test_auth_signs_in_first_and_forwards_the_app_profile(self):
        self.plan["accounts"] = {"ACME": ["one@example.test"]}
        self.payloads = [self.sites_payload()]
        code, _, err = self.invoke(["sites", "--auth", "--profile", "acme"])
        self.assertEqual(0, code, err)
        asked = self.asked()
        self.assertEqual(["login", "google", "--profile", "acme"], asked[0])
        self.assertEqual(["access", "google"], asked[1][1:3])

    def test_auth_without_a_profile_asks_rundesk_for_its_own_default(self):
        code, out, err = self.invoke(["profiles", "--auth"])
        self.assertEqual(0, code, err)
        self.assertEqual(["login", "google"], self.asked()[0])

    def test_a_declined_sign_in_stops_before_google_is_touched(self):
        self.plan["mode"] = "login-refused"
        code, _, err = self.invoke(["sites", "--auth"])
        self.assertEqual(2, code)
        self.assertIn("Google login was declined", err)
        self.assertEqual([], self.requests)

    def test_a_token_that_is_not_bearer_is_refused_rather_than_sent(self):
        self.plan["mode"] = "wrong-token-type"
        code, _, err = self.invoke(["sites"])
        self.assertEqual(2, code)
        self.assertIn("cannot send", err)
        self.assertEqual([], self.requests)

    def test_a_grant_without_a_subject_is_refused(self):
        self.plan["mode"] = "no-subject"
        code, _, err = self.invoke(["sites"])
        self.assertEqual(2, code)
        self.assertIn("no usable Google access token", err)
        self.assertEqual([], self.requests)

    def test_a_framed_refusal_is_read_from_the_socket_rather_than_from_stderr(self):
        self.plan["accounts"] = {"ACME": []}
        code, _, err = self.invoke(["sites", "--profile", "acme"])
        self.assertEqual(2, code)
        # Rundesk frames the reason and also says it; the framed one is what this package reports.
        self.assertIn("no matching Google profile is connected", err)
        self.assertNotIn("oauth: FAILED", err)
        self.assertIn("rundesk login google --profile acme", err)

    def test_an_unknown_provider_or_capability_is_reported_as_rundesk_framed_it(self):
        with patch.object(self.module, "PROVIDER", "nowhere"):
            code, _, err = self.invoke(["sites"])
        self.assertEqual(2, code)
        self.assertIn("no installed OAuth provider called 'nowhere'", err)

    def test_an_expired_token_is_refused_rather_than_sent_to_google(self):
        self.plan["mode"] = "expired"
        code, _, err = self.invoke(["sites"])
        self.assertEqual(2, code)
        self.assertIn("expired", err)
        self.assertEqual([], self.requests)

    # --- an older Rundesk ----------------------------------------------------------------------

    def test_a_rundesk_without_the_bridge_says_to_update_and_sign_in(self):
        self.plan["mode"] = "old"
        code, _, err = self.invoke(["sites"])
        self.assertEqual(2, code)
        self.assertIn("older than Rundesk-managed Google sign-in", err)
        self.assertIn("rundesk login google", err)

    def test_no_rundesk_at_all_is_reported_as_the_missing_install_it_is(self):
        # An empty PATH as well, so the case cannot reach whatever install runs it.
        code, _, err = self.invoke(["sites"], RUNDESK_COMMAND="", PATH=str(self.home / "none"))
        self.assertEqual(2, code)
        self.assertIn("no Rundesk is reachable", err)
        self.assertIn("rundesk login google", err)

    # --- the token never leaves this process ---------------------------------------------------

    def test_the_token_reaches_no_argument_variable_or_stream(self):
        self.payloads = [self.sites_payload()]
        with patch.dict(os.environ, self.environment(), clear=True), patch.object(
            self.module, "open_url", self.opener
        ), redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            code = self.module.main(["sites"])
            leaked = [name for name, value in os.environ.items() if MANAGED_TOKEN in value]
        self.assertEqual(0, code, err.getvalue())
        self.assertEqual([], leaked)
        self.assertNotIn(MANAGED_TOKEN, out.getvalue())
        self.assertNotIn(MANAGED_TOKEN, err.getvalue())
        self.assertNotIn(MANAGED_TOKEN, self.record.read_text(encoding="utf-8"))
        self.assertNotIn(MANAGED_TOKEN, str(self.module.Access("", "")))


class SafeErrorTest(unittest.TestCase):
    """Google refuses in two shapes, and both have to reach the person who has to act on one."""

    def setUp(self):
        self.module = load_module()

    def refusal(self, body, code=400):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        return urllib.error.HTTPError("https://example.test/x", code, "Bad Request", {},
                                      io.BytesIO(raw))

    def test_an_oauth_refusal_names_its_reason_rather_than_its_status(self):
        """The inherited defect: `error` is a *string* here, and reaching for `.message` raised.

        Swallowed, that reported `HTTP 400` for a revoked grant — true, and not the sentence that
        tells somebody to sign in again.
        """
        self.assertEqual(
            "Token has been expired or revoked.",
            self.module.safe_error(self.refusal(
                {"error": "invalid_grant",
                 "error_description": "Token has been expired or revoked."})))
        self.assertEqual("invalid_grant",
                         self.module.safe_error(self.refusal({"error": "invalid_grant"})))

    def test_an_api_refusal_still_names_its_message(self):
        self.assertEqual("Request had insufficient authentication scopes.",
                         self.module.safe_error(self.refusal(
                             {"error": {"code": 403, "message":
                                        "Request had insufficient authentication scopes."}})))

    def test_anything_unrecognisable_falls_back_to_the_status(self):
        for body in (b"not json", b"[1, 2]", b"", b'{"error": {}}', b'{"error": ""}',
                     b'{"error": {"message": "   "}}', b'{"nothing": true}'):
            with self.subTest(body=body):
                self.assertEqual("HTTP 400", self.module.safe_error(self.refusal(body)))

    def test_an_oversized_refusal_body_is_bounded(self):
        huge = b'{"error": "' + b"x" * (self.module.MAX_ERROR_BODY * 2) + b'"}'
        # Bounded reads cannot complete the JSON, so this falls back rather than allocating it all.
        self.assertEqual("HTTP 400", self.module.safe_error(self.refusal(huge)))

    def test_the_body_is_read_once_and_closed(self):
        failure = self.refusal({"error": "invalid_grant"})
        self.assertEqual("invalid_grant", self.module.safe_error(failure))
        # Read a second time, an `HTTPError` is closed or empty — either way a caller that re-read
        # it would silently lose the reason, which is why this reads it exactly once.
        try:
            again = failure.read()
        except ValueError:
            again = b""
        self.assertEqual(b"", again)


if __name__ == "__main__":
    unittest.main()
