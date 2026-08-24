#!/usr/bin/env python3
"""Offline tests for google-pagespeed-insights."""

from __future__ import annotations

import importlib.util
import io
import json
import math
import os
import socket
import subprocess
import sys
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "google-pagespeed-insights.py"
LAUNCHER = HERE.parent / "google-pagespeed-insights"


def load_module():
    spec = importlib.util.spec_from_file_location("google_pagespeed_insights_module", SCRIPT)
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


NAN = float("nan")
INFINITY = float("inf")


def lighthouse(categories=None, audits=None, **extra):
    result = {"categories": categories if categories is not None else {}, "audits": audits if audits is not None else {}}
    result.update(extra)
    return {"lighthouseResult": result}


LEGACY_COLUMNS = ("row_type,category,metric,audit,title,score,value,numeric_value,display_value,"
                  "weight,requested_url,final_url,strategy,fetch_time,lighthouse_version,profile")


def field_experience(**overrides):
    """A CrUX scope shaped like the documented response: percentile, category, and open-ended tail."""
    experience = {
        "id": "https://www.example.test/",
        "metrics": {
            # Deliberately not in the documented order, so row order proves it is imposed here.
            "INTERACTION_TO_NEXT_PAINT": {"percentile": 180, "category": "FAST", "distributions": [
                {"min": 0, "max": 200, "proportion": 0.88},
                {"min": 200, "max": 500, "proportion": 0.09},
                {"min": 500, "proportion": 0.03},
            ]},
            # A raw CrUX integer, not a Lighthouse CLS ratio.
            "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 10, "category": "FAST", "distributions": []},
            "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400, "category": "AVERAGE", "distributions": [
                {"min": 0, "max": 2500, "proportion": 0.7231},
                {"min": 2500, "max": 4000, "proportion": 0.19},
                {"min": 4000, "proportion": 0.0869},
            ]},
        },
        "overall_category": "AVERAGE",
        # origin_fallback is deliberately absent: Google omits the field unless it is true, so the
        # common shape must be the one the fixtures exercise by default.
    }
    experience.update(overrides)
    return experience


def with_field_data(url=None, origin=None, **lighthouse_extra):
    payload = lighthouse(
        categories={"performance": {"score": 0.5, "auditRefs": []}},
        audits={}, **lighthouse_extra,
    )
    if url is not None:
        payload["loadingExperience"] = url
    if origin is not None:
        payload["originLoadingExperience"] = origin
    return payload


def analyze_args(**overrides):
    # field_data mirrors the real default so a test must opt in exactly as a caller would.
    defaults = dict(profile="example", url="https://example.test/", strategy="mobile",
                    category=["performance"], audit_limit=10, json=True, field_data="none",
                    field_limit=100)
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


GOLDEN_PAYLOAD = {
    "loadingExperience": {
        "id": "https://www.example.test/",
        "metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400, "category": "AVERAGE",
                                                    "distributions": [
                                                        {"min": 0, "max": 2500, "proportion": 0.7231},
                                                        {"min": 2500, "max": 4000, "proportion": 0.19},
                                                        {"min": 4000, "proportion": 0.0869}]}},
        "overall_category": "AVERAGE"},
    "originLoadingExperience": {
        "id": "https://www.example.test",
        "metrics": {"CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 10, "category": "AVERAGE"}},
        "overall_category": "SLOW"},
    "lighthouseResult": {
        "requestedUrl": "https://example.test/", "finalUrl": "https://www.example.test/",
        "fetchTime": "2026-08-18T12:00:00Z", "lighthouseVersion": "13.0.0",
        "categories": {"performance": {"score": 0.82, "auditRefs": [
            {"id": "render-blocking-resources", "weight": 5}]}},
        "audits": {"largest-contentful-paint": {"numericValue": 2600, "displayValue": "2.6 s"},
                   "render-blocking-resources": {"score": 0.2,
                                                 "title": "Eliminate render-blocking resources"}}},
}
CONTEXT = ("https://example.test/,https://www.example.test/,mobile,2026-08-18T12:00:00Z,13.0.0,"
           "example")
# The exact bytes a caller written before field data existed received for GOLDEN_PAYLOAD.
GOLDEN_CSV = "\n".join((
    LEGACY_COLUMNS,
    f"summary,performance,,,,82,,,,,{CONTEXT}",
    f"metric,,largest_contentful_paint,,,,2.6 s,2600,,,{CONTEXT}",
    f"audit,,,render-blocking-resources,Eliminate render-blocking resources,20,,,,5,{CONTEXT}",
)) + "\n"
GOLDEN_CONTEXT = {"requested_url": "https://example.test/", "final_url": "https://www.example.test/",
                  "strategy": "mobile", "fetch_time": "2026-08-18T12:00:00Z",
                  "lighthouse_version": "13.0.0", "profile": "example"}
GOLDEN_JSON = [
    {**GOLDEN_CONTEXT, "row_type": "summary", "category": "performance", "score": 82},
    {**GOLDEN_CONTEXT, "row_type": "metric", "metric": "largest_contentful_paint",
     "value": "2.6 s", "numeric_value": 2600},
    {**GOLDEN_CONTEXT, "row_type": "audit", "audit": "render-blocking-resources",
     "title": "Eliminate render-blocking resources", "score": 20, "display_value": "", "weight": 5},
]


class PageSpeedTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.env = {
            "GOOGLE_PAGESPEED_INSIGHTS_API_KEY__EXAMPLE": "secret-key",
            "GOOGLE_PAGESPEED_INSIGHTS_LABEL__EXAMPLE": "Example PageSpeed",
        }
        self.profile = self.module.Profile("example", "secret-key", "Example PageSpeed")

    def analyze(self, payload, **overrides):
        args = analyze_args(**overrides)
        with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
            self.module, "request_json", return_value=payload
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            self.module.cmd_analyze(args)
        return output.getvalue(), error.getvalue()

    def field_of(self, payload, **overrides):
        emitted, error = self.analyze(payload, **overrides)
        rows = json.loads(emitted)
        return [row for row in rows if row["row_type"].startswith("field_")], error

    def run_main(self, argv, payload):
        """Drive the real entry point so exit status and staged output are what a caller sees."""
        with patch.dict(os.environ, self.env, clear=True), patch.object(
            self.module, "request_json", return_value=payload
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            code = self.module.main(argv)
        return code, output.getvalue(), error.getvalue()

    def assertFieldRefused(self, extra, expected, field_data="distributions"):
        """A refused optional section is reported and costs the exit status, never the lab rows."""
        payload = with_field_data()
        payload.update(extra)
        with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
            self.module, "request_json", return_value=payload
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            code = self.module.cmd_analyze(analyze_args(field_data=field_data))
        self.assertEqual(2, code)
        self.assertRegex(error.getvalue(), expected)
        self.assertTrue(error.getvalue().startswith("ERROR: "), error.getvalue())
        rows = json.loads(output.getvalue())
        self.assertEqual([50], [row["score"] for row in rows if row["row_type"] == "summary"])
        self.assertEqual([], [row for row in rows if row["row_type"].startswith("field_")])
        return output.getvalue(), error.getvalue()

    def test_profiles_discovers_named_profile_without_network(self):
        with patch.dict(os.environ, self.env, clear=True), patch.object(
            self.module.urllib.request, "urlopen", side_effect=AssertionError("network")
        ), redirect_stdout(io.StringIO()) as output:
            code = self.module.main(["profiles"])
        self.assertEqual(code, 0)
        self.assertIn("example,Example PageSpeed,ready", output.getvalue())

    def test_named_profile_never_falls_back_to_plain_key(self):
        env = {"GOOGLE_PAGESPEED_INSIGHTS_API_KEY": "plain", "GOOGLE_PAGESPEED_INSIGHTS_PROFILES": "example"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(self.module.PageSpeedError) as raised:
                self.module.get_profile("example")
        self.assertIn("API_KEY__EXAMPLE", str(raised.exception))
        self.assertNotIn("plain", str(raised.exception))

    def test_api_key_is_not_in_profile_representation(self):
        self.assertNotIn("secret-key", repr(self.profile))

    def test_request_encodes_parameters_and_does_not_expose_key_on_error(self):
        requests = []

        def opener(request, timeout):
            requests.append(request)
            return Response({"lighthouseResult": {}})

        self.module.request_json([("url", "https://example.test/a b"), ("key", "secret-key")], opener)
        self.assertIn("url=https%3A%2F%2Fexample.test%2Fa+b", requests[0].full_url)
        error = urllib.error.HTTPError(
            "https://example", 403, "Forbidden", {},
            io.BytesIO(json.dumps({"error": {"message": "API disabled for secret-key"}}).encode()),
        )
        with self.assertRaises(self.module.PageSpeedError) as raised:
            self.module.request_json(
                [("key", "secret-key")],
                opener=lambda *args, **kwargs: (_ for _ in ()).throw(error),
            )
        self.assertIn("API disabled", str(raised.exception))
        self.assertIn("[REDACTED]", str(raised.exception))
        self.assertNotIn("secret-key", str(raised.exception))

    def test_analyze_normalizes_scores_metrics_and_bounded_audits(self):
        args = analyze_args(category=["performance", "seo"], audit_limit=1)
        payload = {"lighthouseResult": {
            "requestedUrl": args.url, "finalUrl": "https://www.example.test/", "fetchTime": "2026-08-17T12:00:00Z", "lighthouseVersion": "13.0.0",
            "categories": {
                "performance": {"score": 0.82, "auditRefs": [{"id": "render-blocking-resources", "weight": 5}, {"id": "uses-long-cache-ttl", "weight": 1}]},
                "seo": {"score": 0.95, "auditRefs": []},
            },
            "audits": {
                "largest-contentful-paint": {"score": 0.8, "numericValue": 2400, "displayValue": "2.4 s", "title": "Largest Contentful Paint"},
                "render-blocking-resources": {"score": 0.2, "title": "Eliminate render-blocking resources", "displayValue": "1.2 s"},
                "uses-long-cache-ttl": {"score": 0.4, "title": "Use efficient cache lifetimes"},
            },
        }}
        with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
            self.module, "request_json", return_value=payload
        ) as request, redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            self.module.cmd_analyze(args)
        params = request.call_args.args[0]
        self.assertEqual([value for key, value in params if key == "category"], ["PERFORMANCE", "SEO"])
        self.assertIn(("strategy", "MOBILE"), params)
        self.assertIn(("key", "secret-key"), params)
        rows = json.loads(output.getvalue())
        self.assertEqual([82, 95], [row["score"] for row in rows if row["row_type"] == "summary"])
        self.assertEqual("2.4 s", next(row["value"] for row in rows if row.get("metric") == "largest_contentful_paint"))
        findings = [row for row in rows if row["row_type"] == "audit"]
        self.assertEqual("render-blocking-resources", findings[0]["audit"])
        self.assertIn("truncated", error.getvalue())
        self.assertNotIn("secret-key", output.getvalue() + error.getvalue())

    def test_empty_lighthouse_result_is_refused(self):
        args = analyze_args(category=None)
        with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(self.module, "request_json", return_value={}):
            with self.assertRaisesRegex(self.module.PageSpeedError, "no Lighthouse result"):
                self.module.cmd_analyze(args)

    def test_url_validation_rejects_credentials_and_non_http_schemes(self):
        self.assertEqual("https://example.test/", self.module.valid_url("https://example.test/"))
        with self.assertRaises(Exception):
            self.module.valid_url("file:///tmp/page.html")
        with self.assertRaises(Exception):
            self.module.valid_url("https://user:pass@example.test/")

    def test_main_rejects_unbounded_audit_limit_before_network(self):
        with patch.dict(os.environ, self.env, clear=True), redirect_stderr(io.StringIO()) as error:
            code = self.module.main(["analyze", "--profile", "example", "--url", "https://example.test/", "--audit-limit", "51"])
        self.assertEqual(2, code)
        self.assertIn("between 0 and 50", error.getvalue())

    def test_request_uses_the_official_uppercase_discovery_enums(self):
        # https://pagespeedonline.googleapis.com/$discovery/rest?version=v5 defines the query enums
        # as MOBILE/DESKTOP and PERFORMANCE/ACCESSIBILITY/BEST_PRACTICES/SEO.
        self.assertEqual({"mobile": "MOBILE", "desktop": "DESKTOP"}, self.module.STRATEGIES)
        self.assertEqual(
            {"performance": "PERFORMANCE", "accessibility": "ACCESSIBILITY",
             "best-practices": "BEST_PRACTICES", "seo": "SEO"},
            self.module.CATEGORIES,
        )
        for strategy, expected in self.module.STRATEGIES.items():
            with self.subTest(strategy=strategy):
                args = analyze_args(strategy=strategy, category=list(self.module.CATEGORIES),
                                    field_data="summary")
                with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
                    self.module, "request_json", return_value=lighthouse()
                ) as request, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.module.cmd_analyze(args)
                self.assertEqual(
                    [("url", "https://example.test/"), ("strategy", expected),
                     ("category", "PERFORMANCE"), ("category", "ACCESSIBILITY"),
                     ("category", "BEST_PRACTICES"), ("category", "SEO"),
                     ("key", "secret-key")],
                    request.call_args.args[0],
                )

    def test_lowercase_choices_stay_user_facing(self):
        parsed = self.module.parser().parse_args(
            ["analyze", "--url", "https://example.test/", "--strategy", "desktop", "--category", "best-practices"]
        )
        self.assertEqual("desktop", parsed.strategy)
        self.assertEqual(["best-practices"], parsed.category)
        args = analyze_args(strategy="desktop", category=["best-practices"])
        with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
            self.module, "request_json",
            return_value=lighthouse(categories={"best-practices": {"score": 0.5, "auditRefs": []}}),
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
            self.module.cmd_analyze(args)
        row = json.loads(output.getvalue())[0]
        self.assertEqual("best-practices", row["category"])
        self.assertEqual("desktop", row["strategy"])

    def test_hostile_response_shapes_are_refused(self):
        cases = (
            ({"lighthouseResult": None}, "malformed Lighthouse result"),
            ({"lighthouseResult": []}, "malformed Lighthouse result"),
            ({"lighthouseResult": "x"}, "malformed Lighthouse result"),
            ({}, "no Lighthouse result"),
            (lighthouse(runtimeError=[]), "malformed Lighthouse runtime error"),
            (lighthouse(runtimeError={"code": 7}), "malformed Lighthouse runtime error code"),
            (lighthouse(runtimeError={"message": []}), "malformed Lighthouse runtime error message"),
            ({"lighthouseResult": {"categories": None}}, "malformed Lighthouse categories object"),
            ({"lighthouseResult": {"categories": []}}, "malformed Lighthouse categories object"),
            ({"lighthouseResult": {"audits": None}}, "malformed Lighthouse audits object"),
            ({"lighthouseResult": {"audits": []}}, "malformed Lighthouse audits object"),
            (lighthouse(categories={"performance": None}), "malformed performance category object"),
            (lighthouse(categories={"performance": "x"}), "malformed performance category object"),
            (lighthouse(categories={"performance": {"auditRefs": None}}), "malformed performance audit reference collection"),
            (lighthouse(categories={"performance": {"auditRefs": "x"}}), "malformed performance audit reference collection"),
            (lighthouse(categories={"performance": {"auditRefs": ["x"]}}), "malformed performance audit reference"),
            (lighthouse(categories={"performance": {"auditRefs": [None]}}), "malformed performance audit reference"),
            (lighthouse(categories={"performance": {"auditRefs": [{"id": 7, "weight": 1}]}}), "malformed performance audit reference id"),
            (lighthouse(categories={"performance": {"auditRefs": [{"id": "a", "weight": "heavy"}]}}), "malformed performance audit reference weight"),
            (lighthouse(audits={"a": None}), "malformed a audit object"),
            (lighthouse(audits={"a": "x"}), "malformed a audit object"),
            (lighthouse(audits={"a": {"score": "low"}}), "malformed a audit score"),
            (lighthouse(audits={"a": {"score": 0.1, "title": 7}}), "malformed a audit title"),
            (lighthouse(audits={"largest-contentful-paint": {"numericValue": "fast"}}), "malformed largest-contentful-paint audit numeric value"),
            (lighthouse(categories={"performance": {"score": "great"}}), "malformed performance category score"),
            (lighthouse(requestedUrl=7), "malformed requested URL"),
            (lighthouse(finalUrl=[]), "malformed final URL"),
            (lighthouse(fetchTime=7), "malformed fetch time"),
            (lighthouse(lighthouseVersion={}), "malformed Lighthouse version"),
        )
        for payload, expected in cases:
            with self.subTest(expected=expected, payload=payload):
                args = analyze_args()
                with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
                    self.module, "request_json", return_value=payload
                ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    with self.assertRaisesRegex(self.module.PageSpeedError, expected):
                        self.module.cmd_analyze(args)

    def test_lighthouse_runtime_error_exits_two_without_success_output(self):
        payload = lighthouse(runtimeError={
            "code": "ERRORED_DOCUMENT_REQUEST",
            "message": "Lighthouse was unable to reliably load the page.",
        })
        with patch.dict(os.environ, self.env, clear=True), patch.object(
            self.module, "request_json", return_value=payload
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            code = self.module.main(["analyze", "--profile", "example", "--url", "https://example.test/"])
        self.assertEqual(2, code)
        self.assertEqual("", output.getvalue())
        self.assertIn("ERRORED_DOCUMENT_REQUEST", error.getvalue())
        self.assertIn("unable to reliably load", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())

    def test_non_finite_values_are_refused_before_rounding_or_emission(self):
        cases = (
            (lighthouse(categories={"performance": {"score": NAN}}), "non-finite performance category score"),
            (lighthouse(categories={"performance": {"score": INFINITY}}), "non-finite performance category score"),
            (lighthouse(categories={"performance": {"score": -INFINITY}}), "non-finite performance category score"),
            (lighthouse(audits={"a": {"score": NAN}}), "non-finite a audit score"),
            (lighthouse(audits={"a": {"score": -INFINITY}}), "non-finite a audit score"),
            (lighthouse(categories={"performance": {"auditRefs": [{"id": "a", "weight": NAN}]}}), "non-finite performance audit reference weight"),
            (lighthouse(categories={"performance": {"auditRefs": [{"id": "a", "weight": INFINITY}]}}), "non-finite performance audit reference weight"),
            (lighthouse(audits={"largest-contentful-paint": {"numericValue": NAN}}), "non-finite largest-contentful-paint audit numeric value"),
            (lighthouse(audits={"largest-contentful-paint": {"numericValue": INFINITY}}), "non-finite largest-contentful-paint audit numeric value"),
        )
        for payload, expected in cases:
            with self.subTest(expected=expected):
                args = analyze_args()
                with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
                    self.module, "request_json", return_value=payload
                ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    with self.assertRaisesRegex(self.module.PageSpeedError, expected):
                        self.module.cmd_analyze(args)

    def test_non_finite_json_literals_are_refused_at_parse_time(self):
        for body in (b'{"lighthouseResult": {"categories": {"performance": {"score": NaN}}}}',
                     b'{"lighthouseResult": {"categories": {"performance": {"score": Infinity}}}}',
                     b'{"lighthouseResult": {"categories": {"performance": {"score": -Infinity}}}}'):
            with self.subTest(body=body):
                with self.assertRaisesRegex(self.module.PageSpeedError, "non-finite JSON value"):
                    self.module.request_json([("key", "secret-key")], opener=lambda *a, **k: RawResponse(body))

    def test_json_output_is_standards_safe(self):
        with self.assertRaisesRegex(self.module.PageSpeedError, "non-finite value as JSON"):
            with redirect_stdout(io.StringIO()):
                self.module.write_rows([{"score": NAN}], ["score"], True)
        args = analyze_args()
        payload = lighthouse(
            categories={"performance": {"score": 0.5, "auditRefs": [{"id": "a", "weight": 3}]}},
            audits={"a": {"score": 0.25, "title": "Fix a"},
                    "largest-contentful-paint": {"numericValue": 2400.5, "displayValue": "2.4 s"}},
        )
        with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
            self.module, "request_json", return_value=payload
        ), redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()):
            self.module.cmd_analyze(args)
        emitted = output.getvalue()
        self.assertNotIn("NaN", emitted)
        self.assertNotIn("Infinity", emitted)
        for row in json.loads(emitted):
            for value in row.values():
                if isinstance(value, float):
                    self.assertTrue(math.isfinite(value))

    def test_malformed_response_exits_two_without_a_traceback(self):
        for payload in (lighthouse(categories={"performance": {"auditRefs": None}}),
                        lighthouse(categories={"performance": {"score": NAN}}),
                        {"lighthouseResult": None}):
            with self.subTest(payload=payload):
                with patch.dict(os.environ, self.env, clear=True), patch.object(
                    self.module, "request_json", return_value=payload
                ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as error:
                    code = self.module.main(["analyze", "--profile", "example", "--url", "https://example.test/"])
                self.assertEqual(2, code)
                self.assertTrue(error.getvalue().startswith("ERROR: "), error.getvalue())
                self.assertNotIn("Traceback", error.getvalue())

    def test_request_json_resolves_the_opener_at_call_time_without_touching_the_network(self):
        def refuse(*args, **kwargs):
            raise AssertionError("a real network connection was attempted")

        calls = []

        def fake_open_url(request, timeout=60):
            calls.append(request)
            return Response({"lighthouseResult": {"categories": {}, "audits": {}}})

        with patch.object(socket.socket, "connect", refuse), patch.object(
            socket, "create_connection", refuse
        ), patch.object(socket, "getaddrinfo", refuse), patch.object(
            self.module, "open_url", fake_open_url
        ):
            # No opener argument: a def-time default would bypass the patch and hit the guards above.
            result = self.module.request_json([("url", "https://example.test/"), ("key", "secret-key")])
        self.assertEqual({"lighthouseResult": {"categories": {}, "audits": {}}}, result)
        self.assertEqual(1, len(calls))
        self.assertIn("key=secret-key", calls[0].full_url)

    def test_default_invocation_emits_byte_for_byte_legacy_csv(self):
        # A caller written before field data existed must see exactly the output it saw then, even
        # though this response carries field data.
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/"], GOLDEN_PAYLOAD)
        self.assertEqual(0, code)
        self.assertEqual(GOLDEN_CSV, emitted)
        self.assertEqual("", error)

    def test_default_invocation_emits_the_legacy_json_row_set(self):
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/", "--json"],
            GOLDEN_PAYLOAD)
        self.assertEqual(0, code)
        self.assertEqual(GOLDEN_JSON, json.loads(emitted))
        self.assertEqual("", error)
        emitted_keys = {key for row in json.loads(emitted) for key in row}
        self.assertEqual(set(), emitted_keys & set(self.module.FIELD_COLUMNS))
        self.assertEqual(set(), emitted_keys & set(self.module.DISTRIBUTION_COLUMNS))

    def test_field_data_defaults_to_none_without_changing_the_request(self):
        parsed = self.module.parser().parse_args(["analyze", "--url", "https://example.test/"])
        self.assertEqual("none", parsed.field_data)
        args = analyze_args()
        with patch.object(self.module, "selected_profile", return_value=self.profile), patch.object(
            self.module, "request_json", return_value=GOLDEN_PAYLOAD
        ) as request, redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as error:
            self.assertEqual(0, self.module.cmd_analyze(args))
        self.assertEqual([("url", "https://example.test/"), ("strategy", "MOBILE"),
                          ("category", "PERFORMANCE"), ("key", "secret-key")],
                         request.call_args.args[0])
        self.assertNotIn("secret-key", output.getvalue() + error.getvalue())

    def test_field_data_reports_page_and_origin_scopes_separately(self):
        payload = with_field_data(
            url=field_experience(),
            origin=field_experience(
                id="https://www.example.test",
                metrics={"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 3100, "category": "SLOW"}},
                overall_category="SLOW",
            ),
        )
        rows, error = self.field_of(payload, field_data="summary")
        summaries = [row for row in rows if row["row_type"] == "field_summary"]
        self.assertEqual([("url", "url"), ("origin", "origin")],
                         [(row["requested_scope"], row["effective_scope"]) for row in summaries])
        self.assertEqual(["https://www.example.test/", "https://www.example.test"],
                         [row["field_id"] for row in summaries])
        self.assertEqual(["AVERAGE", "SLOW"], [row["field_category"] for row in summaries])
        # Neither object reported the flag, and neither reading is a fallback.
        self.assertEqual(["false", "false"], [row["origin_fallback"] for row in summaries])
        page = [row for row in rows
                if row["row_type"] == "field_metric" and row["requested_scope"] == "url"]
        self.assertEqual(["largest_contentful_paint", "cumulative_layout_shift_score_raw",
                          "interaction_to_next_paint"], [row["metric"] for row in page])
        self.assertEqual([2400, 10, 180], [row["percentile"] for row in page])
        self.assertEqual(["AVERAGE", "FAST", "FAST"], [row["field_category"] for row in page])
        self.assertEqual([], [row for row in rows if row["row_type"] == "field_distribution"])
        self.assertNotIn("NOTE:", error)

    def test_origin_fallback_is_reported_as_an_origin_effective_scope(self):
        # https://developers.google.com/speed/docs/insights/v5/about: a page with too few samples is
        # answered with origin-level experiences.
        payload = with_field_data(url=field_experience(id="https://www.example.test",
                                                       origin_fallback=True))
        rows, _ = self.field_of(payload, field_data="distributions")
        self.assertEqual({"url"}, {row["requested_scope"] for row in rows})
        self.assertEqual({"origin"}, {row["effective_scope"] for row in rows})
        self.assertEqual({"true"}, {row["origin_fallback"] for row in rows})
        self.assertEqual({"field_summary", "field_metric", "field_distribution"},
                         {row["row_type"] for row in rows})

    def test_absent_origin_fallback_reads_as_a_page_level_reading(self):
        """Google omits origin_fallback in the common case; absent must mean "not a fallback"."""
        payload = with_field_data(url=field_experience(), origin=field_experience(
            id="https://www.example.test", overall_category="SLOW"))
        self.assertNotIn("origin_fallback", payload["loadingExperience"])
        self.assertNotIn("origin_fallback", payload["originLoadingExperience"])
        rows, _ = self.field_of(payload, field_data="summary")
        self.assertTrue(rows)
        self.assertEqual({"false"}, {row["origin_fallback"] for row in rows})
        page = [row for row in rows if row["requested_scope"] == "url"]
        self.assertTrue(page)
        # An absent flag must not quietly reattribute the page's data to the whole origin.
        self.assertEqual({"url"}, {row["effective_scope"] for row in page})

    def test_absent_and_explicit_false_origin_fallback_are_reported_alike(self):
        absent, _ = self.field_of(with_field_data(url=field_experience()), field_data="summary")
        explicit, _ = self.field_of(
            with_field_data(url=field_experience(origin_fallback=False)), field_data="summary")
        # Both mean the same thing, so one spelling reaches the reader.
        self.assertEqual(absent, explicit)
        self.assertEqual({"false"}, {row["origin_fallback"] for row in absent})

    def test_absent_origin_fallback_stays_distinguishable_from_a_malformed_one(self):
        # Absent is a value the parser returns; malformed is a response the parser refuses.
        self.assertIsNone(self.module.optional_flag({}, "origin_fallback", "url field origin fallback"))
        self.assertIs(False, self.module.optional_flag(
            {"origin_fallback": False}, "origin_fallback", "url field origin fallback"))
        self.assertIs(True, self.module.optional_flag(
            {"origin_fallback": True}, "origin_fallback", "url field origin fallback"))
        for value in ("true", 1, 0, [], {}):
            with self.subTest(value=value):
                with self.assertRaisesRegex(self.module.PageSpeedError, "malformed url field origin fallback"):
                    self.module.optional_flag({"origin_fallback": value}, "origin_fallback",
                                              "url field origin fallback")
        self.assertEqual(("false", "false", "true"),
                         tuple(self.module.fallback_text(value) for value in (None, False, True)))

    def test_an_explicit_null_origin_fallback_is_malformed_rather_than_absent(self):
        """Google omits the field; a literal null is a payload that answered, badly.

        Read as absent, this reports a confident `false` — the reading nobody would think to
        question — from a response that never actually said so.
        """
        with self.assertRaisesRegex(self.module.PageSpeedError,
                                    "malformed url field origin fallback"):
            self.module.optional_flag({"origin_fallback": None}, "origin_fallback",
                                      "url field origin fallback")
        # Absent stays absent: the key not being there is still the ordinary case.
        self.assertIsNone(self.module.optional_flag({"other": 1}, "origin_fallback",
                                                    "url field origin fallback"))

    def test_an_origin_scope_may_not_report_an_origin_fallback(self):
        """Origin data cannot be a fallback from itself, and Google never says it is."""
        common = {"requested_url": "https://www.example.test/", "final_url":
                  "https://www.example.test/", "strategy": "mobile", "profile": "default"}
        for value in (True, False, None):
            with self.subTest(value=value):
                experience = field_experience(origin_fallback=value)
                with self.assertRaisesRegex(self.module.PageSpeedError,
                                            "origin fallback on origin field data"):
                    self.module.scope_rows(experience, "origin", common, distributions=False)
        # The page-level scope is where the flag belongs, and it still works there.
        rows = self.module.scope_rows(field_experience(origin_fallback=True), "url", common,
                                      distributions=False)
        self.assertEqual("true", rows[0]["origin_fallback"])
        self.assertEqual("origin", rows[0]["effective_scope"])
        # And an origin scope with no flag at all is the ordinary, accepted case.
        rows = self.module.scope_rows(field_experience(), "origin", common, distributions=False)
        self.assertEqual("false", rows[0]["origin_fallback"])
        self.assertEqual("origin", rows[0]["effective_scope"])

    def test_effective_scope_alone_cannot_classify_fallback_as_page_level(self):
        payload = with_field_data(
            url=field_experience(id="https://www.example.test", origin_fallback=True),
            origin=field_experience(id="https://www.example.test", overall_category="SLOW"),
        )
        rows, _ = self.field_of(payload, field_data="summary")
        # Reading effective_scope alone must never yield page-level data that is really site-wide.
        self.assertEqual([], [row for row in rows if row["effective_scope"] == "url"])
        self.assertEqual({"origin"}, {row["effective_scope"] for row in rows})
        # requested_scope is what still separates the fallback from the genuine origin object.
        self.assertEqual({"url", "origin"}, {row["requested_scope"] for row in rows})
        fallback = [row for row in rows if row["requested_scope"] == "url"]
        genuine = [row for row in rows if row["requested_scope"] == "origin"]
        self.assertTrue(fallback and genuine)
        self.assertEqual({"true"}, {row["origin_fallback"] for row in fallback})
        self.assertEqual({"false"}, {row["origin_fallback"] for row in genuine})

    def test_raw_metric_key_and_unit_travel_with_every_field_row(self):
        payload = with_field_data(url=field_experience(metrics={
            "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400, "category": "AVERAGE",
                                            "distributions": [{"min": 0, "max": 2500, "proportion": 1}]},
            "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 25, "category": "SLOW"},
            "EXPERIMENTAL_NEW_VITAL": {"percentile": 42, "category": "FAST"},
        }))
        rows, _ = self.field_of(payload, field_data="distributions")
        measured = [row for row in rows if row["row_type"] != "field_summary"]
        self.assertTrue(all(row["field_metric_key"] and row["unit"] for row in measured))
        by_name = {row["metric"]: row for row in measured if row["row_type"] == "field_metric"}
        self.assertEqual(("LARGEST_CONTENTFUL_PAINT_MS", "milliseconds"),
                         (by_name["largest_contentful_paint"]["field_metric_key"],
                          by_name["largest_contentful_paint"]["unit"]))
        self.assertEqual(("EXPERIMENTAL_NEW_VITAL", "api_value"),
                         (by_name["experimental_new_vital"]["field_metric_key"],
                          by_name["experimental_new_vital"]["unit"]))
        bucket = next(row for row in measured if row["row_type"] == "field_distribution")
        self.assertEqual(("LARGEST_CONTENTFUL_PAINT_MS", "milliseconds"),
                         (bucket["field_metric_key"], bucket["unit"]))

    def test_cumulative_layout_shift_keeps_the_raw_integer_and_a_distinct_name(self):
        payload = with_field_data(url=field_experience(metrics={
            "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 25, "category": "SLOW", "distributions": [
                {"min": 0, "max": 10, "proportion": 0.6},
                {"min": 10, "max": 25, "proportion": 0.25},
                {"min": 25, "proportion": 0.15},
            ]}}))
        rows, _ = self.field_of(payload, field_data="distributions")
        metric = next(row for row in rows if row["row_type"] == "field_metric")
        # The raw integer is preserved exactly: 25 is never rescaled to 0.25.
        self.assertEqual(25, metric["percentile"])
        self.assertEqual("cumulative_layout_shift_score_raw", metric["metric"])
        self.assertEqual("CUMULATIVE_LAYOUT_SHIFT_SCORE", metric["field_metric_key"])
        self.assertEqual("api_integer", metric["unit"])
        # The name must not be the one a Lighthouse CLS row uses, or the two would be compared.
        self.assertNotIn(metric["metric"], set(self.module.METRICS.values()))
        self.assertNotEqual("cumulative_layout_shift", metric["metric"])
        buckets = [row for row in rows if row["row_type"] == "field_distribution"]
        self.assertEqual([(0, 10), (10, 25), (25, "")],
                         [(row["bucket_min"], row["bucket_max"]) for row in buckets])
        self.assertEqual({"api_integer"}, {row["unit"] for row in buckets})

    def test_absent_field_values_are_never_reported_as_zero(self):
        payload = with_field_data(url=field_experience(metrics={
            # A real zero percentile survives; an unreported one stays visibly empty.
            "CUMULATIVE_LAYOUT_SHIFT_SCORE": {"percentile": 0, "category": "FAST"},
            "LARGEST_CONTENTFUL_PAINT_MS": {"category": "NONE"},
            "INTERACTION_TO_NEXT_PAINT": {},
        }))
        rows, _ = self.field_of(payload, field_data="summary")
        metrics = {row["metric"]: row for row in rows if row["row_type"] == "field_metric"}
        self.assertEqual(0, metrics["cumulative_layout_shift_score_raw"]["percentile"])
        self.assertEqual("", metrics["largest_contentful_paint"]["percentile"])
        self.assertEqual("NONE", metrics["largest_contentful_paint"]["field_category"])
        # A metric Google returned empty and a metric it never returned are both simply absent.
        self.assertNotIn("interaction_to_next_paint", metrics)
        self.assertNotIn("first_contentful_paint", metrics)

    def test_partial_field_data_reports_only_the_object_google_returned(self):
        # https://developers.google.com/speed/docs/insights/release_notes (2021-06-10): a page can
        # have sufficient data for some metrics and not others.
        payload = with_field_data(url=field_experience(
            metrics={"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400, "category": "AVERAGE"}}))
        rows, error = self.field_of(payload, field_data="summary")
        self.assertEqual({"url"}, {row["requested_scope"] for row in rows})
        self.assertEqual(["largest_contentful_paint"],
                         [row["metric"] for row in rows if row["row_type"] == "field_metric"])
        self.assertNotIn("NOTE:", error)

    def test_distributions_report_raw_bucket_bounds_and_proportions(self):
        rows, _ = self.field_of(with_field_data(url=field_experience()),
                                field_data="distributions")
        buckets = [row for row in rows if row["row_type"] == "field_distribution"
                   and row["metric"] == "largest_contentful_paint"]
        self.assertEqual(
            [(0, 2500, 0.7231), (2500, 4000, 0.19), (4000, "", 0.0869)],
            [(row["bucket_min"], row["bucket_max"], row["proportion"]) for row in buckets],
        )
        # A metric with no buckets keeps its percentile row and adds nothing else.
        self.assertEqual([], [row for row in rows if row["row_type"] == "field_distribution"
                              and row["metric"] == "cumulative_layout_shift_score_raw"])
        self.assertIn("cumulative_layout_shift_score_raw",
                      [row["metric"] for row in rows if row["row_type"] == "field_metric"])

    def test_absent_or_empty_distributions_stay_acceptable(self):
        for distributions in ({}, {"distributions": []}):
            with self.subTest(distributions=distributions):
                payload = with_field_data(url=field_experience(metrics={
                    "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400, "category": "AVERAGE",
                                                    **distributions}}))
                rows, _ = self.field_of(payload, field_data="distributions")
                self.assertEqual(["largest_contentful_paint"],
                                 [row["metric"] for row in rows if row["row_type"] == "field_metric"])
                self.assertEqual([], [row for row in rows if row["row_type"] == "field_distribution"])

    def test_rounded_distribution_proportions_stay_acceptable(self):
        payload = with_field_data(url=field_experience(metrics={
            "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400, "category": "AVERAGE",
                                            "distributions": [
                                                {"min": 0, "max": 2500, "proportion": 0.72},
                                                {"min": 2500, "max": 4000, "proportion": 0.19},
                                                {"min": 4000, "proportion": 0.08}]}}))
        rows, _ = self.field_of(payload, field_data="distributions")
        self.assertEqual(3, len([row for row in rows if row["row_type"] == "field_distribution"]))

    def test_field_rows_are_bounded_by_default_with_an_explicit_truncation_notice(self):
        payload = with_field_data(url=field_experience(), origin=field_experience(
            id="https://www.example.test", overall_category="SLOW"))
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "distributions", "--field-limit", "5", "--json"], payload)
        rows = [row for row in json.loads(emitted) if row["row_type"].startswith("field_")]
        self.assertEqual(5, len(rows))
        self.assertIn("WARNING: field output truncated to 5 rows.", error)
        # Truncation is a bound that was honoured, not requested work that did not happen.
        self.assertEqual(0, code)
        # Rows are dropped from the end, so the requested page's scope survives a small bound.
        self.assertEqual({"url"}, {row["requested_scope"] for row in rows})

    def test_field_limit_zero_reports_no_field_row_and_says_so(self):
        payload = with_field_data(url=field_experience())
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "summary", "--field-limit", "0", "--json"], payload)
        self.assertEqual(0, code)
        self.assertEqual([], [row for row in json.loads(emitted) if row["row_type"].startswith("field_")])
        self.assertIn("WARNING: field output truncated to 0 rows.", error)
        # Data that was dropped by the bound is not data Google failed to return.
        self.assertNotIn("no Chrome UX Report field data", error)

    def test_default_field_limit_holds_a_complete_current_response(self):
        self.assertEqual(100, self.module.FIELD_LIMIT_DEFAULT)
        self.assertEqual(500, self.module.FIELD_LIMIT_MAXIMUM)
        self.assertEqual(100, self.module.parser().parse_args(
            ["analyze", "--url", "https://example.test/"]).field_limit)
        every_metric = {key: {"percentile": 1, "category": "FAST", "distributions": [
            {"min": 0, "max": 10, "proportion": 0.5}, {"min": 10, "proportion": 0.5}]}
            for key in self.module.FIELD_METRICS}
        payload = with_field_data(url=field_experience(metrics=every_metric),
                                  origin=field_experience(metrics=every_metric,
                                                          id="https://www.example.test"))
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "distributions", "--json"], payload)
        self.assertEqual(0, code)
        self.assertEqual(2 * (1 + len(self.module.FIELD_METRICS) * 3),
                         len([row for row in json.loads(emitted)
                              if row["row_type"].startswith("field_")]))
        self.assertNotIn("truncated", error)

    def test_main_rejects_an_unbounded_field_limit_before_network(self):
        for value in ("501", "-1"):
            with self.subTest(value=value):
                with patch.dict(os.environ, self.env, clear=True), patch.object(
                    self.module.urllib.request, "urlopen", side_effect=AssertionError("network")
                ), redirect_stderr(io.StringIO()) as error:
                    code = self.module.main([
                        "analyze", "--profile", "example", "--url", "https://example.test/",
                        "--field-data", "summary", "--field-limit", value])
                self.assertEqual(2, code)
                self.assertIn("--field-limit must be between 0 and 500", error.getvalue())

    def test_unrecognized_field_metric_is_passed_through_lowercased(self):
        # The v5 reference documents the metrics map key only as `(key)`, so a new metric must not
        # disappear from the reading.
        payload = with_field_data(url=field_experience(metrics={
            "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400, "category": "AVERAGE"},
            "EXPERIMENTAL_NEW_VITAL": {"percentile": 42, "category": "FAST"},
        }))
        rows, _ = self.field_of(payload, field_data="summary")
        self.assertEqual([("largest_contentful_paint", "LARGEST_CONTENTFUL_PAINT_MS"),
                          ("experimental_new_vital", "EXPERIMENTAL_NEW_VITAL")],
                         [(row["metric"], row["field_metric_key"]) for row in rows
                          if row["row_type"] == "field_metric"])

    def test_missing_field_data_is_noted_rather_than_silently_empty(self):
        for payload in (with_field_data(),
                        with_field_data(url=None, origin=None),
                        {**with_field_data(), "loadingExperience": None,
                         "originLoadingExperience": {}}):
            with self.subTest(payload=payload):
                rows, error = self.field_of(payload, field_data="summary")
                self.assertEqual([], rows)
                self.assertIn("no Chrome UX Report field data", error)

    def test_text_output_carries_the_field_columns(self):
        emitted, _ = self.analyze(with_field_data(url=field_experience()), json=False,
                                  field_data="summary")
        header = emitted.splitlines()[0].split(",")
        self.assertEqual(["requested_scope", "effective_scope", "origin_fallback", "field_id",
                          "field_metric_key", "unit", "percentile", "field_category"],
                         header[header.index("requested_scope"):header.index("requested_scope") + 8])
        self.assertNotIn("bucket_min", header)
        self.assertIn("field_summary,,,,,,,,,,url,url,false,https://www.example.test/,,,,AVERAGE,",
                      emitted)
        self.assertIn("field_metric,,largest_contentful_paint,,,,,,,,url,url,false,"
                      "https://www.example.test/,LARGEST_CONTENTFUL_PAINT_MS,milliseconds,2400,AVERAGE,",
                      emitted)

    def test_distribution_columns_appear_only_when_requested(self):
        emitted, _ = self.analyze(with_field_data(url=field_experience()), json=False,
                                  field_data="distributions")
        self.assertEqual(["bucket_min", "bucket_max", "proportion"],
                         emitted.splitlines()[0].split(",")[18:21])

    def test_runtime_error_reports_requested_field_data_and_still_fails(self):
        # Trace scenario 1: the lab half failed, the field half was asked for and is valid.
        payload = with_field_data(url=field_experience(),
                                  runtimeError={"code": "ERRORED_DOCUMENT_REQUEST",
                                                "message": "Lighthouse was unable to load the page."})
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "summary", "--json"], payload)
        self.assertEqual(2, code)
        rows = json.loads(emitted)
        self.assertTrue(rows)
        # Only field rows: no score, metric, or audit row may be invented from a failed run.
        self.assertEqual({"field_summary", "field_metric"}, {row["row_type"] for row in rows})
        self.assertIn("ERRORED_DOCUMENT_REQUEST", error)
        self.assertIn("unable to load", error)
        self.assertTrue(error.startswith("ERROR: "), error)
        self.assertNotIn("Traceback", error)

    def test_runtime_error_without_requested_field_data_emits_nothing(self):
        # Trace scenario 2: field data was not asked for, so the fail-safe path is unchanged.
        payload = with_field_data(url=field_experience(),
                                  runtimeError={"code": "ERRORED_DOCUMENT_REQUEST", "message": "no load"})
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/"], payload)
        self.assertEqual(2, code)
        self.assertEqual("", emitted)
        self.assertIn("ERRORED_DOCUMENT_REQUEST", error)

    def test_runtime_error_with_no_field_data_available_emits_nothing(self):
        # Trace scenario 3: asked for, but Google returned none, so there is nothing to report.
        payload = with_field_data(runtimeError={"code": "ERRORED_DOCUMENT_REQUEST", "message": "no load"})
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "summary"], payload)
        self.assertEqual(2, code)
        self.assertEqual("", emitted)
        self.assertIn("ERRORED_DOCUMENT_REQUEST", error)
        self.assertNotIn("Traceback", error)

    def test_runtime_error_with_malformed_field_data_emits_nothing(self):
        # Trace scenario 4: requested field data is validated even though Lighthouse also failed.
        payload = with_field_data(url=field_experience(metrics={
            "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": "fast"}}),
            runtimeError={"code": "ERRORED_DOCUMENT_REQUEST", "message": "no load"})
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "summary"], payload)
        self.assertEqual(2, code)
        self.assertEqual("", emitted)
        self.assertIn("field metric percentile", error)
        self.assertNotIn("Traceback", error)

    def test_unknown_field_categories_are_refused(self):
        cases = (
            ({"loadingExperience": {"overall_category": "EXCELLENT"}},
             "unknown url field overall category: EXCELLENT"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"category": "GOOD"}}}},
             "unknown url LARGEST_CONTENTFUL_PAINT_MS field metric category: GOOD"),
        )
        for extra, expected in cases:
            with self.subTest(expected=expected):
                self.assertFieldRefused(extra, expected)
        for category in self.module.FIELD_CATEGORIES:
            with self.subTest(category=category):
                payload = with_field_data(url=field_experience(
                    overall_category=category,
                    metrics={"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 1, "category": category}}))
                rows, _ = self.field_of(payload, field_data="summary")
                self.assertEqual({category}, {row["field_category"] for row in rows})

    def test_incomplete_or_inconsistent_distributions_are_refused(self):
        def buckets(*items):
            return {"loadingExperience": {"metrics": {
                "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400, "distributions": list(items)}}}}

        cases = (
            (buckets({"min": 0, "max": 2500}), "bucket without a proportion"),
            (buckets({"min": 0, "max": 2500, "proportion": 1.5}), "proportion outside 0 to 1"),
            (buckets({"min": 0, "max": 2500, "proportion": -0.1}), "proportion outside 0 to 1"),
            (buckets({"min": 0, "max": 2500, "proportion": 0.4},
                     {"min": 2500, "proportion": 0.2}), "proportions totalling"),
            (buckets({"min": 0, "max": 2500, "proportion": 0.6},
                     {"min": 2500, "proportion": 0.9}), "proportions totalling"),
            (buckets({"max": 2500, "proportion": 1}), "bucket without a minimum"),
            (buckets({"min": -1, "max": 2500, "proportion": 1}), "negative"),
            (buckets({"min": 0, "max": -5, "proportion": 1}), "negative"),
            (buckets({"min": 2500, "max": 100, "proportion": 1}), "ending before it starts"),
            (buckets({"min": 0, "max": 3000, "proportion": 0.5},
                     {"min": 2500, "proportion": 0.5}), "overlapping or unordered"),
            (buckets({"min": 2500, "max": 4000, "proportion": 0.5},
                     {"min": 0, "proportion": 0.5}), "overlapping or unordered"),
            (buckets({"min": 0, "proportion": 0.5},
                     {"min": 2500, "proportion": 0.5}), "open-ended .* bucket before the last one"),
        )
        for extra, expected in cases:
            with self.subTest(expected=expected):
                self.assertFieldRefused(extra, expected)

    def test_malformed_field_data_is_refused(self):
        cases = (
            ({"loadingExperience": []}, "malformed url field data"),
            ({"loadingExperience": "x"}, "malformed url field data"),
            ({"originLoadingExperience": 7}, "malformed origin field data"),
            ({"loadingExperience": {"metrics": []}}, "malformed url field metrics object"),
            ({"loadingExperience": {"metrics": "x"}}, "malformed url field metrics object"),
            ({"loadingExperience": {"id": 7}}, "malformed url field data id"),
            ({"loadingExperience": {"overall_category": []}}, "malformed url field overall category"),
            ({"loadingExperience": {"origin_fallback": "true"}}, "malformed url field origin fallback"),
            ({"loadingExperience": {"origin_fallback": 1}}, "malformed url field origin fallback"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": None}}},
             "malformed url LARGEST_CONTENTFUL_PAINT_MS field metric object"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": "fast"}}}},
             "malformed url LARGEST_CONTENTFUL_PAINT_MS field metric percentile"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"percentile": NAN}}}},
             "non-finite url LARGEST_CONTENTFUL_PAINT_MS field metric percentile"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"category": 7}}}},
             "malformed url LARGEST_CONTENTFUL_PAINT_MS field metric category"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"distributions": None}}}},
             "malformed url LARGEST_CONTENTFUL_PAINT_MS field distribution collection"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS": {"distributions": ["x"]}}}},
             "malformed url LARGEST_CONTENTFUL_PAINT_MS field distribution"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS":
                                                {"distributions": [{"min": "zero", "proportion": 1}]}}}},
             "malformed url LARGEST_CONTENTFUL_PAINT_MS field distribution minimum"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS":
                                                {"distributions": [{"max": [], "proportion": 1}]}}}},
             "malformed url LARGEST_CONTENTFUL_PAINT_MS field distribution maximum"),
            ({"loadingExperience": {"metrics": {"LARGEST_CONTENTFUL_PAINT_MS":
                                                {"distributions": [{"min": 0, "proportion": INFINITY}]}}}},
             "non-finite url LARGEST_CONTENTFUL_PAINT_MS field distribution proportion"),
        )
        for extra, expected in cases:
            with self.subTest(expected=expected):
                self.assertFieldRefused(extra, expected)

    def test_field_validation_does_not_depend_on_the_output_mode(self):
        extra = {"loadingExperience": {"metrics": {
            "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": 2400,
                                            "distributions": [{"proportion": "most"}]}}}}
        for mode in ("summary", "distributions"):
            with self.subTest(mode=mode):
                self.assertFieldRefused(extra, "field distribution proportion", field_data=mode)

    def test_malformed_field_data_keeps_the_valid_lab_output_and_exits_two(self):
        """The optional section is what failed, so the lab assessment must still reach stdout."""
        payload = dict(GOLDEN_PAYLOAD)
        payload["loadingExperience"] = []
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "summary", "--json"], payload)
        # Requested work did not happen, so the status is non-zero even though output was produced.
        self.assertEqual(2, code)
        rows = json.loads(emitted)
        self.assertEqual(["summary", "metric", "audit"], [row["row_type"] for row in rows])
        self.assertEqual(82, rows[0]["score"])
        self.assertEqual([], [row for row in rows if row["row_type"].startswith("field_")])
        self.assertTrue(error.startswith("ERROR: "), error)
        self.assertIn("field data was not reported", error)
        self.assertIn("malformed url field data", error)
        self.assertNotIn("Traceback", error)

    def test_malformed_field_data_keeps_the_default_text_lab_output(self):
        payload = dict(GOLDEN_PAYLOAD)
        payload["loadingExperience"] = {"metrics": {
            "LARGEST_CONTENTFUL_PAINT_MS": {"percentile": "fast"}}}
        code, emitted, error = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "distributions"], payload)
        self.assertEqual(2, code)
        # Every lab row the caller asked for is present; only the field columns stay empty.
        self.assertEqual(4, len(emitted.splitlines()))
        self.assertIn("summary,performance", emitted)
        self.assertNotIn("field_summary", emitted)
        self.assertIn("field metric percentile", error)

    def test_a_refused_optional_section_never_suppresses_a_lab_finding(self):
        """The audit rows are the reason the command was run; they must survive a field refusal."""
        payload = dict(GOLDEN_PAYLOAD)
        payload["loadingExperience"] = {"overall_category": "EXCELLENT"}
        clean, _ = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/", "--json"],
            GOLDEN_PAYLOAD)[1:]
        code, emitted, _ = self.run_main(
            ["analyze", "--profile", "example", "--url", "https://example.test/",
             "--field-data", "summary", "--json"], payload)
        self.assertEqual(2, code)
        self.assertEqual(json.loads(clean), json.loads(emitted))

    def test_field_metric_names_and_units_match_the_documented_response_keys(self):
        # Key strings come from Google's own examples and release notes; see references/cli.md.
        self.assertEqual(
            {"FIRST_CONTENTFUL_PAINT_MS": ("first_contentful_paint", "milliseconds"),
             "LARGEST_CONTENTFUL_PAINT_MS": ("largest_contentful_paint", "milliseconds"),
             "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("cumulative_layout_shift_score_raw", "api_integer"),
             "INTERACTION_TO_NEXT_PAINT": ("interaction_to_next_paint", "milliseconds"),
             "FIRST_INPUT_DELAY_MS": ("first_input_delay", "milliseconds"),
             "EXPERIMENTAL_TIME_TO_FIRST_BYTE": ("experimental_time_to_first_byte", "milliseconds")},
            self.module.FIELD_METRICS,
        )
        self.assertEqual((("url", "loadingExperience"), ("origin", "originLoadingExperience")),
                         self.module.FIELD_SCOPES)
        self.assertEqual(("FAST", "AVERAGE", "SLOW", "NONE"), self.module.FIELD_CATEGORIES)
        # A field metric shares a lab name only where both measure the same quantity and unit.
        shared = {name for name, _ in self.module.FIELD_METRICS.values()} & set(self.module.METRICS.values())
        self.assertEqual({"first_contentful_paint", "largest_contentful_paint",
                          "interaction_to_next_paint"}, shared)
        self.assertNotIn("cumulative_layout_shift", shared)

    def test_field_data_json_output_stays_standards_safe(self):
        emitted, _ = self.analyze(with_field_data(url=field_experience()), field_data="distributions")
        self.assertNotIn("NaN", emitted)
        self.assertNotIn("Infinity", emitted)
        for row in json.loads(emitted):
            for value in row.values():
                if isinstance(value, float):
                    self.assertTrue(math.isfinite(value))

    def test_launcher_help_is_credential_free_and_resolves_outside_repo(self):
        result = subprocess.run([str(LAUNCHER), "--help"], cwd="/tmp", env={"PATH": os.environ.get("PATH", "")}, text=True, capture_output=True, check=False)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("PageSpeed Insights", result.stdout)


if __name__ == "__main__":
    unittest.main()
