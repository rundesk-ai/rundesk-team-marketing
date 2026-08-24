#!/usr/bin/env python3
"""Offline tests for google-auth: the provider it declares and the bridge it speaks."""

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
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "google-auth.py"
LAUNCHER = HERE.parent / "google-auth"
DECLARED = HERE.parent.parent / "oauth-provider.json"
#: Exactly the keys Rundesk's schema 1 validator accepts, and the parameters it reserves.
FIELDS = {"schema", "provider", "display_name", "authorization_endpoint", "token_endpoint",
          "identity_endpoint", "base_scopes", "identity", "authorization_parameters",
          "client_secret", "capabilities"}
RESERVED = {"client_id", "redirect_uri", "response_type", "scope", "state", "code_challenge",
            "code_challenge_method"}


def load_module():
    spec = importlib.util.spec_from_file_location("google_auth_module", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class DeclarationTest(unittest.TestCase):
    """The declaration is data Rundesk reads, so it is checked against Rundesk's own rules."""

    def setUp(self):
        self.module = load_module()
        self.declared = json.loads(DECLARED.read_text(encoding="utf-8"))

    def test_only_the_schema_one_keys_are_declared(self):
        self.assertEqual(FIELDS, set(self.declared))
        self.assertEqual(1, self.declared["schema"])
        self.assertEqual("google", self.declared["provider"])
        self.assertEqual("Google", self.declared["display_name"])
        self.assertIsInstance(self.declared["client_secret"], bool)
        self.assertTrue(self.declared["client_secret"])

    def test_every_endpoint_is_an_official_https_url_without_credentials(self):
        for field, expected in (
            ("authorization_endpoint", "https://accounts.google.com/o/oauth2/v2/auth"),
            ("token_endpoint", "https://oauth2.googleapis.com/token"),
            ("identity_endpoint", "https://openidconnect.googleapis.com/v1/userinfo"),
        ):
            with self.subTest(field=field):
                self.assertEqual(expected, self.declared[field])

    def test_identity_names_the_three_fields_google_returns(self):
        self.assertEqual({"subject": "sub", "email": "email", "email_verified": "email_verified"},
                         self.declared["identity"])

    def test_base_scopes_are_unique_non_empty_and_minimal(self):
        scopes = self.declared["base_scopes"]
        self.assertEqual(
            ["openid", "https://www.googleapis.com/auth/userinfo.email"], scopes)
        self.assertEqual(len(scopes), len(set(scopes)))
        self.assertTrue(all(isinstance(one, str) and one.strip() for one in scopes))

    def test_authorization_parameters_never_override_the_mechanics(self):
        parameters = self.declared["authorization_parameters"]
        self.assertEqual(set(), set(parameters) & RESERVED)
        self.assertTrue(all(isinstance(key, str) and isinstance(value, str)
                            for key, value in parameters.items()))
        # A refresh token needs offline access, and picking the account is the person's decision.
        self.assertEqual("offline", parameters["access_type"])
        self.assertEqual("consent select_account", parameters["prompt"])

    def test_each_capability_is_an_identifier_naming_one_google_scope(self):
        capabilities = self.declared["capabilities"]
        self.assertEqual({"analytics", "search-console", "merchant"}, set(capabilities))
        for name, scope in capabilities.items():
            with self.subTest(capability=name):
                self.assertRegex(name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertTrue(scope.startswith("https://www.googleapis.com/auth/"))

    def test_no_client_credential_name_or_value_is_declared_anywhere(self):
        raw = DECLARED.read_text(encoding="utf-8")
        for owned_by_rundesk in ("CLIENT_ID", "CLIENT_SECRET", "client_id", "refresh_token"):
            self.assertNotIn(owned_by_rundesk, raw)


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
answer(granted)
'''.format(python=sys.executable)


MANAGED_ACCOUNT = "owner@example.test"


class GoogleAuthTest(unittest.TestCase):
    """Every command, against a stand-in Rundesk that answers the bridge as the real one does."""

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
            "accounts": {"DEFAULT": [MANAGED_ACCOUNT],
                         "ACME": ["one@example.test", "two@example.test"]},
        }

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
        with patch.dict(os.environ, self.environment(**extra), clear=True), redirect_stdout(
            out
        ), redirect_stderr(err):
            code = self.module.main(argv)
        return code, out.getvalue(), err.getvalue()

    def asked(self):
        if not self.record.exists():
            return []
        return [json.loads(line) for line in self.record.read_text(encoding="utf-8").splitlines()]

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
            code, out, err = self.invoke(["login"])
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
            code, _, err = self.invoke(["login"])
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
            code, _, err = self.invoke(["login"])
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
            code, _, err = self.invoke(["accounts"])
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
            code, _, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("in time", err)
        self.assertLess(time.monotonic() - started, 30)
        left = self.orphans(where)
        self.assertTrue(left, "the stand-in never spawned the descendant")
        for pid in left:
            self.assertTrue(self.gone(pid), "a descendant of a hung child outlived the deadline")
        self.no_child_is_left()

    def no_child_is_left(self):
        with self.assertRaises(ChildProcessError):
            os.waitpid(-1, os.WNOHANG)

    # --- the declaration this package exists to own -------------------------------------------

    def test_provider_reports_the_declaration_without_reaching_rundesk_or_google(self):
        code, out, err = self.invoke(["provider"])
        self.assertEqual(0, code, err)
        self.assertIn("provider,google", out)
        self.assertIn("https://oauth2.googleapis.com/token", out)
        self.assertIn("capability search-console,https://www.googleapis.com/auth/webmasters", out)
        self.assertEqual([], self.asked())

    def test_provider_json_is_the_declaration_itself(self):
        code, out, err = self.invoke(["provider", "--json"])
        self.assertEqual(0, code, err)
        self.assertEqual(json.loads(DECLARED.read_text(encoding="utf-8")), json.loads(out))

    def test_a_declaration_that_is_not_this_provider_is_refused(self):
        with patch.object(self.module, "DECLARATION", "nothing-here.json"):
            code, _, err = self.invoke(["provider"])
        self.assertEqual(2, code)
        self.assertIn("not readable JSON", err)

    # --- the accounts Rundesk holds -------------------------------------------------------------

    def test_accounts_asks_the_provider_neutral_bridge_for_this_provider(self):
        code, out, err = self.invoke(["accounts"])
        self.assertEqual(0, code, err)
        self.assertIn(f"default,{MANAGED_ACCOUNT},ready", out)
        asked = self.asked()
        self.assertEqual(["_oauth", "accounts", "google", "--response-fd"], asked[0][:4])
        # Rundesk refuses 0, 1, 2, a pipe, a named socket, and a file, so passing proves the socket.
        self.assertGreater(int(asked[0][4]), 2)

    def test_accounts_forwards_the_app_profile_and_lists_every_account(self):
        code, out, err = self.invoke(["accounts", "--profile", "acme"])
        self.assertEqual(0, code, err)
        self.assertIn("acme,one@example.test,ready", out)
        self.assertIn("acme,two@example.test,ready", out)
        self.assertEqual(["_oauth", "accounts", "google", "--profile", "acme"], self.asked()[0][:5])

    def test_an_app_profile_with_no_account_says_what_to_run(self):
        self.plan["accounts"] = {"DEFAULT": []}
        code, out, _ = self.invoke(["accounts"])
        self.assertEqual(0, code)
        self.assertIn("run: rundesk login google", out)

    def test_an_unconfigured_app_profile_is_shown_in_the_table_and_still_fails(self):
        """A listing that could not be made is not an empty listing, and must not exit like one."""
        code, out, err = self.invoke(["accounts", "--profile", "missing"])
        self.assertEqual(2, code)
        # The person reading the table sees the reason and the exact value to set.
        self.assertIn("GOOGLE_OAUTH_CLIENT_ID", out)
        # A script reading the exit code is not told "no accounts", and stderr says why.
        self.assertIn("GOOGLE_OAUTH_CLIENT_ID", err)

    # --- login ----------------------------------------------------------------------------------

    def test_login_runs_rundesk_and_then_shows_what_is_connected(self):
        code, out, err = self.invoke(["login", "--profile", "acme"])
        self.assertEqual(0, code, err)
        asked = self.asked()
        self.assertEqual(["login", "google", "--profile", "acme"], asked[0])
        self.assertEqual(["_oauth", "accounts", "google"], asked[1][:3])
        self.assertIn("acme,one@example.test,ready", out)

    def test_a_declined_login_is_reported_with_the_command_to_repeat(self):
        self.plan["mode"] = "login-refused"
        code, _, err = self.invoke(["login"])
        self.assertEqual(2, code)
        self.assertIn("Google login was declined", err)
        self.assertIn("rundesk login google", err)

    def test_accounts_can_sign_in_first_with_auth(self):
        code, _, err = self.invoke(["accounts", "--auth"])
        self.assertEqual(0, code, err)
        self.assertEqual(["login", "google"], self.asked()[0])

    # --- the protocol and its bounds ------------------------------------------------------------

    def test_a_pipe_is_refused_where_the_protocol_requires_a_socket(self):
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

    def test_a_frame_must_be_version_one_bounded_json(self):
        ours, theirs = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(ours.close)
        body = json.dumps({"version": 2, "ok": True}).encode()
        theirs.sendall(struct.pack(">I", len(body)) + body)
        theirs.close()
        with self.assertRaisesRegex(self.module.GoogleAuthError, "version this package cannot read"):
            self.module.read_frame(ours, time.monotonic() + 5)

    def test_a_child_that_never_answers_is_stopped_at_the_deadline_and_reported(self):
        self.plan["mode"] = "hang"
        started = time.monotonic()
        with patch.object(self.module, "BRIDGE_SECONDS", 0.3):
            code, out, err = self.invoke(["accounts"])
        self.assertEqual(2, code)
        self.assertIn("in time", out)
        self.assertIn("in time", err)
        self.assertLess(time.monotonic() - started, 30)
        self.no_child_is_left()

    def test_a_login_nobody_completes_is_stopped_at_its_own_deadline(self):
        self.plan["mode"] = "login-hang"
        with patch.object(self.module, "SIGN_IN_SECONDS", 0.3):
            code, _, err = self.invoke(["login"])
        self.assertEqual(2, code)
        self.assertIn("signing in to Google", err)
        self.no_child_is_left()

    def test_a_rundesk_without_the_bridge_says_to_update_and_sign_in(self):
        self.plan["mode"] = "old"
        code, _, err = self.invoke(["login"])
        self.assertEqual(2, code)
        self.assertIn("older than Rundesk-managed Google sign-in", err)
        self.assertIn("rundesk login google", err)

    def test_no_rundesk_at_all_is_reported_as_the_missing_install_it_is(self):
        code, _, err = self.invoke(["login"], RUNDESK_COMMAND="", PATH=str(self.home / "none"))
        self.assertEqual(2, code)
        self.assertIn("no Rundesk is reachable", err)

    # --- relocation ------------------------------------------------------------------------------

    def test_the_launcher_resolves_its_runtime_and_declaration_from_outside_the_repository(self):
        completed = subprocess.run(
            [str(LAUNCHER), "provider"], cwd="/tmp", text=True, capture_output=True, check=False,
            env={"PATH": os.environ.get("PATH", os.defpath), "HOME": "/tmp"},
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("provider,google", completed.stdout)


if __name__ == "__main__":
    unittest.main()
