#!/usr/bin/env python3
"""Offline tests for the Google Analytics integration."""

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


SCRIPT = Path(__file__).resolve().parent / "google-analytics.py"
LAUNCHER = SCRIPT.parent.parent / "google-analytics"


def load_module():
    spec = importlib.util.spec_from_file_location("google_analytics_module", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load Google Analytics module")
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


class StubAccess:
    """An account Rundesk has already granted, so a case can start at the Google boundary."""

    name = "example"

    def __init__(self, token="token"):
        self.granted = token

    def token(self):
        return self.granted


class GoogleAnalyticsTest(unittest.TestCase):
    def setUp(self):
        self.module = load_module()
        self.access = StubAccess()

    def test_api_request_refuses_unexpected_origin(self):
        with self.assertRaises(self.module.AnalyticsError):
            self.module.api_request("token", "GET", "https://example.test/data")

    def test_redirects_are_refused(self):
        handler = self.module.RejectRedirectHandler()
        request = self.module.urllib.request.Request(
            self.module.ADMIN_BASE + "/accountSummaries",
            headers={"Authorization": "Bearer secret"},
        )
        self.assertIsNone(
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://example.test/intercept",
            )
        )

    def test_api_error_does_not_disclose_authorization(self):
        request_error = urllib.error.HTTPError(
            "https://analyticsdata.googleapis.com/v1beta/properties/1:runReport",
            403,
            "Forbidden",
            {},
            io.BytesIO(b'{"error":{"message":"Permission denied"}}'),
        )
        with patch.object(self.module, "open_url", side_effect=request_error):
            with self.assertRaises(self.module.AnalyticsError) as raised:
                self.module.api_request(
                    "sensitive-access-token",
                    "POST",
                    self.module.DATA_BASE + "/properties/1:runReport",
                    payload={},
                    retries=0,
                )
        self.assertIn("Permission denied", str(raised.exception))
        self.assertNotIn("sensitive-access-token", str(raised.exception))

    def test_account_summaries_pages_only_to_limit(self):
        calls = []
        responses = [
            ({"accountSummaries": [{"account": "accounts/1"}], "nextPageToken": "next"}),
            ({"accountSummaries": [{"account": "accounts/2"}], "nextPageToken": "more"}),
        ]

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            calls.append(params)
            return responses.pop(0)

        with patch.object(self.module, "api_request", side_effect=fake_request):
            rows, truncated = self.module.account_summaries("token", 2)
        self.assertEqual([row["account"] for row in rows], ["accounts/1", "accounts/2"])
        self.assertTrue(truncated)
        self.assertEqual(calls[1]["pageToken"], "next")

    def test_account_summaries_stops_on_an_empty_page_with_a_token(self):
        response = {"accountSummaries": [], "nextPageToken": "next"}
        with patch.object(self.module, "api_request", return_value=response) as request:
            rows, truncated = self.module.account_summaries("token", 5)
        self.assertEqual([], rows)
        self.assertTrue(truncated)
        request.assert_called_once()

    def test_accounts_emits_normalized_rows(self):
        args = SimpleNamespace(profile="example", limit=25, json=True)
        summaries = [
            {
                "account": "accounts/123",
                "displayName": "Example account",
                "propertySummaries": [{"property": "properties/456"}],
            }
        ]
        output = io.StringIO()
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(self.module, "account_summaries", return_value=(summaries, False)), redirect_stdout(output):
            self.module.command_accounts(args)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload[0]["account_id"], "123")
        self.assertEqual(payload[0]["property_count"], 1)

    def test_properties_filters_one_account_and_bounds_rows(self):
        args = SimpleNamespace(profile="example", account="123", limit=1, json=True)
        summaries = [
            {
                "account": "accounts/123",
                "propertySummaries": [
                    {"property": "properties/10", "displayName": "One", "propertyType": "PROPERTY_TYPE_ORDINARY", "parent": "accounts/123"},
                    {"property": "properties/11", "displayName": "Two", "propertyType": "PROPERTY_TYPE_ORDINARY", "parent": "accounts/123"},
                ],
            },
            {"account": "accounts/999", "propertySummaries": [{"property": "properties/99"}]},
        ]
        output, errors = io.StringIO(), io.StringIO()
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(self.module, "account_summaries", return_value=(summaries, False)), redirect_stdout(output), redirect_stderr(errors):
            self.module.command_properties(args)
        self.assertEqual(json.loads(output.getvalue())[0]["property_id"], "10")
        self.assertIn("truncated", errors.getvalue())

    def test_report_builds_bounded_data_api_request(self):
        args = SimpleNamespace(
            profile="example", property="456", start_date="28daysAgo", end_date="today",
            metrics="sessions,activeUsers", dimensions="date", limit=25, json=True,
        )
        captured = {}

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            captured.update({"method": method, "url": url, "payload": payload})
            return {
                "rowCount": 1,
                "rows": [{"dimensionValues": [{"value": "20260817"}], "metricValues": [{"value": "12"}, {"value": "9"}]}],
            }

        output = io.StringIO()
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(self.module, "api_request", side_effect=fake_request), redirect_stdout(output):
            self.module.command_report(args)
        self.assertTrue(captured["url"].endswith("properties/456:runReport"))
        self.assertEqual(captured["payload"]["limit"], "25")
        self.assertEqual(json.loads(output.getvalue())[0]["sessions"], "12")

    def test_report_refuses_an_invalid_row_count(self):
        args = SimpleNamespace(
            profile="example", property="123", start_date="28daysAgo", end_date="today",
            metrics="sessions", dimensions="date", limit=2, json=False,
        )
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "api_request", return_value={"rows": [], "rowCount": None}
        ), redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(self.module.AnalyticsError, "invalid row count"):
                self.module.command_report(args)

    def test_realtime_uses_realtime_endpoint(self):
        args = SimpleNamespace(profile="example", property="456", metrics="activeUsers", dimensions="", limit=10, json=True)
        captured = {}

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            captured["url"] = url
            return {"rowCount": 0, "rows": []}

        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(self.module, "api_request", side_effect=fake_request), redirect_stdout(io.StringIO()):
            self.module.command_realtime(args)
        self.assertTrue(captured["url"].endswith("properties/456:runRealtimeReport"))

    def test_malformed_json_is_reported_without_a_traceback(self):
        for body in (b"<html>not json</html>", b"\xff\xfe not utf-8"):
            with self.subTest(body=body):
                with patch.object(self.module, "open_url", return_value=RawResponse(body)):
                    with self.assertRaisesRegex(self.module.AnalyticsError, "not valid JSON"):
                        self.module.api_request("token", "GET", self.module.ADMIN_BASE + "/accountSummaries")

    def test_non_object_api_and_token_responses_are_refused(self):
        for body in (b"[]", b'"text"', b"7", b"null"):
            with self.subTest(body=body):
                with patch.object(self.module, "open_url", return_value=RawResponse(body)):
                    with self.assertRaisesRegex(self.module.AnalyticsError, "malformed API response"):
                        self.module.api_request("token", "GET", self.module.ADMIN_BASE + "/accountSummaries")

    def test_account_summaries_refuse_wrong_collection_and_object_shapes(self):
        cases = (
            ({"accountSummaries": {"account": "accounts/1"}}, "account summary collection"),
            ({"accountSummaries": ["accounts/1"]}, "malformed account summary"),
            ({"accountSummaries": [], "nextPageToken": {"token": "next"}}, "malformed page token"),
        )
        for response, expected in cases:
            with self.subTest(response=response):
                with patch.object(self.module, "api_request", return_value=response):
                    with self.assertRaisesRegex(self.module.AnalyticsError, expected):
                        self.module.account_summaries("token", 5)

    def test_report_refuses_wrong_row_and_value_shapes(self):
        cases = (
            ({"rows": {"dimensionValues": []}}, "report row collection"),
            ({"rows": ["20260817"]}, "malformed report row"),
            ({"rows": [{"dimensionValues": "20260817"}]}, "report dimension value collection"),
            ({"rows": [{"dimensionValues": ["20260817"]}]}, "malformed report dimension value"),
            ({"rows": [{"dimensionValues": [], "metricValues": ["12"]}]}, "malformed report metric value"),
        )
        for response, expected in cases:
            with self.subTest(response=response):
                with self.assertRaisesRegex(self.module.AnalyticsError, expected):
                    self.module.normalized_report(response, ["date"], ["sessions"], self.access, "456")

    def test_non_string_resource_identifiers_are_refused(self):
        with self.assertRaises(self.module.AnalyticsError):
            self.module.resource_id({"account": 1}, "accounts")

    def test_malformed_response_exits_two_instead_of_raising(self):
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "open_url", return_value=RawResponse(b"<html>not json</html>")
        ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as error:
            code = self.module.main(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("not valid JSON", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())

    def test_invalid_property_and_excessive_limits_are_refused(self):
        with self.assertRaises(self.module.AnalyticsError):
            self.module.resource_id("not-an-id", "properties")
        with self.assertRaises(self.module.AnalyticsError):
            self.module.bounded_limit(10001)

    def test_launcher_help_resolves_outside_repository(self):
        completed = subprocess.run(
            [str(LAUNCHER), "--help"], cwd="/tmp", env={"PATH": os.environ.get("PATH", "")},
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Google Analytics", completed.stdout)



class ReportFamilyTest(unittest.TestCase):
    """Exact request shapes for the traffic, audience, key-event, and commerce reports."""

    def setUp(self):
        self.module = load_module()
        self.access = StubAccess()

    def run_report(self, handler, response=None, **overrides):
        args = SimpleNamespace(
            profile="example",
            property="456",
            start_date="28daysAgo",
            end_date="today",
            limit=25,
            json=True,
            scope="session",
            event=None,
            purchased_only=False,
        )
        for key, value in overrides.items():
            setattr(args, key, value)
        captured = {}
        body = {"rowCount": 0, "rows": []} if response is None else response

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            captured.update({"token": token, "method": method, "url": url, "payload": payload})
            return body

        output, errors = io.StringIO(), io.StringIO()
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(self.module, "api_request", side_effect=fake_request), redirect_stdout(
            output
        ), redirect_stderr(errors):
            handler(args)
        return captured, output.getvalue(), errors.getvalue()

    def test_traffic_sends_the_documented_session_acquisition_request(self):
        captured, _, _ = self.run_report(self.module.command_traffic, breakdown="channel")
        self.assertEqual("POST", captured["method"])
        self.assertTrue(captured["url"].endswith("properties/456:runReport"))
        self.assertEqual(
            {
                "dateRanges": [{"startDate": "28daysAgo", "endDate": "today"}],
                "dimensions": [{"name": "sessionDefaultChannelGroup"}],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "activeUsers"},
                    {"name": "newUsers"},
                    {"name": "engagedSessions"},
                    {"name": "engagementRate"},
                    {
                        "name": "averageEngagementTimePerSession",
                        "expression": "userEngagementDuration/sessions",
                    },
                    {"name": "keyEvents"},
                    {"name": "totalRevenue"},
                ],
                "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
                "limit": "25",
            },
            captured["payload"],
        )

    def test_traffic_scope_selects_first_user_attribution_names(self):
        captured, _, _ = self.run_report(self.module.command_traffic, breakdown="source-medium", scope="first-user")
        self.assertEqual(
            [{"name": "firstUserSource"}, {"name": "firstUserMedium"}], captured["payload"]["dimensions"]
        )

    def test_traffic_session_scope_keeps_session_attribution_names(self):
        captured, _, _ = self.run_report(self.module.command_traffic, breakdown="source-medium")
        self.assertEqual([{"name": "sessionSource"}, {"name": "sessionMedium"}], captured["payload"]["dimensions"])

    def test_a_date_breakdown_orders_by_day_rather_than_by_size(self):
        captured, _, _ = self.run_report(self.module.command_traffic, breakdown="date")
        self.assertEqual([{"dimension": {"dimensionName": "date"}, "desc": False}], captured["payload"]["orderBys"])

    def test_traffic_refuses_a_scope_the_breakdown_does_not_have(self):
        for breakdown in ("landing-page", "date"):
            with self.subTest(breakdown=breakdown):
                with self.assertRaisesRegex(self.module.AnalyticsError, "has no first-user form"):
                    self.run_report(self.module.command_traffic, breakdown=breakdown, scope="first-user")

    def test_every_offered_breakdown_resolves_to_official_field_names(self):
        cases = (
            (self.module.TRAFFIC_BREAKDOWN_CHOICES, self.module.command_traffic, {}),
            (self.module.AUDIENCE_BREAKDOWN_CHOICES, self.module.command_audience, {}),
            (self.module.KEY_EVENT_BREAKDOWN_CHOICES, self.module.command_key_events, {}),
            (self.module.COMMERCE_BREAKDOWN_CHOICES, self.module.command_commerce, {}),
        )
        for choices, handler, extra in cases:
            for breakdown in choices:
                with self.subTest(handler=handler.__name__, breakdown=breakdown):
                    captured, _, _ = self.run_report(handler, breakdown=breakdown, **extra)
                    payload = captured["payload"]
                    names = [item["name"] for item in payload["dimensions"] + payload["metrics"]]
                    self.assertTrue(names)
                    for name in names:
                        self.assertRegex(name, r"^[A-Za-z][A-Za-z0-9_]*$")
                    self.assertLessEqual(len(payload["dimensions"]), self.module.MAX_DIMENSIONS)
                    self.assertLessEqual(len(payload["metrics"]), self.module.MAX_METRICS)
                    self.assertEqual("25", payload["limit"])

    def test_traffic_table_covers_each_offered_choice_and_nothing_else(self):
        offered = {(breakdown, "session") for breakdown in self.module.TRAFFIC_BREAKDOWN_CHOICES}
        self.assertTrue(offered.issubset(set(self.module.TRAFFIC_DIMENSIONS)))
        for breakdown, scope in self.module.TRAFFIC_DIMENSIONS:
            self.assertIn(breakdown, self.module.TRAFFIC_BREAKDOWN_CHOICES)
            self.assertIn(scope, self.module.TRAFFIC_SCOPE_CHOICES)

    def test_audience_reports_the_metric_set_google_publishes_for_demographics(self):
        captured, _, _ = self.run_report(self.module.command_audience, breakdown="age")
        self.assertEqual(
            [
                {"name": "activeUsers"},
                {"name": "newUsers"},
                {"name": "engagedSessions"},
                {"name": "engagementRate"},
                {"name": "eventCount"},
                {"name": "keyEvents"},
                {"name": "totalRevenue"},
            ],
            captured["payload"]["metrics"],
        )
        # A user-scoped breakdown must not request a session-count metric Google does not
        # pair with it in its own demographic report.
        self.assertNotIn("sessions", self.module.AUDIENCE_METRICS)

    def test_audience_breakdowns_use_the_documented_demographic_dimensions(self):
        expected = {
            "audience": "audienceName",
            "country": "country",
            "region": "region",
            "city": "city",
            "language": "language",
            "device": "deviceCategory",
            "browser": "browser",
            "operating-system": "operatingSystem",
            "platform": "platform",
            "age": "userAgeBracket",
            "gender": "userGender",
        }
        for breakdown, dimension in expected.items():
            with self.subTest(breakdown=breakdown):
                captured, _, _ = self.run_report(self.module.command_audience, breakdown=breakdown)
                self.assertEqual([{"name": dimension}], captured["payload"]["dimensions"])
                self.assertNotIn("dimensionFilter", captured["payload"])
                self.assertNotIn("metricFilter", captured["payload"])

    def test_audience_warns_that_age_and_gender_are_thresholded(self):
        for breakdown in ("age", "gender"):
            with self.subTest(breakdown=breakdown):
                _, _, errors = self.run_report(self.module.command_audience, breakdown=breakdown)
                self.assertIn("aggregation thresholds", errors)
        _, _, errors = self.run_report(self.module.command_audience, breakdown="country")
        self.assertNotIn("aggregation thresholds", errors)

    def test_key_events_always_isolates_key_events(self):
        captured, _, _ = self.run_report(self.module.command_key_events, breakdown="event")
        self.assertEqual(
            {"filter": {"fieldName": "isKeyEvent", "stringFilter": {"matchType": "EXACT", "value": "true"}}},
            captured["payload"]["dimensionFilter"],
        )
        self.assertEqual([{"name": "eventName"}], captured["payload"]["dimensions"])
        self.assertEqual(
            [{"name": "keyEvents"}, {"name": "eventCount"}, {"name": "activeUsers"}, {"name": "totalRevenue"}],
            captured["payload"]["metrics"],
        )

    def test_named_events_are_matched_exactly_inside_the_key_event_filter(self):
        captured, _, _ = self.run_report(
            self.module.command_key_events, breakdown="channel", event="generate_lead, purchase"
        )
        self.assertEqual(
            {
                "andGroup": {
                    "expressions": [
                        {
                            "filter": {
                                "fieldName": "isKeyEvent",
                                "stringFilter": {"matchType": "EXACT", "value": "true"},
                            }
                        },
                        {
                            "filter": {
                                "fieldName": "eventName",
                                "inListFilter": {
                                    "values": ["generate_lead", "purchase"],
                                    "caseSensitive": True,
                                },
                            }
                        },
                    ]
                }
            },
            captured["payload"]["dimensionFilter"],
        )

    def test_invalid_or_unbounded_event_names_are_refused(self):
        for value in ("", ",", " , "):
            with self.subTest(event=value):
                with self.assertRaisesRegex(self.module.AnalyticsError, "at least one GA4 event name"):
                    self.run_report(self.module.command_key_events, breakdown="event", event=value)
        for value in ("1lead", "generate lead", "generate-lead", "a" * 41, "drop table"):
            with self.subTest(event=value):
                with self.assertRaisesRegex(self.module.AnalyticsError, "Invalid GA4 event name"):
                    self.run_report(self.module.command_key_events, breakdown="event", event=value)
        crowd = ",".join(f"event_{index}" for index in range(self.module.MAX_EVENT_FILTER_VALUES + 1))
        with self.assertRaisesRegex(self.module.AnalyticsError, "at most"):
            self.run_report(self.module.command_key_events, breakdown="event", event=crowd)

    def test_commerce_item_breakdowns_use_item_scoped_metrics(self):
        for breakdown, dimension in (
            ("item", "itemName"),
            ("item-id", "itemId"),
            ("brand", "itemBrand"),
            ("category", "itemCategory"),
            ("list", "itemListName"),
        ):
            with self.subTest(breakdown=breakdown):
                captured, _, _ = self.run_report(self.module.command_commerce, breakdown=breakdown)
                self.assertEqual([{"name": dimension}], captured["payload"]["dimensions"])
                self.assertEqual(
                    [
                        {"name": "itemsViewed"},
                        {"name": "itemsAddedToCart"},
                        {"name": "itemsCheckedOut"},
                        {"name": "itemsPurchased"},
                        {"name": "itemRevenue"},
                    ],
                    captured["payload"]["metrics"],
                )
                self.assertEqual(
                    [{"metric": {"metricName": "itemRevenue"}, "desc": True}], captured["payload"]["orderBys"]
                )

    def test_commerce_purchase_breakdowns_use_purchase_scoped_metrics(self):
        for breakdown, dimension in (("date", "date"), ("channel", "sessionDefaultChannelGroup")):
            with self.subTest(breakdown=breakdown):
                captured, _, _ = self.run_report(self.module.command_commerce, breakdown=breakdown)
                self.assertEqual([{"name": dimension}], captured["payload"]["dimensions"])
                self.assertEqual(
                    [{"name": "ecommercePurchases"}, {"name": "purchaseRevenue"}, {"name": "totalRevenue"}],
                    captured["payload"]["metrics"],
                )

    def test_purchased_only_bounds_the_metric_that_the_breakdown_measures(self):
        captured, _, _ = self.run_report(self.module.command_commerce, breakdown="item", purchased_only=True)
        self.assertEqual(
            {
                "filter": {
                    "fieldName": "itemsPurchased",
                    "numericFilter": {"operation": "GREATER_THAN", "value": {"int64Value": "0"}},
                }
            },
            captured["payload"]["metricFilter"],
        )
        captured, _, _ = self.run_report(self.module.command_commerce, breakdown="date", purchased_only=True)
        self.assertEqual("ecommercePurchases", captured["payload"]["metricFilter"]["filter"]["fieldName"])

    def test_commerce_sends_no_filter_unless_it_was_asked_for(self):
        captured, _, _ = self.run_report(self.module.command_commerce, breakdown="item")
        self.assertNotIn("metricFilter", captured["payload"])
        self.assertNotIn("dimensionFilter", captured["payload"])

    def test_new_commands_reject_unbounded_limits_and_bad_properties(self):
        for limit in (0, -1, 10001):
            with self.subTest(limit=limit):
                with self.assertRaisesRegex(self.module.AnalyticsError, "--limit must be between"):
                    self.run_report(self.module.command_traffic, breakdown="channel", limit=limit)
        with self.assertRaisesRegex(self.module.AnalyticsError, "numeric propertie?s? ID|numeric property ID"):
            self.run_report(self.module.command_audience, breakdown="country", property="not-an-id")

    def test_only_documented_date_forms_are_accepted(self):
        for value in ("2026-08-17", "today", "yesterday", "28daysAgo", "0daysAgo"):
            with self.subTest(value=value):
                self.assertEqual(value, self.module.bounded_date(value, "--start-date"))
        for value in ("", "2026/08/17", "28 days ago", "lastMonth", "today OR 1=1", "2026-08-17\n"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(self.module.AnalyticsError, "--start-date must be"):
                    self.module.bounded_date(value, "--start-date")
        with self.assertRaisesRegex(self.module.AnalyticsError, "--end-date must be"):
            self.run_report(self.module.command_traffic, breakdown="channel", end_date="whenever")

    def test_package_defined_fields_pass_the_same_validation_as_caller_fields(self):
        self.module.validated_fields(["date"], ["sessions"])
        with self.assertRaisesRegex(self.module.AnalyticsError, "At least one metric"):
            self.module.validated_fields(["date"], [])
        with self.assertRaisesRegex(self.module.AnalyticsError, "at most 9 dimensions"):
            self.module.validated_fields([f"dimension{index}" for index in range(10)], ["sessions"])
        with self.assertRaisesRegex(self.module.AnalyticsError, "Invalid Analytics field name"):
            self.module.validated_fields(["date;drop"], ["sessions"])

    def test_google_caveats_reach_the_operator(self):
        response = {
            "rowCount": 0,
            "rows": [],
            "metadata": {
                "subjectToThresholding": True,
                "dataLossFromOtherRow": True,
                "samplingMetadatas": [{"samplesReadCount": "10"}],
                "emptyReason": "No data available",
                "currencyCode": "USD",
            },
        }
        _, _, errors = self.run_report(self.module.command_commerce, breakdown="item", response=response)
        self.assertIn("aggregation thresholds", errors)
        self.assertIn("(other)", errors)
        self.assertIn("sampled", errors)
        self.assertIn("No data available", errors)
        self.assertIn("Revenue is reported in USD", errors)

    def test_currency_is_only_reported_next_to_revenue(self):
        response = {"rowCount": 0, "rows": [], "metadata": {"currencyCode": "USD"}}
        _, _, errors = self.run_report(self.module.command_key_events, breakdown="event", response=response)
        self.assertIn("totalRevenue", self.module.KEY_EVENT_METRICS)
        self.assertIn("USD", errors)
        _, _, errors = self.run_report(
            self.module.command_audience, breakdown="country", response={"rowCount": 0, "rows": [], "metadata": {}}
        )
        self.assertNotIn("Revenue is reported", errors)

    def test_malformed_report_metadata_is_refused(self):
        for metadata, expected in (
            ([], "malformed report metadata"),
            ({"samplingMetadatas": {"samplesReadCount": "10"}}, "sampling metadata collection"),
            ({"samplingMetadatas": ["10"]}, "malformed sampling metadata"),
        ):
            with self.subTest(metadata=metadata):
                response = {"rowCount": 0, "rows": [], "metadata": metadata}
                with self.assertRaisesRegex(self.module.AnalyticsError, expected):
                    self.run_report(self.module.command_traffic, breakdown="channel", response=response)

    def test_malformed_rows_are_refused_by_the_new_commands(self):
        response = {"rowCount": 1, "rows": [{"dimensionValues": "web", "metricValues": []}]}
        with self.assertRaisesRegex(self.module.AnalyticsError, "report dimension value collection"):
            self.run_report(self.module.command_audience, breakdown="device", response=response)

    def test_rows_are_normalized_and_truncation_is_reported(self):
        response = {
            "rowCount": 99,
            "rows": [
                {
                    "dimensionValues": [{"value": "Organic Search"}],
                    "metricValues": [
                        {"value": "120"},
                        {"value": "88"},
                        {"value": "31"},
                        {"value": "77"},
                        {"value": "0.64"},
                        {"value": "51.2"},
                        {"value": "4"},
                        {"value": "930.5"},
                    ],
                }
            ],
        }
        captured, output, errors = self.run_report(
            self.module.command_traffic, breakdown="channel", response=response
        )
        row = json.loads(output)[0]
        self.assertEqual("Organic Search", row["sessionDefaultChannelGroup"])
        self.assertEqual("120", row["sessions"])
        self.assertEqual("930.5", row["totalRevenue"])
        self.assertEqual("456", row["property_id"])
        self.assertEqual("example", row["profile"])
        self.assertIn("truncated", errors)

    def test_csv_output_leads_with_the_requested_dimensions(self):
        _, output, _ = self.run_report(self.module.command_commerce, breakdown="brand", json=False)
        self.assertEqual(
            "itemBrand,itemsViewed,itemsAddedToCart,itemsCheckedOut,itemsPurchased,itemRevenue,profile,property_id",
            output.splitlines()[0],
        )

    def test_existing_report_and_realtime_requests_are_unchanged(self):
        captured = {}

        def fake_request(token, method, url, params=None, payload=None, retries=2):
            captured.update({"url": url, "payload": payload})
            return {"rowCount": 0, "rows": []}

        report_args = SimpleNamespace(
            profile="example", property="456", start_date="28daysAgo", end_date="today",
            metrics="sessions,activeUsers", dimensions="date", limit=100, json=True,
        )
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(self.module, "api_request", side_effect=fake_request), redirect_stdout(io.StringIO()):
            self.module.command_report(report_args)
        self.assertEqual(
            {
                "dateRanges": [{"startDate": "28daysAgo", "endDate": "today"}],
                "metrics": [{"name": "sessions"}, {"name": "activeUsers"}],
                "limit": "100",
                "dimensions": [{"name": "date"}],
            },
            captured["payload"],
        )
        # The historical report still accepts any Google date form and adds no ordering or filter.
        report_args.start_date = "2026-01-01"
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(self.module, "api_request", side_effect=fake_request), redirect_stdout(io.StringIO()):
            self.module.command_report(report_args)
        self.assertNotIn("orderBys", captured["payload"])

        realtime_args = SimpleNamespace(
            profile="example", property="456", metrics="activeUsers", dimensions="", limit=25, json=True
        )
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(self.module, "api_request", side_effect=fake_request), redirect_stdout(io.StringIO()):
            self.module.command_realtime(realtime_args)
        self.assertTrue(captured["url"].endswith("properties/456:runRealtimeReport"))
        self.assertEqual({"metrics": [{"name": "activeUsers"}], "limit": "25"}, captured["payload"])

    def test_new_commands_never_disclose_credentials_on_failure(self):
        def forbidden():
            # A fresh body per call because urllib reads an HTTPError's stream only once.
            return urllib.error.HTTPError(
                "https://analyticsdata.googleapis.com/v1beta/properties/456:runReport",
                403, "Forbidden", {}, io.BytesIO(b'{"error":{"message":"User does not have access"}}'),
            )

        for argv in (
            ["traffic", "--property", "456"],
            ["audience", "--property", "456", "--breakdown", "age"],
            ["key-events", "--property", "456", "--event", "generate_lead"],
            ["commerce", "--property", "456", "--purchased-only"],
        ):
            with self.subTest(argv=argv[0]):
                with patch.object(
                    self.module, "selected_access", return_value=StubAccess("sensitive-access-token")
                ), patch.object(self.module, "open_url", side_effect=forbidden()), redirect_stdout(
                    io.StringIO()
                ), redirect_stderr(io.StringIO()) as errors:
                    code = self.module.main(argv + ["--limit", "5"])
                message = errors.getvalue()
                self.assertEqual(2, code)
                self.assertIn("User does not have access", message)
                for secret in ("sensitive-access-token", "Bearer"):
                    self.assertNotIn(secret, message)
                self.assertNotIn("Traceback", message)

    def test_new_commands_exit_two_on_a_malformed_body(self):
        with patch.object(self.module, "selected_access", return_value=self.access), patch.object(
            self.module, "open_url", return_value=RawResponse(b"<html>not json</html>")
        ), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
            code = self.module.main(["commerce", "--property", "456"])
        self.assertEqual(2, code)
        self.assertIn("not valid JSON", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())

    def test_new_subcommands_help_without_credentials(self):
        for command in ("traffic", "audience", "key-events", "commerce"):
            with self.subTest(command=command):
                completed = subprocess.run(
                    [str(LAUNCHER), command, "--help"], cwd="/tmp",
                    env={"PATH": os.environ.get("PATH", "")}, text=True, capture_output=True, check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                self.assertIn("--breakdown", completed.stdout)

    def test_unknown_breakdown_values_are_rejected_by_the_parser(self):
        parser = self.module.build_parser()
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            parser.parse_args(["traffic", "--property", "456", "--breakdown", "cohort"])

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
        return {"accountSummaries": [{"account": "accounts/123", "displayName": "Example account",
                                      "propertySummaries": []}]}

    def authorization(self):
        return [request.get_header("Authorization") for request in self.requests]

    # --- the protocol itself ------------------------------------------------------------------

    def test_access_is_asked_for_over_an_inherited_pipe_and_used_only_as_a_header(self):
        self.payloads = [self.accounts_payload()]
        code, out, err = self.invoke(["accounts"])
        self.assertEqual(0, code, err)
        asked = self.asked()
        self.assertEqual(1, len(asked))
        self.assertEqual(["_oauth", "access", "google", "analytics", "--response-fd"],
                         asked[0][:5])
        # The stand-in makes Rundesk's own check, so passing proves an inherited connected unnamed
        # local socket rather than 0, 1, 2, a pipe, a named socket, or a file.
        self.assertGreater(int(asked[0][5]), 2)
        self.assertEqual(["Bearer " + MANAGED_TOKEN], self.authorization())
        self.assertIn("Example account", out)

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
                with self.assertRaisesRegex(self.module.AnalyticsError, expected):
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
        with self.assertRaisesRegex(self.module.AnalyticsError, "oversized"):
            self.module.read_frame(ours, time.monotonic() + 5)

    def test_truncated_and_silent_answers_are_refused_rather_than_waited_on(self):
        ours, theirs = self.pair()
        theirs.sendall(struct.pack(">I", 64) + b"{")
        theirs.close()
        with self.assertRaisesRegex(self.module.AnalyticsError, "closed the Google response"):
            self.module.read_frame(ours, time.monotonic() + 5)
        quiet, _held = self.pair()
        with self.assertRaisesRegex(self.module.AnalyticsError, "in time"):
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
            ["_oauth", "access", "google", "analytics", "--profile", "acme",
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
