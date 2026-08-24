#!/usr/bin/env python3
"""Offline tests for the Google Merchant Center integration."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parent / "google-merchant.py"
LAUNCHER = SCRIPT.parent.parent / "google-merchant"


def load_module():
    spec = importlib.util.spec_from_file_location("google_merchant_module", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Google Merchant module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class Response:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self):
        return self.payload


class RawResponse:
    """A response body Google never should have sent, kept exactly as received."""

    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return self.payload


def http_error(code, body=None, headers=None):
    stream = io.BytesIO(json.dumps(body).encode("utf-8") if body is not None else b"")
    return urllib.error.HTTPError("https://merchantapi.googleapis.com/x", code, "err", headers or {}, stream)


class StubAccess:
    """An account Rundesk has already granted, so a case can start at the Google boundary."""

    name = "example"

    def __init__(self, token="token"):
        self.granted = token

    def token(self):
        return self.granted


class ProfileTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def enterContext_tempdir(self):
        import tempfile

        directory = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__("shutil").rmtree(directory, ignore_errors=True))
        return directory


class QueryLanguageTest(unittest.TestCase):
    """MCQL defines no string escape, so a value needing one must be refused."""

    def setUp(self):
        self.module = load_module()

    def test_a_value_containing_a_quote_or_backslash_is_refused(self):
        for value in ("o'brien", 'say "hi"', "back\\slash", "tail'; DROP", '"'):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.mcql_string(value)

    def test_a_value_containing_a_control_character_is_refused(self):
        for value in ("line\nbreak", "tab\tstop", "null\x00byte", "del\x7f"):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.mcql_string(value)

    def test_an_ordinary_value_is_quoted_once(self):
        self.assertEqual("'Acme Tools'", self.module.mcql_string("Acme Tools"))

    def test_an_empty_or_non_string_value_is_refused(self):
        for value in ("", None, 5, ["a"]):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.mcql_string(value)

    def test_injection_through_a_command_option_cannot_reach_the_query(self):
        """A crafted --brand must fail rather than extend the WHERE clause."""
        module = self.module
        args = SimpleNamespace(
            profile="example", account="123", limit=10, json=False,
            status=None, brand="Acme' OR title != '", reporting_context=None,
        )
        with patch.object(module, "selected_access", lambda _: StubAccess()), \
                patch.object(module, "search_rows", side_effect=AssertionError("query was sent")):
            with self.assertRaises(module.MerchantError):
                module.command_products(args)

    def test_only_snake_case_identifiers_are_accepted_as_names(self):
        for value in ("Date", "offer id", "offer-id", "1st", "drop table", "", "a;b"):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.mcql_name(value)
        self.assertEqual("category_l1", self.module.mcql_name("category_l1"))

    def test_a_query_cannot_be_built_from_an_unchecked_field(self):
        query = self.module.Query("product_view", ("id; DROP",))
        with self.assertRaises(self.module.MerchantError):
            query.text()

    def test_only_real_calendar_dates_are_accepted(self):
        for value in ("2024-02-30", "2024-13-01", "24-01-01", "2024/01/01", "", "LAST_30_DAYS"):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.mcql_date(value, "--start-date")
        self.assertEqual("'2024-02-29'", self.module.mcql_date("2024-02-29", "--start-date"))

    def test_only_googles_documented_relative_ranges_are_accepted(self):
        self.assertEqual("date DURING LAST_30_DAYS", self.module.during("date", "LAST_30_DAYS"))
        for value in ("LAST_90_DAYS", "THIS_YEAR", "yesterday", "LAST_30_DAYS'"):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.during("date", value)

    def test_the_builder_joins_conditions_with_and_only(self):
        query = self.module.Query(
            "product_view", ("id", "title"), ("brand = 'A'", "condition = 'new'"), "title", False, 5
        )
        text = query.text()
        self.assertEqual(
            "SELECT id, title FROM product_view WHERE brand = 'A' AND condition = 'new' "
            "ORDER BY title ASC LIMIT 5",
            text,
        )
        self.assertNotIn(" OR ", text)

    def test_a_country_or_category_must_match_its_documented_form(self):
        self.assertEqual("US", self.module.country_code("us"))
        for value in ("USA", "U", "u1", "US'", ""):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.country_code(value)
        self.assertEqual("166", self.module.category_id("166"))
        for value in ("166 OR 1=1", "-1", "abc", ""):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.category_id(value)

    def test_an_enum_option_is_restricted_to_googles_members(self):
        self.assertEqual("ADS", self.module.enum_choice("ads", self.module.MARKETING_METHODS, "--marketing-method"))
        with self.assertRaises(self.module.MerchantError):
            self.module.enum_choice("BUY_ON_GOOGLE", self.module.MARKETING_METHODS, "--marketing-method")
        with self.assertRaises(self.module.MerchantError):
            self.module.reporting_context("SHOPPING_ADS' OR '1'='1")


class RequestContractTest(unittest.TestCase):
    """The exact query text and HTTP request each command sends."""

    def setUp(self):
        self.module = load_module()

    def capture(self, handler, args, results=None):
        sent = {}

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            sent.update(method=method, url=url, params=params, payload=payload)
            return {"results": results or []}

        module = self.module
        with patch.object(module, "selected_access", lambda _: StubAccess()), \
                patch.object(module, "api_request", fake_request), \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            handler(args)
        return sent

    def base(self, **overrides):
        args = dict(profile="example", account="123", limit=10, json=False)
        args.update(overrides)
        return SimpleNamespace(**args)

    def test_performance_sends_the_documented_search_request(self):
        sent = self.capture(
            self.module.command_performance,
            self.base(breakdown="product", during="LAST_30_DAYS", start_date=None, end_date=None,
                      marketing_method=None, country=None, store_type=None),
        )
        self.assertEqual("POST", sent["method"])
        self.assertEqual(
            "https://merchantapi.googleapis.com/reports/v1/accounts/123/reports:search", sent["url"]
        )
        self.assertEqual(
            {
                "query": "SELECT offer_id, title, clicks, impressions, click_through_rate, "
                         "conversions, conversion_value, conversion_rate "
                         "FROM product_performance_view WHERE date DURING LAST_30_DAYS "
                         "ORDER BY clicks DESC LIMIT 11",
                "pageSize": 11,
            },
            sent["payload"],
        )

    def test_performance_always_carries_a_date_condition(self):
        for window in (
            dict(during="LAST_7_DAYS", start_date=None, end_date=None),
            dict(during="LAST_30_DAYS", start_date="2024-01-01", end_date="2024-01-31"),
        ):
            with self.subTest(**window):
                sent = self.capture(
                    self.module.command_performance,
                    self.base(breakdown="brand", marketing_method=None, country=None,
                              store_type=None, **window),
                )
                self.assertIn("WHERE date ", sent["payload"]["query"])

    def test_a_partial_explicit_window_is_refused(self):
        module = self.module
        args = self.base(breakdown="date", during="LAST_30_DAYS", start_date="2024-01-01",
                         end_date=None, marketing_method=None, country=None, store_type=None)
        with self.assertRaises(module.MerchantError):
            module.date_condition(args)

    def test_a_time_breakdown_reads_in_order_and_others_read_largest_first(self):
        ordered = self.capture(
            self.module.command_performance,
            self.base(breakdown="date", during="LAST_30_DAYS", start_date=None, end_date=None,
                      marketing_method=None, country=None, store_type=None),
        )
        self.assertIn("ORDER BY date ASC", ordered["payload"]["query"])
        ranked = self.capture(
            self.module.command_performance,
            self.base(breakdown="brand", during="LAST_30_DAYS", start_date=None, end_date=None,
                      marketing_method=None, country=None, store_type=None),
        )
        self.assertIn("ORDER BY clicks DESC", ranked["payload"]["query"])

    def test_every_performance_breakdown_selects_a_metric_beside_its_segments(self):
        for breakdown in self.module.PERFORMANCE_BREAKDOWNS:
            with self.subTest(breakdown=breakdown):
                sent = self.capture(
                    self.module.command_performance,
                    self.base(breakdown=breakdown, during="LAST_30_DAYS", start_date=None,
                              end_date=None, marketing_method=None, country=None, store_type=None),
                )
                query = sent["payload"]["query"]
                self.assertIn("clicks", query)
                self.assertNotIn("*", query)

    def test_custom_label_uses_the_published_merchant_field_name(self):
        sent = self.capture(
            self.module.command_performance,
            self.base(breakdown="custom-label", during="LAST_30_DAYS", start_date=None,
                      end_date=None, marketing_method=None, country=None, store_type=None),
        )
        self.assertIn("SELECT custom_label0, clicks", sent["payload"]["query"])
        self.assertNotIn("custom_label_0", sent["payload"]["query"])

    def test_products_orders_by_click_potential_and_filters_by_context(self):
        sent = self.capture(
            self.module.command_products,
            self.base(status="eligible", brand="Acme", reporting_context="shopping_ads"),
        )
        self.assertEqual(
            "SELECT id, offer_id, title, brand, condition, availability, price, "
            "aggregated_reporting_context_status, click_potential, click_potential_rank, "
            "channel, feed_label, language_code FROM product_view "
            "WHERE aggregated_reporting_context_status = 'ELIGIBLE' AND brand = 'Acme' "
            "AND reporting_context = 'SHOPPING_ADS' ORDER BY click_potential_rank ASC LIMIT 11",
            sent["payload"]["query"],
        )

    def test_best_sellers_sends_googles_required_conditions(self):
        sent = self.capture(
            self.module.command_best_sellers,
            self.base(view="products", granularity="weekly", country="us", category="166", date="2022-10-10"),
        )
        query = sent["payload"]["query"]
        self.assertIn("report_granularity = 'WEEKLY'", query)
        self.assertIn("report_country_code = 'US'", query)
        # Google's own sample sends the category ID unquoted.
        self.assertIn("report_category_id = 166", query)
        self.assertIn("report_date = '2022-10-10'", query)
        for required in ("report_date", "report_granularity", "report_country_code", "report_category_id"):
            self.assertIn(required, query.split(" FROM ")[0])

    def test_best_sellers_omits_the_optional_conditions_when_unset(self):
        sent = self.capture(
            self.module.command_best_sellers,
            self.base(view="brands", granularity="monthly", country="US", category=None, date=None),
        )
        query = sent["payload"]["query"]
        self.assertIn("FROM best_sellers_brand_view", query)
        self.assertNotIn("report_category_id =", query)
        self.assertNotIn("report_date =", query)

    def test_the_top_merchant_view_never_selects_the_date_it_must_filter_on(self):
        sent = self.capture(
            self.module.command_competitive_visibility,
            self.base(view="top-merchant", country="US", category="166", during="LAST_30_DAYS",
                      start_date=None, end_date=None, traffic_source=None),
        )
        query = sent["payload"]["query"]
        selected, _, filtered = query.partition(" FROM ")
        self.assertNotIn("date", selected)
        self.assertIn("date DURING LAST_30_DAYS", filtered)

    def test_the_benchmark_view_selects_the_date_google_requires(self):
        sent = self.capture(
            self.module.command_competitive_visibility,
            self.base(view="benchmark", country="US", category="166", during="LAST_30_DAYS",
                      start_date=None, end_date=None, traffic_source=None),
        )
        selected = sent["payload"]["query"].split(" FROM ")[0]
        self.assertIn("date", selected)

    def test_competitive_visibility_always_bounds_country_and_category(self):
        for view in self.module.VISIBILITY_VIEWS:
            with self.subTest(view=view):
                sent = self.capture(
                    self.module.command_competitive_visibility,
                    self.base(view=view, country="US", category="166", during="LAST_30_DAYS",
                              start_date=None, end_date=None, traffic_source=None),
                )
                query = sent["payload"]["query"]
                self.assertIn("report_country_code = 'US'", query)
                self.assertIn("report_category_id = 166", query)

    def test_price_views_select_the_id_google_requires(self):
        for handler, extra, table in (
            (self.module.command_price_competitiveness, dict(country=None), "price_competitiveness_product_view"),
            (self.module.command_price_insights, {}, "price_insights_product_view"),
        ):
            with self.subTest(table=table):
                sent = self.capture(handler, self.base(**extra))
                query = sent["payload"]["query"]
                self.assertTrue(query.startswith("SELECT id,"))
                self.assertIn(f"FROM {table}", query)

    def test_price_competitiveness_selects_the_required_country_column(self):
        sent = self.capture(self.module.command_price_competitiveness, self.base(country=None))
        self.assertIn("report_country_code", sent["payload"]["query"].split(" FROM ")[0])

    def test_accounts_reads_the_documented_list_endpoint(self):
        sent = self.capture(self.module.command_accounts, self.base(limit=5))
        self.assertEqual("GET", sent["method"])
        self.assertEqual("https://merchantapi.googleapis.com/accounts/v1/accounts", sent["url"])
        self.assertEqual({"pageSize": 5}, sent["params"])

    def test_issue_commands_read_the_issueresolution_endpoint_with_a_bounded_filter(self):
        for handler in (self.module.command_status, self.module.command_issues):
            with self.subTest(handler=handler.__name__):
                sent = self.capture(
                    handler, self.base(reporting_context="shopping_ads", country="us")
                )
                self.assertEqual("GET", sent["method"])
                self.assertEqual(
                    "https://merchantapi.googleapis.com/issueresolution/v1/accounts/123/aggregateProductStatuses",
                    sent["url"],
                )
                self.assertEqual(
                    'reportingContext = "SHOPPING_ADS" AND country = "US"', sent["params"]["filter"]
                )

    def test_an_unfiltered_issue_read_sends_no_filter(self):
        sent = self.capture(self.module.command_status, self.base(reporting_context=None, country=None))
        self.assertNotIn("filter", sent["params"])

    def test_a_bad_query_is_rejected_before_any_credential_is_used(self):
        module = self.module
        args = self.base(status=None, brand=None, reporting_context=None)
        class Untouchable(StubAccess):
            def token(self):
                raise AssertionError("a token was asked for before the query was validated")

        with patch.object(module, "selected_access", lambda _: Untouchable()), \
                patch.object(module, "PRODUCT_FIELDS", ("id", "bad field")):
            with self.assertRaises(module.MerchantError):
                module.command_products(args)

    def test_an_account_id_is_required_to_be_numeric(self):
        self.assertEqual("123", self.module.account_id("accounts/123"))
        self.assertEqual("123", self.module.account_id("123"))
        for value in ("abc", "1/2", "", "12'", None, "accounts/abc"):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.account_id(value)


class TransportTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_an_unexpected_origin_is_refused_before_any_request(self):
        for url in (
            "https://evil.example/reports/v1/accounts/1/reports:search",
            "https://merchantapi.googleapis.com.evil.example/reports/v1/x",
            "https://merchantapi.googleapis.com/content/v2.1/x",
            "https://merchantapi.googleapis.com/accounts/v1beta/accounts",
        ):
            with self.subTest(url=url):
                with patch.object(self.module, "open_url", side_effect=AssertionError("network called")):
                    with self.assertRaises(self.module.MerchantError):
                        self.module.api_request("token", "GET", url)

    def test_a_report_row_missing_the_requested_view_is_refused(self):
        module = self.module
        query = module.Query("product_view", ("id",), limit=2)
        with patch.object(module, "api_request", return_value={"results": [{"wrongView": {}}]}):
            with self.assertRaises(module.MerchantError) as raised:
                module.search_rows("token", "1", query, 2, "productView")
        self.assertIn("without productView", str(raised.exception))

    def test_each_allowed_origin_is_a_pinned_v1_sub_api(self):
        for base in self.module.API_BASES:
            with self.subTest(base=base):
                self.assertTrue(base.startswith("https://merchantapi.googleapis.com/"))
                self.assertTrue(base.endswith("/v1"))
                self.assertNotIn("beta", base)
                self.assertNotIn("alpha", base)

    def test_a_redirect_is_refused_so_credentials_stay_on_the_api_origin(self):
        handler = self.module.RejectRedirectHandler()
        self.assertIsNone(
            handler.redirect_request(None, None, 302, "found", {}, "https://evil.example/")
        )

    def test_search_pages_until_google_omits_the_token(self):
        pages = [
            {"results": [{"productView": {"id": "a"}}], "nextPageToken": "t1"},
            {"results": [{"productView": {"id": "b"}}]},
        ]
        sent = []

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            sent.append(payload)
            return pages[len(sent) - 1]

        query = self.module.Query("product_view", ("id",))
        with patch.object(self.module, "api_request", fake_request):
            rows, truncated = self.module.search_rows("token", "1", query, 10, "productView")
        self.assertEqual([{"id": "a"}, {"id": "b"}], rows)
        self.assertFalse(truncated)
        self.assertNotIn("pageToken", sent[0])
        self.assertEqual("t1", sent[1]["pageToken"])
        # Every page must repeat the same query text.
        self.assertEqual(sent[0]["query"], sent[1]["query"])

    def test_a_short_page_does_not_end_pagination(self):
        pages = [
            {"results": [{"productView": {"id": "a"}}], "nextPageToken": "t1"},
            {"results": [{"productView": {"id": "b"}}, {"productView": {"id": "c"}}]},
        ]
        calls = []

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            calls.append(payload)
            return pages[len(calls) - 1]

        query = self.module.Query("product_view", ("id",))
        with patch.object(self.module, "api_request", fake_request):
            rows, _ = self.module.search_rows("token", "1", query, 10, "productView")
        self.assertEqual(3, len(rows))

    def test_a_short_list_page_does_not_end_pagination(self):
        pages = [
            {"accounts": [{"accountId": "1"}], "nextPageToken": "t1"},
            {"accounts": [{"accountId": "2"}]},
        ]
        calls = []

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            calls.append(params)
            return pages[len(calls) - 1]

        with patch.object(self.module, "api_request", fake_request):
            rows, truncated = self.module.list_rows(
                "token", "https://x/y", "accounts", "account", 10, 500
            )
        self.assertEqual([{"accountId": "1"}, {"accountId": "2"}], rows)
        self.assertFalse(truncated)
        self.assertEqual("t1", calls[1]["pageToken"])

    def test_a_page_size_never_exceeds_googles_ceiling(self):
        sent = []

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            sent.append(payload["pageSize"])
            return {"results": []}

        query = self.module.Query("product_view", ("id",))
        with patch.object(self.module, "api_request", fake_request):
            self.module.search_rows("token", "1", query, 5000, "productView")
        self.assertEqual([1000], sent)

    def test_a_repeated_page_token_is_refused_instead_of_looping(self):
        def fake_request(token, method, url, params=None, payload=None, retries=2):
            return {"results": [{"productView": {"id": "a"}}], "nextPageToken": "same"}

        query = self.module.Query("product_view", ("id",))
        with patch.object(self.module, "api_request", fake_request):
            with self.assertRaises(self.module.MerchantError):
                self.module.search_rows("token", "1", query, 100, "productView")

    def test_a_non_string_page_token_is_refused(self):
        def fake_request(token, method, url, params=None, payload=None, retries=2):
            return {"results": [], "nextPageToken": 7}

        query = self.module.Query("product_view", ("id",))
        with patch.object(self.module, "api_request", fake_request):
            with self.assertRaises(self.module.MerchantError):
                self.module.search_rows("token", "1", query, 10, "productView")

    def test_an_empty_page_with_a_token_stops_and_reports_truncation(self):
        def fake_request(token, method, url, params=None, payload=None, retries=2):
            return {"results": [], "nextPageToken": "more"}

        query = self.module.Query("product_view", ("id",))
        with patch.object(self.module, "api_request", fake_request):
            rows, truncated = self.module.search_rows("token", "1", query, 10, "productView")
        self.assertEqual([], rows)
        self.assertTrue(truncated)

    def test_reaching_the_limit_with_more_available_reports_truncation(self):
        def fake_request(token, method, url, params=None, payload=None, retries=2):
            return {"results": [{"productView": {"id": "a"}}], "nextPageToken": "more"}

        query = self.module.Query("product_view", ("id",))
        with patch.object(self.module, "api_request", fake_request):
            rows, truncated = self.module.search_rows("token", "1", query, 1, "productView")
        self.assertEqual(1, len(rows))
        self.assertTrue(truncated)

    def test_list_reads_respect_each_methods_page_ceiling(self):
        sent = []

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            sent.append(params["pageSize"])
            return {"accounts": []}

        with patch.object(self.module, "api_request", fake_request):
            self.module.list_rows("token", "https://x/y", "accounts", "account", 4000, 500)
        self.assertEqual([500], sent)

    def test_limits_are_bounded(self):
        self.assertEqual(10, self.module.bounded_limit(10))
        for value in (0, -1, 100000):
            with self.subTest(value=value):
                with self.assertRaises(self.module.MerchantError):
                    self.module.bounded_limit(value)

    def test_a_retryable_status_is_retried_and_a_client_error_is_not(self):
        attempts = []

        def flaky(request, timeout=30):
            attempts.append(request)
            if len(attempts) == 1:
                raise http_error(503)
            return Response({"ok": True})

        with patch.object(self.module, "open_url", flaky), patch.object(self.module.time, "sleep", lambda s: None):
            self.assertEqual(
                {"ok": True},
                self.module.api_request("token", "GET", f"{self.module.ACCOUNTS_BASE}/accounts"),
            )
        self.assertEqual(2, len(attempts))

    def test_a_permission_failure_reports_googles_message(self):
        body = {
            "error": {
                "code": 401,
                "message": "The caller does not have access to the accounts: [1234567]",
                "status": "UNAUTHENTICATED",
            }
        }
        with patch.object(self.module, "open_url", side_effect=http_error(401, body)):
            with self.assertRaises(self.module.MerchantError) as raised:
                self.module.api_request("token", "GET", f"{self.module.ACCOUNTS_BASE}/accounts")
        self.assertIn("does not have access", str(raised.exception))

    def test_an_invalid_query_failure_reports_googles_message(self):
        body = {"error": {"code": 400, "message": "The query is invalid.", "status": "INVALID_ARGUMENT"}}
        with patch.object(self.module, "open_url", side_effect=http_error(400, body)):
            with self.assertRaises(self.module.MerchantError) as raised:
                self.module.api_request("token", "POST", f"{self.module.REPORTS_BASE}/accounts/1/reports:search")
        self.assertIn("The query is invalid.", str(raised.exception))

    def test_an_error_body_without_a_message_falls_back_to_the_status_code(self):
        with patch.object(self.module, "open_url", side_effect=http_error(403, {"nope": 1})):
            with self.assertRaises(self.module.MerchantError) as raised:
                self.module.api_request("token", "GET", f"{self.module.ACCOUNTS_BASE}/accounts")
        self.assertIn("HTTP 403", str(raised.exception))


class MalformedResponseTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_a_body_that_is_not_json_is_reported_without_a_traceback(self):
        with patch.object(self.module, "open_url", lambda request, timeout=30: RawResponse(b"<html>")):
            with self.assertRaises(self.module.MerchantError):
                self.module.api_request("token", "GET", f"{self.module.ACCOUNTS_BASE}/accounts")

    def test_a_list_or_scalar_body_is_refused(self):
        for payload in ([], "text", 5):
            with self.subTest(payload=payload):
                with patch.object(self.module, "open_url", lambda request, timeout=30, p=payload: Response(p)):
                    with self.assertRaises(self.module.MerchantError):
                        self.module.api_request("token", "GET", f"{self.module.ACCOUNTS_BASE}/accounts")

    def test_a_malformed_results_collection_is_refused(self):
        for payload in ({"results": "rows"}, {"results": ["a"]}, {"results": [{"productView": 5}]}):
            with self.subTest(payload=payload):
                with patch.object(self.module, "api_request", lambda *a, **k: payload):
                    query = self.module.Query("product_view", ("id",))
                    with self.assertRaises(self.module.MerchantError):
                        self.module.search_rows("token", "1", query, 10, "productView")

    def test_a_nested_value_in_a_scalar_cell_is_refused(self):
        with self.assertRaises(self.module.MerchantError):
            self.module.text_field({"accountId": {"a": 1}}, "accountId")

    def test_an_unrecognized_nested_report_value_is_refused(self):
        with self.assertRaises(self.module.MerchantError):
            self.module.report_cell({"surprise": 1})

    def test_a_malformed_price_amount_is_refused(self):
        with self.assertRaises(self.module.MerchantError):
            self.module.money_amount({"amountMicros": "many", "currencyCode": "USD"})

    def test_a_malformed_body_exits_two_rather_than_raising(self):
        env = {
            "GOOGLE_MERCHANT_CLIENT_ID": "client",
            "GOOGLE_MERCHANT_CLIENT_SECRET": "secret",
            "GOOGLE_MERCHANT_REFRESH_TOKEN": "refresh",
        }
        errors = io.StringIO()
        with patch.dict(os.environ, env, clear=True), patch.object(
            self.module, "selected_access", lambda args: StubAccess()
        ), patch.object(self.module, "open_url", lambda request, timeout=30: RawResponse(b"nope")), \
                redirect_stderr(errors), redirect_stdout(io.StringIO()):
            result = self.module.main(["accounts"])
        self.assertEqual(2, result)
        self.assertIn("ERROR:", errors.getvalue())


class OutputTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_a_price_is_rendered_exactly_with_its_own_currency_column(self):
        rows = [{"price": {"amountMicros": "150000000", "currencyCode": "USD"}, "id": "a"}]
        headers, table = self.module.report_table(rows, ("id", "price"), {})
        self.assertEqual(["id", "price", "price_currency"], headers)
        self.assertEqual("150", table[0]["price"])
        self.assertEqual("USD", table[0]["price_currency"])

    def test_a_fractional_price_keeps_its_exact_value(self):
        self.assertEqual("19.99", self.module.money_amount({"amountMicros": "19990000"}))
        self.assertEqual("0.01", self.module.money_amount({"amountMicros": "10000"}))

    def test_googles_zero_padded_currency_row_is_preserved_rather_than_merged(self):
        """Google splits price and non-price metrics into separate rows per currency."""
        rows = [
            {"conversions": "27", "conversionValue": {"amountMicros": "0", "currencyCode": ""}},
            {"conversions": "0", "conversionValue": {"amountMicros": "150000000", "currencyCode": "USD"}},
            {"conversions": "0", "conversionValue": {"amountMicros": "70000000", "currencyCode": "CAD"}},
        ]
        headers, table = self.module.report_table(rows, ("conversions", "conversion_value"), {})
        self.assertIn("conversion_value_currency", headers)
        self.assertEqual(3, len(table))
        self.assertEqual(["", "USD", "CAD"], [row["conversion_value_currency"] for row in table])
        self.assertEqual(["27", "0", "0"], [row["conversions"] for row in table])

    def test_a_price_missing_its_amount_still_reports_its_currency(self):
        """Header detection and cell rendering must recognize a Price identically."""
        rows = [{"price": {"currencyCode": "USD"}}]
        headers, table = self.module.report_table(rows, ("price",), {})
        self.assertIn("price_currency", headers)
        self.assertEqual("", table[0]["price"])
        self.assertEqual("USD", table[0]["price_currency"])

    def test_money_schema_is_stable_for_empty_results(self):
        headers, table = self.module.report_table([], ("id", "price", "conversion_value"), {})
        self.assertEqual(
            ["id", "price", "price_currency", "conversion_value", "conversion_value_currency"],
            headers,
        )
        self.assertEqual([], table)

    def test_a_date_is_rendered_from_either_shape_google_sends(self):
        self.assertEqual("2023-12-01", self.module.report_cell({"year": 2023, "month": 12, "day": 1}))
        self.assertEqual("2022-10-10", self.module.report_cell("2022-10-10"))

    def test_a_repeated_field_is_joined_rather_than_dumped(self):
        self.assertEqual("a|b", self.module.report_cell(["a", "b"]))
        self.assertEqual("true", self.module.report_cell(True))
        self.assertEqual("", self.module.report_cell(None))

    def test_a_snake_case_field_reads_its_camel_case_response_key(self):
        self.assertEqual("clickThroughRate", self.module.camel("click_through_rate"))
        self.assertEqual("categoryL1", self.module.camel("category_l1"))
        self.assertEqual("clicks", self.module.camel("clicks"))
        self.assertEqual("productPerformanceView", self.module.camel("product_performance_view"))
        self.assertEqual("customLabel0", self.module.camel("custom_label0"))

    def test_every_queried_view_maps_to_its_response_key(self):
        tables = ["product_performance_view", "product_view", "price_competitiveness_product_view",
                  "price_insights_product_view", "competitive_visibility_benchmark_view"]
        tables.extend(table for table, _ in self.module.BEST_SELLER_VIEWS.values())
        for table in tables:
            with self.subTest(table=table):
                key = self.module.camel(table)
                self.assertTrue(key[0].islower())
                self.assertEqual(table, "".join(
                    "_" + c.lower() if c.isupper() else c for c in key
                ))

    def test_issues_are_reported_with_the_largest_blast_radius_first(self):
        module = self.module
        statuses = [
            {
                "reportingContext": "SHOPPING_ADS",
                "country": "US",
                "itemLevelIssues": [
                    {"code": "small", "productCount": "2", "severity": "DEMOTED",
                     "resolution": "MERCHANT_ACTION", "documentationUri": "https://x"},
                    {"code": "large", "productCount": "90", "severity": "DISAPPROVED",
                     "resolution": "MERCHANT_ACTION", "documentationUri": "https://y"},
                ],
            }
        ]
        output = io.StringIO()
        with patch.object(module, "selected_access", lambda _: StubAccess()), \
                patch.object(module, "list_rows", lambda *a, **k: (statuses, False)), \
                redirect_stdout(output), redirect_stderr(io.StringIO()):
            module.command_issues(SimpleNamespace(
                profile="example", account="123", limit=10, json=False,
                reporting_context=None, country=None,
            ))
        lines = output.getvalue().strip().splitlines()
        self.assertTrue(lines[1].startswith("large,DISAPPROVED,MERCHANT_ACTION,90"))
        self.assertTrue(lines[2].startswith("small,DEMOTED,MERCHANT_ACTION,2"))

    def test_issues_limit_bounds_emitted_rows_not_status_buckets(self):
        module = self.module
        statuses = [{
            "reportingContext": "SHOPPING_ADS",
            "country": "US",
            "itemLevelIssues": [
                {"code": "small", "productCount": "2"},
                {"code": "large", "productCount": "90"},
            ],
        }]
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(module, "selected_access", lambda _: StubAccess()), \
                patch.object(module, "list_rows", side_effect=lambda *a, **k: (statuses, False)) as listed, \
                redirect_stdout(output), redirect_stderr(errors):
            module.command_issues(SimpleNamespace(
                profile="example", account="123", limit=1, json=False,
                reporting_context=None, country=None,
            ))
        self.assertEqual(1000, listed.call_args.args[4])
        lines = output.getvalue().strip().splitlines()
        self.assertEqual(2, len(lines))
        self.assertTrue(lines[1].startswith("large,"))
        self.assertIn("--limit 1", errors.getvalue())

    def test_issues_refuse_a_non_integer_product_count(self):
        module = self.module
        statuses = [{
            "reportingContext": "SHOPPING_ADS",
            "country": "US",
            "itemLevelIssues": [{"code": "bad", "productCount": "many"}],
        }]
        with patch.object(module, "selected_access", lambda _: StubAccess()), \
                patch.object(module, "list_rows", return_value=(statuses, False)), \
                redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            with self.assertRaises(module.MerchantError) as raised:
                module.command_issues(SimpleNamespace(
                    profile="example", account="123", limit=1, json=False,
                    reporting_context=None, country=None,
                ))
        self.assertIn("productCount", str(raised.exception))

    def test_an_omitted_issue_product_count_is_zero_and_does_not_hide_other_issues(self):
        module = self.module
        statuses = [{
            "reportingContext": "SHOPPING_ADS",
            "country": "US",
            "itemLevelIssues": [
                {"code": "zero", "severity": "NOT_IMPACTED"},
                {"code": "large", "severity": "DISAPPROVED", "productCount": "42"},
            ],
        }]
        output = io.StringIO()
        with patch.object(module, "selected_access", lambda _: StubAccess()), \
                patch.object(module, "list_rows", return_value=(statuses, False)), \
                redirect_stdout(output), redirect_stderr(io.StringIO()):
            module.command_issues(SimpleNamespace(
                profile="example", account="123", limit=10, json=False,
                reporting_context=None, country=None,
            ))
        lines = output.getvalue().strip().splitlines()
        self.assertTrue(lines[1].startswith("large,DISAPPROVED,,42"))
        self.assertTrue(lines[2].startswith("zero,NOT_IMPACTED,,0"))

    def test_omitted_aggregate_counts_are_rendered_as_zero(self):
        module = self.module
        statuses = [{
            "reportingContext": "SHOPPING_ADS",
            "country": "US",
            "stats": {"activeCount": "1500"},
        }]
        output = io.StringIO()
        with patch.object(module, "selected_access", lambda _: StubAccess()), \
                patch.object(module, "list_rows", return_value=(statuses, False)), \
                redirect_stdout(output), redirect_stderr(io.StringIO()):
            module.command_status(SimpleNamespace(
                profile="example", account="123", limit=10, json=False,
                reporting_context=None, country=None,
            ))
        self.assertIn("SHOPPING_ADS,US,1500,0,0,0,0,123,example", output.getvalue())

    def test_report_limit_uses_a_sentinel_row_and_warns(self):
        module = self.module
        output, errors = io.StringIO(), io.StringIO()
        captured = {}

        def fake_search(token, account, query, limit, view):
            captured["query"] = query.text()
            captured["limit"] = limit
            return ([{"id": "first"}, {"id": "sentinel"}], False)

        with patch.object(module, "selected_access", lambda _: StubAccess()), \
                patch.object(module, "search_rows", side_effect=fake_search), \
                redirect_stdout(output), redirect_stderr(errors):
            module.run_report(
                SimpleNamespace(profile="example", account="123", limit=1, json=False),
                "product_view", ("id",), (),
            )
        self.assertEqual(2, captured["limit"])
        self.assertTrue(captured["query"].endswith("LIMIT 2"))
        self.assertEqual(["id,account_id,profile", "first,123,example"], output.getvalue().strip().splitlines())
        self.assertIn("--limit 1", errors.getvalue())

    def test_an_unrecognized_aggregate_status_shape_fails_loudly(self):
        """A shape this package does not recognize must not print empty columns."""
        module = self.module
        # The field names Google's migration-era guide shows instead of the ones the
        # client-library sample and discovery document use.
        foreign = [{
            "reportingContext": "SHOPPING_ADS",
            "countryCode": "US",
            "statistics": {"approvedCount": "1500"},
            "issues": [{"issueType": "missing_image", "numProducts": "15"}],
        }]
        for handler in (module.command_status, module.command_issues):
            with self.subTest(handler=handler.__name__):
                with patch.object(module, "selected_access", lambda _: StubAccess()), \
                        patch.object(module, "list_rows", lambda *a, **k: (foreign, False)), \
                        redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    with self.assertRaises(module.MerchantError) as raised:
                        handler(SimpleNamespace(
                            profile="example", account="123", limit=10, json=False,
                            reporting_context=None, country=None,
                        ))
                self.assertTrue(
                    "unrecognized" in str(raised.exception) or "without stats" in str(raised.exception)
                )

    def test_a_recognized_aggregate_status_shape_is_accepted(self):
        self.assertEqual(
            {"stats": {}}, self.module.expect_known_shape({"stats": {}}, ("stats", "itemLevelIssues"), "x")
        )
        self.assertEqual(
            {"itemLevelIssues": []},
            self.module.expect_known_shape({"itemLevelIssues": []}, ("stats", "itemLevelIssues"), "x"),
        )

    def test_json_output_is_opt_in(self):
        module = self.module
        rows = [{"a": "1"}]
        plain, structured = io.StringIO(), io.StringIO()
        with redirect_stdout(plain):
            module.emit_rows(("a",), rows, False)
        with redirect_stdout(structured):
            module.emit_rows(("a",), rows, True)
        self.assertEqual("a\n1\n", plain.getvalue())
        self.assertEqual(rows, json.loads(structured.getvalue()))

    def test_truncation_is_reported_on_stderr(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            self.module.warn_truncated(True, 25)
        self.assertIn("--limit 25", errors.getvalue())


class SecretSafetyTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_a_failure_never_discloses_the_token_it_was_granted(self):
        errors, output = io.StringIO(), io.StringIO()
        with patch.object(
            self.module, "selected_access", lambda args: StubAccess("granted-access-token")
        ), patch.object(
            self.module, "open_url", side_effect=http_error(401, {"error": {"message": "denied"}})
        ), redirect_stderr(errors), redirect_stdout(output):
            result = self.module.main(["performance", "--account", "123"])
        self.assertEqual(2, result)
        combined = errors.getvalue() + output.getvalue()
        self.assertIn("denied", combined)
        self.assertNotIn("granted-access-token", combined)

    def test_the_authorization_header_is_never_printed(self):
        errors, output = io.StringIO(), io.StringIO()
        with patch.object(
            self.module, "selected_access", lambda args: StubAccess("super-secret-token")
        ), patch.object(
            self.module, "open_url", side_effect=urllib.error.URLError("offline")
        ), redirect_stderr(errors), redirect_stdout(output):
            self.module.main(["accounts"])
        combined = errors.getvalue() + output.getvalue()
        self.assertNotIn("super-secret-token", combined)
        self.assertNotIn("Bearer", combined)

    def test_the_source_carries_no_credential_or_owner_path(self):
        # Both markers are assembled rather than written out, so this assertion does not
        # itself trip the catalog suite's scan for owner paths and committed keys.
        home_root = str(Path.home().parent) + os.sep
        private_key = "BEGIN " + "RSA PRIVATE KEY"
        text = SCRIPT.read_text(encoding="utf-8")
        for forbidden in (home_root, "refresh_token=1//", private_key):
            self.assertNotIn(forbidden, text)


class LauncherTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()

    def test_the_launcher_resolves_its_runtime_outside_the_repository(self):
        completed = subprocess.run(
            [str(LAUNCHER), "--help"], cwd="/", env={"PATH": os.environ.get("PATH", "")},
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("Google Merchant Center", completed.stdout)

    def test_every_subcommand_helps_without_credentials(self):
        parser = self.module.build_parser()
        commands = [
            action.choices for action in parser._subparsers._group_actions if action.choices
        ][0]
        for command in commands:
            with self.subTest(command=command):
                completed = subprocess.run(
                    [str(LAUNCHER), command, "--help"], cwd="/",
                    env={"PATH": os.environ.get("PATH", "")},
                    text=True, capture_output=True, check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertIn("usage:", completed.stdout.lower())

    def test_an_unknown_option_value_is_rejected_by_the_parser(self):
        parser = self.module.build_parser()
        for argv in (
            ["performance", "--account", "1", "--breakdown", "cohort"],
            ["best-sellers", "--account", "1", "--country", "US", "--granularity", "daily"],
            ["competitive-visibility", "--account", "1", "--country", "US", "--category", "1", "--view", "rivals"],
        ):
            with self.subTest(argv=argv):
                with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                    parser.parse_args(argv)

    def test_an_account_is_required_for_every_account_scoped_command(self):
        parser = self.module.build_parser()
        for command in ("status", "issues", "products", "performance", "price-insights"):
            with self.subTest(command=command):
                with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                    parser.parse_args([command])


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

    def accounts_payload(self):
        return {"accounts": [{"accountId": "123", "accountName": "Example Shop",
                              "languageCode": "en", "timeZone": {"id": "UTC"}}]}

    def authorization(self):
        return [request.get_header("Authorization") for request in self.requests]

    # --- the protocol itself ------------------------------------------------------------------

    def test_access_is_asked_for_over_an_inherited_pipe_and_used_only_as_a_header(self):
        self.payloads = [self.accounts_payload()]
        code, out, err = self.invoke(["accounts"])
        self.assertEqual(0, code, err)
        asked = self.asked()
        self.assertEqual(1, len(asked))
        self.assertEqual(["_oauth", "access", "google", "merchant", "--response-fd"],
                         asked[0][:5])
        # The stand-in makes Rundesk's own check, so passing proves an inherited connected unnamed
        # local socket rather than 0, 1, 2, a pipe, a named socket, or a file.
        self.assertGreater(int(asked[0][5]), 2)
        self.assertEqual(["Bearer " + MANAGED_TOKEN], self.authorization())
        self.assertIn("Example Shop", out)

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
                with self.assertRaisesRegex(self.module.MerchantError, expected):
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
        with self.assertRaisesRegex(self.module.MerchantError, "oversized"):
            self.module.read_frame(ours, time.monotonic() + 5)

    def test_truncated_and_silent_answers_are_refused_rather_than_waited_on(self):
        ours, theirs = self.pair()
        theirs.sendall(struct.pack(">I", 64) + b"{")
        theirs.close()
        with self.assertRaisesRegex(self.module.MerchantError, "closed the Google response"):
            self.module.read_frame(ours, time.monotonic() + 5)
        quiet, _held = self.pair()
        with self.assertRaisesRegex(self.module.MerchantError, "in time"):
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
            code, _, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("in time", err)
        # The stand-in would sleep for ten minutes, so this bounds the wait rather than the machine.
        self.assertLess(time.monotonic() - started, 30)
        self.no_child_is_left()

    def test_a_child_that_answers_and_then_hangs_is_still_stopped(self):
        self.plan["mode"] = "frame-then-hang"
        with patch.object(self.module, "BRIDGE_SECONDS", 0.3):
            code, _, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("in time", err)
        self.no_child_is_left()

    def test_a_sign_in_nobody_completes_is_stopped_at_its_own_deadline(self):
        self.plan["mode"] = "login-hang"
        with patch.object(self.module, "SIGN_IN_SECONDS", 0.3):
            code, _, err = self.invoke(["accounts", "--auth"])
        self.assertEqual(2, code)
        self.assertIn("signing in to Google", err)
        self.assertEqual([], self.requests)
        self.no_child_is_left()

    def test_rundesk_answering_nothing_at_all_is_a_refusal_with_the_login_command(self):
        self.plan["mode"] = "silent"
        code, _, err = self.invoke(["accounts"])
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
        self.payloads = [self.accounts_payload()]
        code, out, err = self.invoke(["accounts", "--profile", "acme", "--email", "two@example.test"])
        self.assertEqual(2, code)
        self.assertIn("other than two@example.test", err)
        # Refused before the request, not after: nothing was asked of Google.
        self.assertEqual([], self.requests)
        self.assertEqual("", out)

    def test_the_same_address_in_another_case_is_the_same_account(self):
        self.plan["accounts"] = {"ACME": ["Two@Example.test"]}
        self.payloads = [self.accounts_payload()]
        code, _, err = self.invoke(["accounts", "--profile", "acme", "--email", "two@example.test"])
        self.assertEqual(0, code, err)

    def test_profile_and_email_are_forwarded_to_rundesk_unchanged(self):
        self.plan["accounts"] = {"ACME": ["one@example.test", "two@example.test"]}
        self.payloads = [self.accounts_payload()]
        code, _, err = self.invoke(["accounts", "--profile", "acme", "--email", "two@example.test"])
        self.assertEqual(0, code, err)
        self.assertEqual(
            ["_oauth", "access", "google", "merchant", "--profile", "acme",
             "--email", "two@example.test"],
            self.asked()[0][:8],
        )
        self.assertEqual(["Bearer access-token-for-two@example.test"], self.authorization())

    def test_several_accounts_under_one_app_profile_need_an_explicit_email(self):
        self.plan["accounts"] = {"ACME": ["one@example.test", "two@example.test"]}
        code, _, err = self.invoke(["accounts", "--profile", "acme"])
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
        code, _, err = self.invoke(["accounts", "--profile", "acme"])
        self.assertEqual(2, code)
        self.assertIn("did not return a reusable grant for every requested scope", err)
        self.assertIn("Run: rundesk login google --profile acme", err)

    def test_auth_signs_in_first_and_forwards_the_app_profile(self):
        self.plan["accounts"] = {"ACME": ["one@example.test"]}
        self.payloads = [self.accounts_payload()]
        code, _, err = self.invoke(["accounts", "--auth", "--profile", "acme"])
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
        code, _, err = self.invoke(["accounts", "--auth"])
        self.assertEqual(2, code)
        self.assertIn("Google login was declined", err)
        self.assertEqual([], self.requests)

    def test_a_token_that_is_not_bearer_is_refused_rather_than_sent(self):
        self.plan["mode"] = "wrong-token-type"
        code, _, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("cannot send", err)
        self.assertEqual([], self.requests)

    def test_a_grant_without_a_subject_is_refused(self):
        self.plan["mode"] = "no-subject"
        code, _, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("no usable Google access token", err)
        self.assertEqual([], self.requests)

    def test_a_framed_refusal_is_read_from_the_socket_rather_than_from_stderr(self):
        self.plan["accounts"] = {"ACME": []}
        code, _, err = self.invoke(["accounts", "--profile", "acme"])
        self.assertEqual(2, code)
        # Rundesk frames the reason and also says it; the framed one is what this package reports.
        self.assertIn("no matching Google profile is connected", err)
        self.assertNotIn("oauth: FAILED", err)
        self.assertIn("rundesk login google --profile acme", err)

    def test_an_unknown_provider_or_capability_is_reported_as_rundesk_framed_it(self):
        with patch.object(self.module, "PROVIDER", "nowhere"):
            code, _, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("no installed OAuth provider called 'nowhere'", err)

    def test_an_expired_token_is_refused_rather_than_sent_to_google(self):
        self.plan["mode"] = "expired"
        code, _, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("expired", err)
        self.assertEqual([], self.requests)

    # --- an older Rundesk ----------------------------------------------------------------------

    def test_a_rundesk_without_the_bridge_says_to_update_and_sign_in(self):
        self.plan["mode"] = "old"
        code, _, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("older than Rundesk-managed Google sign-in", err)
        self.assertIn("rundesk login google", err)

    def test_no_rundesk_at_all_is_reported_as_the_missing_install_it_is(self):
        # An empty PATH as well, so the case cannot reach whatever install runs it.
        code, _, err = self.invoke(["accounts"], RUNDESK_COMMAND="", PATH=str(self.home / "none"))
        self.assertEqual(2, code)
        self.assertIn("no Rundesk is reachable", err)
        self.assertIn("rundesk login google", err)

    # --- the token never leaves this process ---------------------------------------------------

    def test_the_token_reaches_no_argument_variable_or_stream(self):
        self.payloads = [self.accounts_payload()]
        with patch.dict(os.environ, self.environment(), clear=True), patch.object(
            self.module, "open_url", self.opener
        ), redirect_stdout(io.StringIO()) as out, redirect_stderr(io.StringIO()) as err:
            code = self.module.main(["accounts"])
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
