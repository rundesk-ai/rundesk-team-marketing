#!/usr/bin/env python3
"""Bounded Google Search Console reads and one guarded sitemap submission."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zoneinfo
from typing import Any, Callable


WEBMASTERS_API = "https://www.googleapis.com/webmasters/v3"
INSPECTION_API = "https://searchconsole.googleapis.com/v1"
# Search Console buckets every row by Pacific day, so complete-day defaults must use that zone.
PACIFIC_ZONE = "America/Los_Angeles"
# sitemaps.submit is the only writing method in this package, and it needs the full scope rather
# than webmasters.readonly. Rundesk attaches this one to every token it grants here, so submission
# is never a separate authorization step.
SUBMIT_SCOPE = "https://www.googleapis.com/auth/webmasters"
FILTER_DIMENSIONS = ("query", "page", "country", "device", "searchAppearance")
FILTER_OPERATORS = ("contains", "equals", "notContains", "notEquals", "includingRegex", "excludingRegex")
# Only these two compare the whole dimension value, so only these two can be safely canonicalized.
EXACT_OPERATORS = ("equals", "notEquals")
DEVICE_VALUES = ("DESKTOP", "MOBILE", "TABLET")
COUNTRY_CODE_RE = re.compile(r"[A-Za-z]{3}")
# Google publishes no expression limit; this bound keeps a mistyped argument out of the request.
MAX_EXPRESSION = 4096


class SearchConsoleError(RuntimeError):
    pass


class PacificFallback(dt.tzinfo):
    """US Pacific rules in force since 2007, used only where no IANA database is installed.

    Converting a UTC instant reproduces the IANA wall clock exactly. Like the tzinfo example in
    Python's own documentation, it cannot name the repeated hour at the autumn transition, which
    does not matter here because only the resulting Pacific date is ever read.
    """

    def utcoffset(self, value: dt.datetime | None) -> dt.timedelta:
        return dt.timedelta(hours=-7) if self._is_daylight(value) else dt.timedelta(hours=-8)

    def dst(self, value: dt.datetime | None) -> dt.timedelta:
        return dt.timedelta(hours=1) if self._is_daylight(value) else dt.timedelta(0)

    def tzname(self, value: dt.datetime | None) -> str:
        return "PDT" if self._is_daylight(value) else "PST"

    @staticmethod
    def _is_daylight(value: dt.datetime | None) -> bool:
        if value is None:
            return False
        # utcoffset minus dst is a constant -8 hours, so tzinfo.fromutc hands this rule a local
        # standard-time value, which is the frame the statute defines the transitions in.
        local = value.replace(tzinfo=None)
        march = dt.datetime(local.year, 3, 1)
        november = dt.datetime(local.year, 11, 1)
        begins = march + dt.timedelta(days=7 + (6 - march.weekday()) % 7, hours=2)
        ends = november + dt.timedelta(days=(6 - november.weekday()) % 7, hours=1)
        return begins <= local < ends


def pacific_zone() -> dt.tzinfo:
    try:
        return zoneinfo.ZoneInfo(PACIFIC_ZONE)
    except zoneinfo.ZoneInfoNotFoundError:
        return PacificFallback()


def utc_now() -> dt.datetime:
    """The single clock reading, isolated so tests can freeze a Pacific-day boundary."""
    return dt.datetime.now(dt.timezone.utc)


def pacific_today() -> dt.date:
    return utc_now().astimezone(pacific_zone()).date()


# --- Rundesk-managed Google sign-in -------------------------------------------------------------
#
# Rundesk owns the OAuth client, the browser, the refresh token, and where those are kept. This
# package owns none of it and asks the install's own CLI for one short-lived access token, which
# arrives over one connected unnamed local socket held by nothing but these two processes rather
# than through argv, the environment, stdout, or a file. The wire format is Rundesk's hidden
# `_oauth` bridge, version 1. Rundesk refuses a pipe, a named socket, a regular file, and 0, 1, 2.
COMMAND_VARIABLE = "RUNDESK_COMMAND"
BRIDGE = "_oauth"
# Which OAuth provider Rundesk signs in to. What that name means — Google's endpoints, identity
# fields, and the scope each capability carries — is declared by this catalog's `google-auth`
# package, which this one reads nothing from and never runs.
PROVIDER = "google"
# The capability this package asks for. Rundesk turns it into the scope the provider declares, so no
# scope is chosen here.
CAPABILITY = "search-console"
BRIDGE_VERSION = 1
MAX_FRAME = 65536
# One bound for a whole child, not for each step of one: a request that spends its time reading a
# frame has that much less left to be waited on. Rundesk gives a person 180 seconds at the browser
# when a grant has to be widened, and its own calls to Google time out at 30, so this covers every
# phase and still ends.
BRIDGE_SECONDS = 300
# `rundesk login google` waits on a person at the browser first and on Google afterwards, so its
# bound is larger than the bridge's. It is still finite: a login nobody completes is stopped rather
# than left holding this command open.
SIGN_IN_SECONDS = 420
# Rundesk's own words about signing in belong beside this command's other diagnostics, never in the
# rows a caller parses.
#: How long a stopped child and its group get to actually go. Bounded like everything else here:
#: the point of this window is to end a wait, so it may not become one.
STOP_SECONDS = 5.0

#: How long an already-finished child's abandoned pipe is given to yield what it has. Short on
#: purpose: reaching that path means something else is holding the pipe open, so this is a grace
#: for bytes already in flight, never a wait for a writer nobody here owns.
LINGER_SECONDS = 0.2

#: The most partial output that is ever carried out of an abandoned pipe. A refusal is one line;
#: this is room for context and a bound on a writer nobody here owns.
MAX_SAID = 65536

DIAGNOSTIC_FD = 2
# A Rundesk released before this bridge answers as argparse does: exit 2, naming the choice it did
# not recognize. Rundesk's own refusals exit 1, so the two are never mistaken for each other.
UNSUPPORTED_EXIT = 2
UNSUPPORTED_MARKS = ("invalid choice: '_oauth'", "invalid choice: 'login'",
                     "invalid choice: 'google'", "unrecognized arguments")
MAX_REASON = 400


def login_command(profile: str) -> str:
    """The exact command that connects a Google account for one OAuth app profile."""
    return "rundesk login google" + (f" --profile {profile}" if profile else "")


def rundesk_command() -> str:
    """The rundesk this install means, which is a whole path and is not always on PATH."""
    command = os.environ.get(COMMAND_VARIABLE, "").strip()
    if command:
        return command
    found = shutil.which("rundesk")
    if not found:
        raise SearchConsoleError(
            f"This skill signs in through Rundesk, and no Rundesk is reachable: {COMMAND_VARIABLE} "
            f"is unset and no rundesk command is on PATH. Run: {login_command('')}"
        )
    return found


def read_exactly(connection: socket.socket, wanted: int, deadline: float) -> bytes:
    """Exactly one bounded segment, refusing rather than waiting on an install that never answers."""
    held = bytearray()
    while len(held) < wanted:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SearchConsoleError("Rundesk did not answer the Google request in time.")
        connection.settimeout(remaining)
        try:
            part = connection.recv(wanted - len(held))
        except socket.timeout as exc:
            raise SearchConsoleError("Rundesk did not answer the Google request in time.") from exc
        if not part:
            raise SearchConsoleError("Rundesk closed the Google response before answering.")
        held.extend(part)
    return bytes(held)


def read_frame(connection: socket.socket, deadline: float) -> dict[str, Any]:
    """One version 1 frame: four big-endian length bytes, then that much compact UTF-8 JSON.

    `deadline` is a `time.monotonic` instant shared with the wait that follows, so reading and
    reaping cannot each spend the whole allowance.
    """
    size = struct.unpack(">I", read_exactly(connection, 4, deadline))[0]
    if size > MAX_FRAME:
        raise SearchConsoleError("Rundesk sent an oversized Google response.")
    try:
        payload = json.loads(read_exactly(connection, size, deadline).decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise SearchConsoleError("Rundesk sent a malformed Google response.") from exc
    if not isinstance(payload, dict) or payload.get("version") != BRIDGE_VERSION:
        raise SearchConsoleError("Rundesk sent a Google response version this package cannot read.")
    return payload


def framed_error(payload: dict[str, Any]) -> str:
    """The refusal Rundesk framed, bounded. A frame carrying no reason yields nothing."""
    reason = payload.get("error")
    return reason.strip()[:MAX_REASON] if isinstance(reason, str) and reason.strip() else ""


def bridge_reason(said: str) -> str:
    """Rundesk's own refusal, bounded, and never more of another program's output than that."""
    for line in said.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        head, marker, reason = stripped.partition(" — ")
        return (reason if marker and head.endswith("FAILED") else stripped)[:MAX_REASON]
    return ""


def unsupported(code: int, said: str) -> bool:
    """Whether this Rundesk predates managed sign-in rather than having refused the request."""
    return code == UNSUPPORTED_EXIT and any(mark in said for mark in UNSUPPORTED_MARKS)


def refused(code: int, said: str, profile: str, framed: str = "",
            trouble: str = "") -> SearchConsoleError:
    if unsupported(code, said):
        return SearchConsoleError(
            "This Rundesk install is older than Rundesk-managed Google sign-in. Update Rundesk, "
            f"then run: {login_command(profile)}"
        )
    # Rundesk's framed reason is its structured answer and comes first; its stderr says the same
    # thing when it could not frame one; the protocol's own complaint is the last resort.
    reason = framed or bridge_reason(said) or trouble or f"rundesk exited {code}"
    # Rundesk names the login command itself when that is the fix. Appending it again turns one
    # instruction into two identical ones, which reads as a program that has lost track of itself.
    run = login_command(profile)
    also = "" if run in reason else f" Run: {run}"
    return SearchConsoleError(
        f"Rundesk did not grant Google access: {reason}." + also
    )


def stop_group(process: subprocess.Popen) -> None:
    """Signal the child's whole process group, because a descendant is what holds the pipe open.

    Falls back to the child alone when there is no group to signal — it has already been reaped, or
    the platform does not have one. Every failure here is ignored on purpose: this runs while a
    deadline is already being enforced, and a command must not fail at the step whose whole job is
    to stop something failing.
    """
    try:
        # **`process.pid`, not `os.getpgid(process.pid)`.** Every spawn here uses
        # `start_new_session=True`, so the child *is* the group leader and its pid is the group ID,
        # known without asking anything. Asking has a race: `finished` reaches here having just
        # seen the leader alive, and the leader can exit in the moment between that look and this
        # call. `getpgid` would then raise `ESRCH` and nothing would be signalled, while the group
        # it led still holds live members. The pid does not go stale that way.
        os.killpg(process.pid, signal.SIGKILL)
        return
    except (ProcessLookupError, PermissionError, OSError, AttributeError):
        pass
    try:
        process.kill()
    except OSError:
        pass


def as_text(said: object) -> str:
    """Partial output as bounded text, whatever shape the interruption left it in.

    `TimeoutExpired` carries what had been read when it fired, and carries it as *bytes* even from
    a text-mode child, because decoding happens after the read this never got to finish. Bounded
    because nothing downstream needs more than the first refusal line, and an unbounded child
    should not decide how much of this one's memory it uses.
    """
    if said is None:
        return ""
    if isinstance(said, bytes):
        said = said.decode("utf-8", "replace")
    return said[:MAX_SAID] if isinstance(said, str) else ""


def abandoned(process: subprocess.Popen) -> str:
    """Whatever the pipe has to give in a moment, and then let go of it.

    Never waits on whatever is still holding the writing end: this is the path where that holder is
    somebody else's business, so the read is bounded and the pipe is closed rather than drained.
    """
    said = ""
    try:
        _, said = process.communicate(timeout=LINGER_SECONDS)
    except subprocess.TimeoutExpired as expired:
        # **What was read before the wait ran out is kept.** A child that exited non-zero after
        # launching a helper has already written why, and the helper is only holding the pipe open
        # afterwards; dropping that would turn Rundesk's actual refusal into `rundesk exited 1`.
        said = expired.stderr
    except (ValueError, OSError):
        said = ""
    if process.stderr is not None:
        try:
            process.stderr.close()
        except (OSError, ValueError):
            pass
    return as_text(said)


def finished(process: subprocess.Popen, deadline: float, doing: str) -> tuple[str, int]:
    """What Rundesk said and how it ended, never leaving a descendant holding this command open.

    **A pipe that never reaches end-of-file is not the same as a command that never finished**, and
    telling them apart is the whole of this. `communicate` waits for end-of-file, and Rundesk's
    sign-in opens a browser that inherits the stderr being read — so on a perfectly successful
    login the pipe stays open for as long as the person leaves the browser running.

    So when the wait runs out, the question asked is *whether the child itself is still there*:

    - **It has exited.** The sign-in is over and its exit code is the answer. Something it left
      behind holds the pipe, and that something is the person's browser — killing it would turn a
      completed sign-in into a window that vanished. The pipe is abandoned, not drained, and
      whatever stderr came back in the moment allowed is kept.
    - **It is still running.** Now it really is out of time. The whole process group is signalled —
      by the pid that *is* the group, which `start_new_session=True` guarantees — reaped under a
      bound, and refused.
    """
    try:
        _, said = process.communicate(timeout=max(0.0, deadline - time.monotonic()))
        return said or "", process.returncode
    except subprocess.TimeoutExpired:
        pass
    if process.poll() is not None:
        return abandoned(process), process.returncode
    stop_group(process)
    try:
        process.communicate(timeout=STOP_SECONDS)
    except subprocess.TimeoutExpired:
        abandoned(process)
        try:
            process.wait(timeout=STOP_SECONDS)
        except subprocess.TimeoutExpired:
            pass
    raise SearchConsoleError(f"Rundesk did not finish {doing} in time, and was stopped.")


def ask_rundesk(action: list[str], profile: str, seconds: float | None = None) -> dict[str, Any]:
    """One `_oauth` answer, read from a socket pair no other process holds an end of."""
    command = rundesk_command()
    # One deadline for the whole transaction: spawning, reading the frame, and waiting for the exit
    # share it, so a child that stalls in any one phase cannot extend the others.
    deadline = time.monotonic() + (BRIDGE_SECONDS if seconds is None else seconds)
    ours, theirs = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        try:
            process = subprocess.Popen(
                [command, BRIDGE] + action + ["--response-fd", str(theirs.fileno())],
                stdin=subprocess.DEVNULL, stdout=DIAGNOSTIC_FD, stderr=subprocess.PIPE,
                start_new_session=True,
                pass_fds=(theirs.fileno(),), text=True,
            )
        except OSError as exc:
            raise SearchConsoleError(
                f"Cannot run {command} to reach Google: {exc.strerror or exc}."
            ) from exc
        finally:
            # Rundesk holds the only other end, so its refusal closes the socket instead of leaving
            # this command waiting on an end it holds open itself.
            theirs.close()
        payload: dict[str, Any] = {}
        trouble = ""
        try:
            # Read before waiting: Rundesk writes under its own deadline, and a child blocked on
            # that write would never be reaped by a wait that came first.
            payload = read_frame(ours, deadline)
        except SearchConsoleError as exc:
            trouble = str(exc)
        said, code = finished(process, deadline, "the Google request")
    finally:
        ours.close()
    if code != 0 or payload.get("ok") is not True:
        raise refused(code, said, profile, framed_error(payload), trouble)
    return payload


def profile_action(action: list[str], profile: str) -> list[str]:
    return action + (["--profile", profile] if profile else [])


def signed_in_accounts(profile: str) -> list[str]:
    """Every Google account Rundesk holds for one OAuth app profile. Local, with no network call."""
    action = profile_action(["accounts", PROVIDER], profile)
    accounts = ask_rundesk(action, profile).get("accounts")
    if not isinstance(accounts, list) or not all(isinstance(one, str) for one in accounts):
        raise SearchConsoleError("Rundesk sent a malformed Google account list.")
    return accounts


def managed_token(profile: str, email: str) -> tuple[str, str]:
    """One short-lived token and the verified account it belongs to."""
    action = profile_action(["access", PROVIDER, CAPABILITY], profile)
    payload = ask_rundesk(action + (["--email", email] if email else []), profile)
    token, expires, who = (payload.get("access_token"), payload.get("expires_at"),
                           payload.get("email"))
    subject = payload.get("subject")
    # bool is an int, and an expiry of True would otherwise pass every check below.
    if (not isinstance(token, str) or not token or not isinstance(who, str) or not who
            or not isinstance(subject, str) or not subject
            or isinstance(expires, bool) or not isinstance(expires, int)):
        raise SearchConsoleError("Rundesk sent no usable Google access token.")
    # Bearer is the one scheme this package knows how to send, so anything else is refused rather
    # than sent as though it were one.
    if payload.get("token_type") != "Bearer":
        raise SearchConsoleError("Rundesk sent a Google access token this package cannot send.")
    if expires <= int(time.time()):
        raise SearchConsoleError(
            f"Rundesk sent an already expired Google access token. Run: {login_command(profile)}"
        )
    # **Checked here as well as inside Rundesk, and the reason is whose promise it is.** This
    # command is what told the caller which account it would use; a token for a different one would
    # read every figure out of somebody else's Google account under the address they asked for.
    # Compared case-insensitively because an address is not case-sensitive in its domain and
    # providers vary in what they echo back.
    if email and who.casefold() != email.casefold():
        raise SearchConsoleError(
            f"Rundesk returned a Google account other than {email}; no Google request was made."
        )
    return token, who


def sign_in(profile: str, seconds: float | None = None) -> None:
    """Rundesk's own public login, so the person sees the browser step and its result."""
    command = rundesk_command()
    action = ["login", "google"] + (["--profile", profile] if profile else [])
    deadline = time.monotonic() + (SIGN_IN_SECONDS if seconds is None else seconds)
    try:
        process = subprocess.Popen(
            [command] + action, stdin=subprocess.DEVNULL, stdout=DIAGNOSTIC_FD,
            stderr=subprocess.PIPE, text=True, start_new_session=True,
        )
    except OSError as exc:
        raise SearchConsoleError(
            f"Cannot run {command} to sign in to Google: {exc.strerror or exc}."
        ) from exc
    said, code = finished(process, deadline, "signing in to Google")
    if code != 0:
        raise refused(code, said, profile)


class Access:
    """A Google account Rundesk holds. This package sees a token for it and never a grant."""

    def __init__(self, profile: str, email: str) -> None:
        self.profile = profile
        self.wanted_email = email
        self.name = profile or "default"
        self.email = ""
        self._token = ""

    def token(self) -> str:
        """The one token this command uses, fetched once and kept only in memory."""
        if not self._token:
            self._token, self.email = managed_token(self.profile, self.wanted_email)
        return self._token


def listed(trouble: str) -> None:
    """Raise after a listing has been written, so the rows are seen and the exit is still earned.

    Written first and refused second on purpose: a person gets the table with the reason in it, and
    a script gets a non-zero exit instead of an empty account list it would have believed.
    """
    if trouble:
        raise SearchConsoleError(trouble)


def managed_rows(profile: str) -> tuple[list[dict[str, Any]], str]:
    """What Rundesk holds for one app profile, and why the listing is incomplete when it is.

    **Two different answers wear the same shape, and only one of them is success.** "Nothing is
    connected yet" is a true, complete listing whose next step is a login, and it exits zero. "The
    bridge could not be reached, spoke a version this package cannot read, or sent a malformed
    list" is a listing that does not know what is connected — reported as a row so a person reading
    the table sees why, *and* as a refusal so a script does not read an empty table as an empty
    account list.
    """
    named = profile or "default"
    try:
        accounts = signed_in_accounts(profile)
    except SearchConsoleError as exc:
        return [{"profile": named, "account": "", "status": str(exc)}], str(exc)
    if not accounts:
        return [{"profile": named, "account": "", "status": f"run: {login_command(profile)}"}], ""
    return [{"profile": named, "account": account, "status": "ready"}
            for account in accounts], ""


def selected_access(args: argparse.Namespace) -> Access:
    """The one Google account this command will use, named before anything is asked of Google."""
    profile = (getattr(args, "profile", "") or "").strip()
    if getattr(args, "auth", False):
        sign_in(profile)
    return Access(profile, (getattr(args, "email", "") or "").strip())


class RejectRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuse redirects so bearer tokens never cross an unexpected request boundary."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def open_url(request: urllib.request.Request, timeout: int = 30):
    return urllib.request.build_opener(RejectRedirectHandler()).open(request, timeout=timeout)


def expect_object(value: Any, noun: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SearchConsoleError(f"Google returned a malformed {noun}.")
    return value


def expect_list(container: dict[str, Any], key: str, noun: str) -> list[Any]:
    value = container.get(key, [])
    if not isinstance(value, list):
        raise SearchConsoleError(f"Google returned a malformed {noun} collection.")
    return value


def expect_objects(container: dict[str, Any], key: str, noun: str) -> list[dict[str, Any]]:
    return [expect_object(item, noun) for item in expect_list(container, key, noun)]


#: The most of a refusal body that is ever read. Google's error payloads are short, and an
#: unbounded read here lets a remote party choose how much memory this command uses.
MAX_ERROR_BODY = 65536


def safe_error(exc: urllib.error.HTTPError) -> str:
    """Google's own reason for refusing, or the status when it did not give one.

    **Two shapes, and both are real.** A Google API error is `{"error": {"message": "..."}}`. An
    OAuth token endpoint error is `{"error": "invalid_grant", "error_description": "..."}` — a
    *string* where the other shape has an object. Reaching for `.get("message")` on that string
    raises `AttributeError`, and the handler that swallowed it reported `HTTP 400` for a revoked
    grant: true, and not the thing anybody needed to read. The body is read once, bounded, and
    closed, because an `HTTPError` read twice yields nothing the second time.
    """
    try:
        raw = exc.read(MAX_ERROR_BODY)
    except OSError:
        return f"HTTP {exc.code}"
    finally:
        exc.close()
    try:
        body = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return f"HTTP {exc.code}"
    if not isinstance(body, dict):
        return f"HTTP {exc.code}"
    error = body.get("error")
    message = error.get("message") if isinstance(error, dict) else None
    if not message and isinstance(body.get("error_description"), str):
        message = body["error_description"]
    if not message and isinstance(error, str):
        message = error
    return str(message).strip() if message and str(message).strip() else f"HTTP {exc.code}"


def request_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, body: dict[str, Any] | None = None, opener: Callable[..., Any] | None = None) -> dict[str, Any]:
    opener = opener or open_url
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    if body is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with opener(request, timeout=30) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise SearchConsoleError(f"Google API request failed: {safe_error(exc)}.") from exc
    except urllib.error.URLError as exc:
        raise SearchConsoleError(f"Google API request failed: {exc.reason}") from exc
    if not payload:
        return {}
    try:
        decoded = json.loads(payload)
    except ValueError as exc:
        raise SearchConsoleError("Google API returned invalid JSON.") from exc
    # A list or scalar body would otherwise surface as an attribute error several frames later.
    return expect_object(decoded, "API response")


def api(access: Access, path: str, *, base: str = WEBMASTERS_API, method: str = "GET", body: dict[str, Any] | None = None) -> dict[str, Any]:
    # The token is a header value and nothing else: never a query parameter, an argument, a variable
    # in this process's environment, or anything written down.
    return request_json(base + path, method=method, headers={"Authorization": f"Bearer {access.token()}"}, body=body)


def write_rows(rows: list[dict[str, Any]], columns: list[str], as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    sys.stdout.write(output.getvalue())


def bounded(items: list[Any], limit: int, noun: str) -> list[Any]:
    if len(items) > limit:
        print(f"WARNING: {noun} output truncated to {limit} results.", file=sys.stderr)
    return items[:limit]


def cmd_profiles(args: argparse.Namespace) -> None:
    """Which Google accounts Rundesk holds for one OAuth app profile, without asking Google."""
    profile = (args.profile or "").strip()
    if args.auth:
        sign_in(profile)
    rows, trouble = managed_rows(profile)
    write_rows(rows, ["profile", "account", "status"], args.json)
    listed(trouble)



def cmd_sites(args: argparse.Namespace) -> None:
    access = selected_access(args)
    entries = expect_objects(api(access, "/sites"), "siteEntry", "site entry")
    rows = [{"site": item.get("siteUrl", ""), "permission": item.get("permissionLevel", ""), "profile": access.name} for item in bounded(entries, args.limit, "sites")]
    write_rows(rows, ["site", "permission", "profile"], args.json)


def date_range(args: argparse.Namespace) -> tuple[str, str]:
    if bool(args.start_date) != bool(args.end_date):
        raise SearchConsoleError("Use both --start-date and --end-date, or neither.")
    if args.start_date:
        try:
            start, end = dt.date.fromisoformat(args.start_date), dt.date.fromisoformat(args.end_date)
        except ValueError as exc:
            raise SearchConsoleError("Dates must use YYYY-MM-DD.") from exc
        if start > end:
            raise SearchConsoleError("--start-date must not be after --end-date.")
        return start.isoformat(), end.isoformat()
    end = pacific_today() - dt.timedelta(days=1)
    return (end - dt.timedelta(days=args.days - 1)).isoformat(), end.isoformat()


def canonical_expression(dimension: str, operator: str, expression: str) -> str:
    """Case-correct the closed-vocabulary dimensions Google matches exactly.

    A country or device value in the wrong case matches nothing and returns an empty, entirely
    plausible report. Substring and regex expressions are the caller's own pattern and are sent
    verbatim, as is searchAppearance, whose vocabulary Google extends without notice.
    """
    if operator not in EXACT_OPERATORS:
        return expression
    if dimension == "country":
        if not COUNTRY_CODE_RE.fullmatch(expression):
            raise SearchConsoleError(
                f"--filter country:{operator} needs a three-letter ISO 3166-1 alpha-3 code such as usa."
            )
        return expression.lower()
    if dimension == "device":
        if expression.upper() not in DEVICE_VALUES:
            raise SearchConsoleError(
                f"--filter device:{operator} must be one of: " + ", ".join(DEVICE_VALUES) + "."
            )
        return expression.upper()
    return expression


def parse_filter(value: str) -> dict[str, str]:
    """One --filter argument as Google's ApiDimensionFilter object."""
    # Split twice only, so a page or query expression may contain its own colons.
    parts = value.split(":", 2)
    if len(parts) != 3:
        raise SearchConsoleError(
            f"--filter {value!r} must be DIMENSION:OPERATOR:EXPRESSION, such as query:contains:running shoes."
        )
    dimension, operator, expression = parts
    if dimension not in FILTER_DIMENSIONS:
        raise SearchConsoleError(
            f"--filter dimension {dimension!r} must be one of: " + ", ".join(FILTER_DIMENSIONS) + "."
        )
    if operator not in FILTER_OPERATORS:
        raise SearchConsoleError(
            f"--filter operator {operator!r} must be one of: " + ", ".join(FILTER_OPERATORS) + "."
        )
    if not expression:
        raise SearchConsoleError(f"--filter {dimension}:{operator} needs a non-empty expression.")
    if len(expression) > MAX_EXPRESSION:
        raise SearchConsoleError(
            f"--filter expression for {dimension} exceeds {MAX_EXPRESSION} characters."
        )
    return {
        "dimension": dimension,
        "operator": operator,
        "expression": canonical_expression(dimension, operator, expression),
    }


def dimension_filter_groups(values: list[str]) -> list[dict[str, Any]]:
    """Every requested filter as the one filter group Google's request body accepts.

    Google ANDs separate groups together and documents only the "and" group type, so a single
    group already expresses every combination this CLI can build.
    """
    if not values:
        return []
    return [{"groupType": "and", "filters": [parse_filter(value) for value in values]}]


def cmd_performance(args: argparse.Namespace) -> None:
    # Parsed before configuration so a malformed filter is reported as one, not as a missing profile.
    groups = dimension_filter_groups(args.filter)
    access = selected_access(args)
    start, end = date_range(args)
    body: dict[str, Any] = {"startDate": start, "endDate": end, "rowLimit": args.limit, "startRow": 0}
    if args.dimension:
        body["dimensions"] = args.dimension
    if args.search_type:
        body["type"] = args.search_type
    # Omitted entirely when unfiltered, so an unfiltered query keeps its previous request body.
    if groups:
        body["dimensionFilterGroups"] = groups
    path = "/sites/" + urllib.parse.quote(args.site, safe="") + "/searchAnalytics/query"
    items = expect_objects(api(access, path, method="POST", body=body), "rows", "performance row")
    if len(items) == args.limit:
        print(
            f"WARNING: performance output reached the {args.limit}-row limit and may be truncated.",
            file=sys.stderr,
        )
    rows = []
    for item in items:
        row = {dimension: value for dimension, value in zip(args.dimension, expect_list(item, "keys", "performance row key"))}
        row.update({"clicks": item.get("clicks", 0), "impressions": item.get("impressions", 0), "ctr": item.get("ctr", 0), "position": item.get("position", 0), "profile": access.name})
        rows.append(row)
    write_rows(rows, args.dimension + ["clicks", "impressions", "ctr", "position", "profile"], args.json)


def cmd_inspect(args: argparse.Namespace) -> None:
    access = selected_access(args)
    response = api(access, "/urlInspection/index:inspect", base=INSPECTION_API, method="POST", body={"inspectionUrl": args.url, "siteUrl": args.site, "languageCode": "en-US"})
    result = response.get("inspectionResult")
    index = result.get("indexStatusResult") if isinstance(result, dict) else None
    if not isinstance(index, dict) or not index:
        raise SearchConsoleError("Google returned no URL inspection result for the requested URL.")
    row = {"url": args.url, "verdict": index.get("verdict", ""), "coverage_state": index.get("coverageState", ""), "indexing_state": index.get("indexingState", ""), "last_crawl": index.get("lastCrawlTime", ""), "robots_state": index.get("robotsTxtState", ""), "google_canonical": index.get("googleCanonical", ""), "user_canonical": index.get("userCanonical", ""), "profile": access.name}
    write_rows([row], list(row), args.json)


def cmd_sitemaps(args: argparse.Namespace) -> None:
    access = selected_access(args)
    path = "/sites/" + urllib.parse.quote(args.site, safe="") + "/sitemaps"
    items = expect_objects(api(access, path), "sitemap", "sitemap entry")
    rows = [{"path": item.get("path", ""), "type": item.get("type", ""), "submitted": item.get("lastSubmitted", ""), "downloaded": item.get("lastDownloaded", ""), "pending": item.get("isPending", False), "warnings": item.get("warnings", 0), "errors": item.get("errors", 0), "profile": access.name} for item in bounded(items, args.limit, "sitemaps")]
    write_rows(rows, ["path", "type", "submitted", "downloaded", "pending", "warnings", "errors", "profile"], args.json)


def sitemap_path(site: str, sitemap: str) -> str:
    """The sitemaps.submit and sitemaps.get path for one sitemap.

    Both segments carry a whole URL, so neither may keep the slashes and colon that would otherwise
    split it across path segments.
    """
    return "/sites/" + urllib.parse.quote(site, safe="") + "/sitemaps/" + urllib.parse.quote(sitemap, safe="")


def validated_sitemap(site: str, sitemap: str) -> str:
    parsed = urllib.parse.urlparse(sitemap)
    if (
        parsed.scheme not in ("http", "https")
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise SearchConsoleError(
            "--sitemap must be an absolute http or https URL without credentials, "
            "such as https://www.example.test/sitemap.xml."
        )
    # A URL-prefix property only contains sitemaps below its own prefix; a domain property covers
    # every host it verifies, so only the prefix form can be checked before spending the request.
    if site.startswith(("http://", "https://")) and not sitemap.startswith(site):
        print(
            f"WARNING: {sitemap} is outside the property {site}; Google rejects a sitemap the property does not contain.",
            file=sys.stderr,
        )
    return sitemap


def cmd_submit_sitemap(args: argparse.Namespace) -> None:
    access = selected_access(args)
    sitemap = validated_sitemap(args.site, args.sitemap)
    path = sitemap_path(args.site, sitemap)
    if not args.confirm:
        # The preview resolves only local configuration; it must not reach Google at all, so no
        # token refresh and no API call may happen before this returns.
        row = {
            "site": args.site,
            "path": sitemap,
            "method": "PUT",
            "url": WEBMASTERS_API + path,
            "scope": SUBMIT_SCOPE,
            "state": "preview",
            "profile": access.name,
        }
        write_rows([row], list(row), args.json)
        raise SearchConsoleError("Refusing to submit without --confirm; the preview above changed nothing.")
    # Google answers the submission with an empty body, so success is only established by reading
    # the sitemap back rather than by the absence of an HTTP error.
    api(access, path, method="PUT")
    entry = expect_object(api(access, path), "sitemap entry")
    recorded = entry.get("path", "")
    if not isinstance(recorded, str) or not recorded:
        raise SearchConsoleError(
            "Google accepted the submission but did not return the sitemap; verify it in Search Console."
        )
    if recorded != sitemap:
        print(f"WARNING: Google recorded the sitemap as {recorded}.", file=sys.stderr)
    row = {
        "site": args.site,
        "path": recorded,
        "type": entry.get("type", ""),
        "submitted": entry.get("lastSubmitted", ""),
        "downloaded": entry.get("lastDownloaded", ""),
        "pending": entry.get("isPending", False),
        "warnings": entry.get("warnings", 0),
        "errors": entry.get("errors", 0),
        "state": "submitted",
        "profile": access.name,
    }
    write_rows([row], list(row), args.json)


def parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--json", action="store_true")
    profile = argparse.ArgumentParser(add_help=False)
    profile.add_argument("--profile", help="Which Google OAuth app profile Rundesk signed in with")
    profile.add_argument("--email", help="Which signed-in Google account to use when Rundesk holds more than one")
    profile.add_argument("--auth", action="store_true", help="Run `rundesk login google` first, with --profile when given")
    result = argparse.ArgumentParser(prog="google-search-console", description="Read bounded Google Search Console evidence and submit a sitemap on explicit confirmation.")
    subs = result.add_subparsers(dest="command", required=True)
    p = subs.add_parser("profiles", parents=[parent], help="List the Google accounts Rundesk holds, without contacting Google.")
    p.add_argument("--profile", help="OAuth app profile to list Rundesk's signed-in accounts for")
    p.add_argument("--auth", action="store_true", help="Run `rundesk login google` first, with --profile when given")
    p.set_defaults(func=cmd_profiles)
    p = subs.add_parser("sites", parents=[parent, profile], help="List accessible Search Console properties.")
    p.add_argument("--limit", type=int, default=25)
    p.set_defaults(func=cmd_sites)
    p = subs.add_parser("performance", parents=[parent, profile], help="Query aggregated organic search performance.")
    p.add_argument("--site", required=True)
    p.add_argument("--days", type=int, default=28)
    p.add_argument("--start-date")
    p.add_argument("--end-date")
    p.add_argument("--dimension", action="append", choices=["date", "country", "device", "page", "query", "searchAppearance"], default=[])
    p.add_argument("--search-type", choices=["web", "image", "video", "news", "discover", "googleNews"])
    p.add_argument(
        "--filter", action="append", default=[], metavar="DIMENSION:OPERATOR:EXPRESSION",
        help="Repeatable Search Analytics filter; a row must match every filter given.",
    )
    p.add_argument("--limit", type=int, default=25)
    p.set_defaults(func=cmd_performance)
    p = subs.add_parser("inspect-url", parents=[parent, profile], help="Inspect Google's indexed state for one URL.")
    p.add_argument("--site", required=True)
    p.add_argument("--url", required=True)
    p.set_defaults(func=cmd_inspect)
    p = subs.add_parser("sitemaps", parents=[parent, profile], help="List submitted sitemaps for one property.")
    p.add_argument("--site", required=True)
    p.add_argument("--limit", type=int, default=25)
    p.set_defaults(func=cmd_sitemaps)
    p = subs.add_parser("submit-sitemap", parents=[parent, profile], help="Submit one sitemap to Search Console; changes Google state and requires --confirm.")
    p.add_argument("--site", required=True)
    p.add_argument("--sitemap", required=True)
    p.add_argument("--confirm", action="store_true", help="Perform the submission. Without it the command previews the request and refuses.")
    p.set_defaults(func=cmd_submit_sitemap)
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        if hasattr(args, "limit") and not 1 <= args.limit <= 1000:
            raise SearchConsoleError("--limit must be between 1 and 1000.")
        if hasattr(args, "days") and not 1 <= args.days <= 480:
            raise SearchConsoleError("--days must be between 1 and 480.")
        args.func(args)
        return 0
    except SearchConsoleError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
