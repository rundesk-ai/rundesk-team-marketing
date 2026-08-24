from __future__ import annotations

import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = Path(__file__).with_name("posthog.py")
SPEC = importlib.util.spec_from_file_location("posthog_command", MODULE_PATH)
assert SPEC and SPEC.loader
posthog = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = posthog
SPEC.loader.exec_module(posthog)


class PostHogCommandTests(unittest.TestCase):
    def profile(self) -> object:
        return posthog.Profile(
            name="example",
            api_key="phx-test-secret",
            project_id="12345",
            base_url="https://us.posthog.com",
            label="Example",
        )

    def test_rundesk_profile_precedence_and_discovery(self):
        env = {
            "POSTHOG_PERSONAL_API_KEY__ACME": "rundesk-key",
            "POSTHOG_PROJECT_ID__ACME": "123",
            "POSTHOG_ACME_KEY": "legacy-key",
            "POSTHOG_ACME_PROJECT_ID": "456",
            "POSTHOG_PERSONAL_API_KEY": "default-key",
            "POSTHOG_PROJECT_ID": "789",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(["acme"], posthog.configured_profile_names())
            self.assertEqual("rundesk-key", posthog.profile_value("acme", "POSTHOG_PERSONAL_API_KEY"))
            self.assertEqual("123", posthog.profile_value("acme", "POSTHOG_PROJECT_ID"))
            self.assertEqual("", posthog.profile_value("other", "POSTHOG_PROJECT_ID"))

    def test_named_profile_does_not_fall_back_to_plain_values(self):
        with mock.patch.dict(os.environ, {"POSTHOG_PERSONAL_API_KEY": "key", "POSTHOG_PROJECT_ID": "123"}, clear=True):
            with self.assertRaises(posthog.PostHogError):
                posthog.get_profile("another")

    def test_url_and_project_validation(self):
        self.assertEqual("https://eu.posthog.com", posthog.validate_base_url("https://eu.posthog.com/"))
        self.assertEqual("12345", posthog.validate_project_id("12345"))
        for value in ("http://example.test", "https://example.test/path", "https://user:pass@example.test"):
            with self.subTest(value=value):
                with self.assertRaises(posthog.PostHogError):
                    posthog.validate_base_url(value)
        with self.assertRaises(posthog.PostHogError):
            posthog.validate_project_id("project-name")

    def test_time_window_rejects_equal_reverse_and_too_broad_ranges(self):
        for after, before in (
            ("2026-08-01", "2026-08-01"),
            ("2026-08-02", "2026-08-01"),
            ("2025-01-01", "2026-08-01"),
        ):
            with self.subTest(after=after, before=before):
                with self.assertRaises(posthog.PostHogError):
                    posthog.validate_window(after, before)

    def test_hogql_guard_and_limit(self):
        self.assertEqual("SELECT * FROM events LIMIT 10", posthog.ensure_limit("SELECT * FROM events", 10))
        self.assertEqual(
            "WITH sample AS (SELECT * FROM events LIMIT 1) SELECT * FROM events LIMIT 10",
            posthog.ensure_limit(
                "WITH sample AS (SELECT * FROM events LIMIT 1) SELECT * FROM events", 10
            ),
        )
        with self.assertRaises(posthog.PostHogError):
            posthog.ensure_limit("SELECT * FROM events LIMIT 11", 10)
        with self.assertRaises(posthog.PostHogError):
            posthog.ensure_limit("SELECT * FROM events LIMIT 2 BY event", 10)
        self.assertEqual("SELECT 'delete'", posthog.validate_hogql("SELECT 'delete';"))
        for sql in ("DELETE FROM events", "SELECT 1; SELECT 2", "DROP TABLE events", ""):
            with self.subTest(sql=sql):
                with self.assertRaises(posthog.PostHogError):
                    posthog.validate_hogql(sql)

    def test_pagination_follows_bounded_same_origin_next(self):
        first = {"results": [{"id": "1"}], "next": "https://us.posthog.com/api/next"}
        second = {"results": [{"id": "2"}], "next": None}
        with mock.patch.object(posthog, "request", return_value=(first, {})) as initial:
            with mock.patch.object(posthog, "request_url", return_value=(second, {})) as next_page:
                rows, more = posthog.paginate(self.profile(), "projects/", {}, 2)
        self.assertEqual([{"id": "1"}, {"id": "2"}], rows)
        self.assertFalse(more)
        initial.assert_called_once()
        next_page.assert_called_once()

    def test_pagination_rejects_malformed_response_and_cross_origin_next(self):
        with mock.patch.object(posthog, "request", return_value=({"results": "bad"}, {})):
            with self.assertRaises(posthog.PostHogError):
                posthog.paginate(self.profile(), "projects/", {}, 2)
        with mock.patch.object(posthog, "request", return_value=({"results": ["bad"]}, {})):
            with self.assertRaises(posthog.PostHogError):
                posthog.paginate(self.profile(), "projects/", {}, 2)
        first = {"results": [{"id": "1"}], "next": "https://evil.example/api/next"}
        with mock.patch.object(posthog, "request", return_value=(first, {})):
            with self.assertRaises(posthog.PostHogError):
                posthog.paginate(self.profile(), "projects/", {}, 2)

    def test_transport_refuses_cross_origin_redirects_and_oversized_responses(self):
        handler = posthog.SameOriginRedirectHandler()
        request = SimpleNamespace(full_url="https://us.posthog.com/api/projects/12345/events/")
        with self.assertRaises(posthog.PostHogError):
            handler.redirect_request(
                request, None, 302, "", {}, "https://evil.example.test/capture"
            )

        class OversizedResponse:
            headers = {}

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, size):
                return b"x" * size

        with mock.patch.object(posthog, "MAX_RESPONSE_BYTES", 8):
            with mock.patch.object(posthog, "open_url", return_value=OversizedResponse()):
                with self.assertRaises(posthog.PostHogError):
                    posthog.request_url(
                        self.profile(), "GET", "https://us.posthog.com/api/projects/12345/events/"
                    )

    def test_event_filters_are_forwarded(self):
        args = SimpleNamespace(
            event="$pageview", distinct_id="visitor", person_id=None,
            after="2026-08-01", before="2026-08-02", include_person=True,
            select=["event", "timestamp"], limit=5,
        )
        with mock.patch.object(posthog, "paginate", return_value=([], False)) as paginate:
            posthog.event_records(self.profile(), args)
        params = paginate.call_args.args[2]
        self.assertEqual("$pageview", params["event"])
        self.assertEqual("2026-08-01", params["after"])
        self.assertEqual("true", params["include_person"])
        self.assertEqual(["event", "timestamp"], params["select"])

    def test_analytics_presets_cover_requested_dimensions(self):
        for mode, events in (
            ("trends", []), ("traffic", []), ("audiences", []),
            ("leads", ["lead"]), ("conversion", ["signup", "purchase"]),
        ):
            args = SimpleNamespace(mode=mode, event=events, after="2026-08-01", before="2026-08-02", days=7, limit=10)
            sql = posthog.analytics_sql(args)
            self.assertIn("FROM events", sql)
            self.assertIn("LIMIT 10", sql)
        self.assertIn("$pageview", posthog.analytics_sql(SimpleNamespace(
            mode="traffic", event=[], after="2026-08-01", before="2026-08-02", days=7, limit=10,
        )))
        with self.assertRaises(posthog.PostHogError):
            posthog.analytics_sql(SimpleNamespace(
                mode="leads", event=[], after=None, before=None, days=7, limit=10,
            ))
        self.assertIn("person.properties.email", posthog.analytics_sql(SimpleNamespace(
            mode="leads", event=["lead"], after="2026-08-01", before="2026-08-02", days=7, limit=10,
        )))
        self.assertIn("person.properties.email", posthog.analytics_sql(SimpleNamespace(
            mode="audiences", event=[], after="2026-08-01", before="2026-08-02", days=7, limit=10,
        )))
        with self.assertRaises(posthog.PostHogError):
            posthog.analytics_sql(SimpleNamespace(
                mode="traffic", event=["signup"], after="2026-08-01", before="2026-08-02", days=7, limit=10,
            ))

    def test_analytics_window_names_utc_and_normalizes_offsets(self):
        args = SimpleNamespace(
            mode="trends", event=[], after="2026-08-01T12:00:00+02:00",
            before="2026-08-02T12:00:00+0200", days=7, limit=10,
        )
        window = posthog.analytics_window(args)
        # The bound is converted to UTC and the timezone is named, because HogQL reads a bare
        # toDateTime literal in the project's timezone.
        self.assertIn("toDateTime('2026-08-01 10:00:00', 'UTC')", window)
        self.assertIn("toDateTime('2026-08-02 10:00:00', 'UTC')", window)
        self.assertNotIn("+02", window)

    def test_unsupported_timestamp_is_refused_not_raised_as_valueerror(self):
        # `fromisoformat` on the Python 3.9 floor rejects spellings the option pattern accepts.
        with self.assertRaises(posthog.PostHogError):
            posthog.timestamp_value("2026-08-01T12:00:00+99:99")
        self.assertEqual(
            "toDateTime('2026-08-01 00:00:00', 'UTC')", posthog.sql_timestamp("2026-08-01")
        )

    def test_query_payload_has_hogql_kind_name_and_limit(self):
        captured = {}

        def fake_request(profile, method, path, params=None, payload=None, retries=2):
            captured.update(method=method, path=path, payload=payload)
            return ({"columns": ["count"], "results": [[3]]}, {})

        with mock.patch.object(posthog, "request", side_effect=fake_request):
            result, more = posthog.run_hogql(
                self.profile(), "SELECT count() FROM events", 25, "trend check"
            )
        self.assertEqual([[3]], result["results"])
        self.assertFalse(more)
        self.assertEqual("POST", captured["method"])
        self.assertEqual("HogQLQuery", captured["payload"]["query"]["kind"])
        self.assertIn("LIMIT 25", captured["payload"]["query"]["query"])
        self.assertEqual("trend check", captured["payload"]["name"])

        with mock.patch.object(
            posthog,
            "request",
            return_value=({"columns": ["count"], "results": [[1], [2], [3]]}, {}),
        ):
            bounded_result, more = posthog.run_hogql(
                self.profile(), "SELECT count() FROM events", 2, "bounded check"
            )
        self.assertEqual([[1], [2]], bounded_result["results"])
        self.assertTrue(more)

    def test_query_name_respects_posthog_bound(self):
        args = SimpleNamespace(
            command="query", profile="example", all_profiles=False, json=False,
            sql="SELECT 1", name="x" * (posthog.MAX_QUERY_NAME + 1), limit=10,
        )
        with mock.patch.object(posthog, "get_profile", return_value=self.profile()):
            with self.assertRaises(posthog.PostHogError):
                posthog.run_command(args)

    def test_human_output_redacts_pii_and_url_queries(self):
        output = io.StringIO()
        with mock.patch("sys.stdout", output):
            posthog.emit_records([{
                "email": "alice@example.test",
                "ip": "203.0.113.8",
                "url": "https://example.test/landing?email=alice@example.test&token=secret",
            }], ("email", "ip", "url"), "example")
        rendered = output.getvalue()
        self.assertNotIn("203.0.113.8", rendered)
        self.assertNotIn("token=secret", rendered)
        self.assertIn("a***@example.test", rendered)

    def test_launcher_help_and_profiles_are_credential_free(self):
        launcher = MODULE_PATH.parents[1] / "posthog"
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""}
        help_result = subprocess.run([str(launcher), "--help"], env=env, text=True, capture_output=True)
        self.assertEqual(0, help_result.returncode, help_result.stderr)
        profile_result = subprocess.run([str(launcher), "profiles"], env=env, text=True, capture_output=True)
        self.assertEqual(0, profile_result.returncode, profile_result.stderr)
        self.assertIn("No PostHog profiles", profile_result.stdout)

    def test_explicit_env_file_is_loaded_after_credential_free_parsing(self):
        with tempfile.TemporaryDirectory() as temporary:
            env_file = Path(temporary) / "posthog.env"
            env_file.write_text(
                "POSTHOG_PERSONAL_API_KEY=synthetic-key\nPOSTHOG_PROJECT_ID=12345\n",
                encoding="utf-8",
            )
            env_file.chmod(0o600)
            output = io.StringIO()
            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch("sys.stdout", output):
                    self.assertEqual(
                        0,
                        posthog.main(["--env-file", str(env_file), "profiles", "--json"]),
                    )
            self.assertIn('"profile": "default"', output.getvalue())

    def test_web_text_names_profile(self):
        web_args = SimpleNamespace(
            command="web", profile="example", all_profiles=False, json=False,
            days=7, compare=True,
        )
        output = io.StringIO()
        with mock.patch.object(posthog, "get_profile", return_value=self.profile()):
            with mock.patch.object(posthog, "web_analytics", return_value={"visitors": 3}):
                with mock.patch("sys.stdout", output):
                    self.assertEqual(0, posthog.run_command(web_args))
        self.assertIn("profile=example", output.getvalue())

    def test_malformed_insight_is_refused(self):
        insight_args = SimpleNamespace(
            command="insight", profile="example", all_profiles=False, json=False,
            insight_id="abc",
        )
        with mock.patch.object(posthog, "get_profile", return_value=self.profile()):
            with mock.patch.object(posthog, "request", return_value=([], {})):
                with self.assertRaises(posthog.PostHogError):
                    posthog.run_command(insight_args)


if __name__ == "__main__":
    unittest.main()
