#!/usr/bin/env python3
"""Read bounded Google Merchant Center account, product, issue, and performance data."""

from __future__ import annotations

import argparse
import csv
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
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


# Merchant API is versioned per sub-API, so each host path carries its own version segment.
API_HOST = "https://merchantapi.googleapis.com"
# v1 is the stable version of every sub-API this package reads. v1beta was discontinued on
# 28 February 2026 but its endpoints still answer, so the version segment is pinned here as
# a literal and is never derived from a discovery probe.
ACCOUNTS_BASE = f"{API_HOST}/accounts/v1"
PRODUCTS_BASE = f"{API_HOST}/products/v1"
REPORTS_BASE = f"{API_HOST}/reports/v1"
ISSUES_BASE = f"{API_HOST}/issueresolution/v1"
API_BASES = (ACCOUNTS_BASE, PRODUCTS_BASE, REPORTS_BASE, ISSUES_BASE)
MAX_PAGES = 100


class MerchantError(RuntimeError):
    """A safe, user-facing Merchant Center integration failure."""


def split_csv(value: str) -> List[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


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
CAPABILITY = "merchant"
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
        raise MerchantError(
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
            raise MerchantError("Rundesk did not answer the Google request in time.")
        connection.settimeout(remaining)
        try:
            part = connection.recv(wanted - len(held))
        except socket.timeout as exc:
            raise MerchantError("Rundesk did not answer the Google request in time.") from exc
        if not part:
            raise MerchantError("Rundesk closed the Google response before answering.")
        held.extend(part)
    return bytes(held)


def read_frame(connection: socket.socket, deadline: float) -> Dict[str, Any]:
    """One version 1 frame: four big-endian length bytes, then that much compact UTF-8 JSON.

    `deadline` is a `time.monotonic` instant shared with the wait that follows, so reading and
    reaping cannot each spend the whole allowance.
    """
    size = struct.unpack(">I", read_exactly(connection, 4, deadline))[0]
    if size > MAX_FRAME:
        raise MerchantError("Rundesk sent an oversized Google response.")
    try:
        payload = json.loads(read_exactly(connection, size, deadline).decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise MerchantError("Rundesk sent a malformed Google response.") from exc
    if not isinstance(payload, dict) or payload.get("version") != BRIDGE_VERSION:
        raise MerchantError("Rundesk sent a Google response version this package cannot read.")
    return payload


def framed_error(payload: Dict[str, Any]) -> str:
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
            trouble: str = "") -> MerchantError:
    if unsupported(code, said):
        return MerchantError(
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
    return MerchantError(
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


def finished(process: subprocess.Popen, deadline: float, doing: str) -> Tuple[str, int]:
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
    raise MerchantError(f"Rundesk did not finish {doing} in time, and was stopped.")


def ask_rundesk(action: List[str], profile: str, seconds: Optional[float] = None) -> Dict[str, Any]:
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
            raise MerchantError(
                f"Cannot run {command} to reach Google: {exc.strerror or exc}."
            ) from exc
        finally:
            # Rundesk holds the only other end, so its refusal closes the socket instead of leaving
            # this command waiting on an end it holds open itself.
            theirs.close()
        payload: Dict[str, Any] = {}
        trouble = ""
        try:
            # Read before waiting: Rundesk writes under its own deadline, and a child blocked on
            # that write would never be reaped by a wait that came first.
            payload = read_frame(ours, deadline)
        except MerchantError as exc:
            trouble = str(exc)
        said, code = finished(process, deadline, "the Google request")
    finally:
        ours.close()
    if code != 0 or payload.get("ok") is not True:
        raise refused(code, said, profile, framed_error(payload), trouble)
    return payload


def profile_action(action: List[str], profile: str) -> List[str]:
    return action + (["--profile", profile] if profile else [])


def signed_in_accounts(profile: str) -> List[str]:
    """Every Google account Rundesk holds for one OAuth app profile. Local, with no network call."""
    action = profile_action(["accounts", PROVIDER], profile)
    accounts = ask_rundesk(action, profile).get("accounts")
    if not isinstance(accounts, list) or not all(isinstance(one, str) for one in accounts):
        raise MerchantError("Rundesk sent a malformed Google account list.")
    return accounts


def managed_token(profile: str, email: str) -> Tuple[str, str]:
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
        raise MerchantError("Rundesk sent no usable Google access token.")
    # Bearer is the one scheme this package knows how to send, so anything else is refused rather
    # than sent as though it were one.
    if payload.get("token_type") != "Bearer":
        raise MerchantError("Rundesk sent a Google access token this package cannot send.")
    if expires <= int(time.time()):
        raise MerchantError(
            f"Rundesk sent an already expired Google access token. Run: {login_command(profile)}"
        )
    # **Checked here as well as inside Rundesk, and the reason is whose promise it is.** This
    # command is what told the caller which account it would use; a token for a different one would
    # read every figure out of somebody else's Google account under the address they asked for.
    # Compared case-insensitively because an address is not case-sensitive in its domain and
    # providers vary in what they echo back.
    if email and who.casefold() != email.casefold():
        raise MerchantError(
            f"Rundesk returned a Google account other than {email}; no Google request was made."
        )
    return token, who


def sign_in(profile: str, seconds: Optional[float] = None) -> None:
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
        raise MerchantError(
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
        raise MerchantError(trouble)


def managed_rows(profile: str) -> Tuple[List[Dict[str, Any]], str]:
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
    except MerchantError as exc:
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
    """Refuse redirects so credentials never cross an unexpected request boundary."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def open_url(request: urllib.request.Request, timeout: int = 30):
    return urllib.request.build_opener(RejectRedirectHandler()).open(request, timeout=timeout)


def expect_object(value: Any, noun: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise MerchantError(f"Google Merchant returned a malformed {noun}.")
    return value


def expect_objects(container: Dict[str, Any], key: str, noun: str) -> List[Dict[str, Any]]:
    items = container.get(key, [])
    if not isinstance(items, list):
        raise MerchantError(f"Google Merchant returned a malformed {noun} collection.")
    return [expect_object(item, noun) for item in items]


def decode_response(response: Any, noun: str = "API response") -> Dict[str, Any]:
    raw = response.read()
    if not raw:
        return {}
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MerchantError(f"Google Merchant returned a malformed {noun}: the body is not valid JSON.") from exc
    # A list or scalar body would otherwise surface as an attribute error several frames later.
    return expect_object(payload, noun)


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


def api_request(
    access_token: str,
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    payload: Optional[Dict[str, Any]] = None,
    retries: int = 2,
) -> Dict[str, Any]:
    if not any(url.startswith(base + "/") for base in API_BASES):
        raise MerchantError("Refused an unexpected Google Merchant API origin.")
    if params:
        encoded = urllib.parse.urlencode(params, doseq=True)
        url += ("&" if "?" in url else "?") + encoded
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    for attempt in range(retries + 1):
        try:
            return decode_response(open_url(request))
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries:
                delay = min(8, 2**attempt)
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                if retry_after and retry_after.isdigit():
                    delay = min(30, int(retry_after))
                exc.read()
                time.sleep(delay)
                continue
            raise MerchantError(f"Google Merchant API request failed: {safe_error(exc)}.") from exc
        except urllib.error.URLError as exc:
            raise MerchantError(f"Google Merchant API request failed: {exc.reason}.") from exc
    raise MerchantError("Google Merchant API request failed.")


def emit_csv(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)


def emit_json(value: Any) -> None:
    json.dump(value, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def warn_truncated(truncated: bool, limit: int) -> None:
    if truncated:
        print(f"WARNING: Results were truncated at --limit {limit}.", file=sys.stderr)


def bounded_limit(value: int, maximum: int = 5000) -> int:
    if value < 1 or value > maximum:
        raise MerchantError(f"--limit must be between 1 and {maximum}.")
    return value


# --- Merchant Center Query Language ------------------------------------------------
#
# MCQL's published grammar is:
#     Query       -> SelectClause FromClause? WhereClause? OrderByClause? LimitClause?
#     WhereClause -> WHERE Condition (AND Condition)*
#     Condition   -> FieldName Operator Value | FieldName BETWEEN Value AND Value
#     String      -> (' Char* ') | (" Char* ")
# Three properties of that grammar drive this whole module.
#
# First, the string production defines no escape sequence at all: there is no documented
# way to represent a quote inside an MCQL literal. So this package never escapes a
# literal, it refuses one that would need escaping. A rejected search term is a visible
# failure; a silently mangled or injected WHERE clause is not.
#
# Second, WHERE takes AND only. Google states the clause "doesn't support OR", and the
# grammar has no parentheses, so a caller cannot smuggle disjunction past this builder.
#
# Third, there is no GROUP BY. Segmentation is implicit: selecting a segment field
# groups by it. Every command here therefore controls grouping by choosing which
# segment columns it selects, not by emitting a clause.
#
# Field names are snake_case in a request and camelCase in the response, so each view
# below carries both forms.

MCQL_NAME_RE = re.compile(r"[a-z][a-z0-9_]*")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
# Google's Function production, which is the complete set of relative ranges DURING accepts.
DURING_RANGES = (
    "LAST_7_DAYS", "LAST_14_DAYS", "LAST_30_DAYS", "LAST_BUSINESS_WEEK", "LAST_MONTH",
    "LAST_WEEK_MON_SUN", "LAST_WEEK_SUN_SAT", "THIS_MONTH", "THIS_WEEK_MON_TODAY",
    "THIS_WEEK_SUN_TODAY", "TODAY", "YESTERDAY",
)
# The characters that would end or extend a literal, plus the backslash a caller might
# expect to neutralize them with. MCQL documents no escape, so each one is refused.
UNQUOTABLE = "'\"\\"


def mcql_name(value: str, kind: str = "field") -> str:
    """Accept only a bare snake_case MCQL identifier."""
    if not isinstance(value, str) or not MCQL_NAME_RE.fullmatch(value):
        raise MerchantError(f"Invalid Merchant {kind} name: {value!r}.")
    return value


def mcql_string(value: str) -> str:
    """Quote a literal, refusing any value MCQL cannot represent."""
    if not isinstance(value, str) or not value:
        raise MerchantError("A Merchant filter value must be a non-empty string.")
    for char in value:
        if char in UNQUOTABLE:
            raise MerchantError(
                f"Merchant filter values cannot contain {char!r}: the query language defines no escape for it."
            )
        # A control character cannot appear in a Char* literal and would split the query.
        if ord(char) < 0x20 or ord(char) == 0x7F:
            raise MerchantError("Merchant filter values cannot contain control characters.")
    return f"'{value}'"


def mcql_date(value: str, option: str) -> str:
    """Accept only a real ISO 8601 calendar day, which is the date form MCQL documents."""
    if not DATE_RE.fullmatch(value or ""):
        raise MerchantError(f"{option} must be an ISO 8601 date such as 2024-01-31, got {value!r}.")
    year, month, day = (int(part) for part in value.split("-"))
    try:
        date(year, month, day)
    except ValueError as exc:
        raise MerchantError(f"{option} is not a real calendar date: {value!r}.") from exc
    return f"'{value}'"


@dataclass(frozen=True)
class Query:
    """One bounded MCQL query, assembled only from package-defined names and checked values."""

    table: str
    select: Tuple[str, ...]
    where: Tuple[str, ...] = ()
    order_by: str = ""
    descending: bool = True
    limit: int = 0

    def text(self) -> str:
        if not self.select:
            raise MerchantError("A Merchant query must select at least one field.")
        parts = [
            "SELECT " + ", ".join(mcql_name(name) for name in self.select),
            "FROM " + mcql_name(self.table, "table"),
        ]
        if self.where:
            # AND only: the grammar offers no OR and no parentheses.
            parts.append("WHERE " + " AND ".join(self.where))
        if self.order_by:
            parts.append(
                "ORDER BY " + mcql_name(self.order_by) + (" DESC" if self.descending else " ASC")
            )
        if self.limit:
            # Report commands request one sentinel row beyond their public 5,000-row
            # ceiling so an exact page can still prove whether output was truncated.
            parts.append(f"LIMIT {bounded_limit(self.limit, 5001)}")
        return " ".join(parts)


def equals(name: str, value: str) -> str:
    return f"{mcql_name(name)} = {mcql_string(value)}"


def within(name: str, values: Sequence[str]) -> str:
    if not values:
        raise MerchantError(f"An {name} filter needs at least one value.")
    return f"{mcql_name(name)} IN ({', '.join(mcql_string(value) for value in values)})"


def between_dates(name: str, start: str, end: str) -> str:
    return (
        f"{mcql_name(name)} BETWEEN {mcql_date(start, '--start-date')} "
        f"AND {mcql_date(end, '--end-date')}"
    )


def during(name: str, window: str) -> str:
    if window not in DURING_RANGES:
        raise MerchantError(f"Unknown relative range {window!r}.")
    return f"{mcql_name(name)} DURING {window}"


# --- Reports transport --------------------------------------------------------------

# reports.search caps a page at 1000 rows; asking for more is an argument error, not a
# larger page, so the request is clamped instead of forwarded.
MAX_PAGE_SIZE = 1000


def account_id(value: str) -> str:
    """Accept a bare Merchant Center account ID or its `accounts/{id}` resource name."""
    if not isinstance(value, str):
        raise MerchantError(f"Expected a numeric Merchant account ID, got {value!r}.")
    cleaned = value.strip()
    if cleaned.startswith("accounts/"):
        cleaned = cleaned.split("/", 1)[1]
    if not cleaned.isdigit():
        raise MerchantError(f"Expected a numeric Merchant account ID, got {value!r}.")
    return cleaned


def search_rows(token: str, account: str, query: Query, limit: int, view: str) -> Tuple[List[Dict[str, Any]], bool]:
    """Page through reports.search and return at most `limit` rows of one view."""
    url = f"{REPORTS_BASE}/accounts/{account}/reports:search"
    text = query.text()
    rows: List[Dict[str, Any]] = []
    page_token = ""
    seen_tokens = set()
    for _ in range(MAX_PAGES):
        payload: Dict[str, Any] = {
            "query": text,
            "pageSize": max(1, min(MAX_PAGE_SIZE, limit - len(rows))),
        }
        if page_token:
            payload["pageToken"] = page_token
        response = api_request(token, "POST", url, payload=payload)
        results = expect_objects(response, "results", "report row")
        remaining = limit - len(rows)
        truncated_here = len(results) > remaining
        for result in results[:remaining]:
            # Each row nests its columns under the camelCase name of the queried view.
            if view not in result:
                raise MerchantError(f"Google Merchant returned a report row without {view}.")
            rows.append(expect_object(result[view], "report row"))
        next_token = response.get("nextPageToken", "")
        if not isinstance(next_token, str):
            raise MerchantError("Google Merchant returned a malformed page token.")
        if len(rows) >= limit:
            return rows, truncated_here or bool(next_token)
        if not next_token:
            return rows, False
        if not results:
            # A token that returns nothing would otherwise loop until MAX_PAGES.
            return rows, True
        if next_token in seen_tokens:
            raise MerchantError("Google Merchant pagination did not advance.")
        seen_tokens.add(next_token)
        page_token = next_token
    raise MerchantError(f"Google Merchant pagination exceeded {MAX_PAGES} pages.")


# --- List transport -----------------------------------------------------------------
#
# Every Merchant list method omits nextPageToken on the last page rather than sending an
# empty one, and each documents its own page-size ceiling above which Google silently
# coerces the value. Each caller passes its own ceiling so a request never asks for a
# page the method does not offer.


def list_rows(
    token: str,
    url: str,
    key: str,
    noun: str,
    limit: int,
    page_ceiling: int,
    params: Optional[Dict[str, Any]] = None,
) -> Tuple[List[Dict[str, Any]], bool]:
    rows: List[Dict[str, Any]] = []
    page_token = ""
    seen_tokens = set()
    for _ in range(MAX_PAGES):
        query: Dict[str, Any] = dict(params or {})
        query["pageSize"] = max(1, min(page_ceiling, limit - len(rows)))
        if page_token:
            query["pageToken"] = page_token
        response = api_request(token, "GET", url, params=query)
        page = expect_objects(response, key, noun)
        remaining = limit - len(rows)
        truncated_here = len(page) > remaining
        rows.extend(page[:remaining])
        next_token = response.get("nextPageToken", "")
        if not isinstance(next_token, str):
            raise MerchantError("Google Merchant returned a malformed page token.")
        if len(rows) >= limit:
            return rows, truncated_here or bool(next_token)
        # A short page does not mean the end; only a missing token does.
        if not next_token:
            return rows, False
        if not page:
            return rows, True
        if next_token in seen_tokens:
            raise MerchantError("Google Merchant pagination did not advance.")
        seen_tokens.add(next_token)
        page_token = next_token
    raise MerchantError(f"Google Merchant pagination exceeded {MAX_PAGES} pages.")


def text_field(row: Dict[str, Any], name: str) -> str:
    """Read one scalar cell, keeping an unexpected nested value out of the output."""
    value = row.get(name, "")
    if isinstance(value, (dict, list)):
        raise MerchantError(f"Google Merchant returned a malformed {name} value.")
    if value is None or value is False:
        return "" if value is None else "false"
    if value is True:
        return "true"
    return str(value)


def count_field(row: Dict[str, Any], name: str) -> str:
    """Read a non-negative count, treating an omitted protobuf default as zero."""
    value = row.get(name, 0)
    if value in (None, ""):
        return "0"
    if isinstance(value, bool) or not (
        isinstance(value, int) or isinstance(value, str) and value.isdigit()
    ):
        raise MerchantError(f"Google Merchant returned a malformed {name} value.")
    count = int(value)
    if count < 0:
        raise MerchantError(f"Google Merchant returned a malformed {name} value.")
    return str(count)


def emit_rows(headers: Sequence[str], rows: List[Dict[str, Any]], as_json: bool) -> None:
    if as_json:
        emit_json(rows)
        return
    emit_csv(headers, ([row.get(header, "") for header in headers] for row in rows))


# --- Accounts, status, and item issues ----------------------------------------------

# Google's reporting-context enum. Unknown members returned by Google are passed through
# unchanged; this tuple only bounds what a caller may send in a filter.
REPORTING_CONTEXTS = (
    "SHOPPING_ADS", "DEMAND_GEN_ADS", "DEMAND_GEN_ADS_DISCOVER_SURFACE", "VIDEO_ADS",
    "DISPLAY_ADS", "LOCAL_INVENTORY_ADS", "VEHICLE_INVENTORY_ADS", "FREE_LISTINGS",
    "FREE_LISTINGS_UCP_CHECKOUT", "FREE_LOCAL_LISTINGS", "FREE_LOCAL_VEHICLE_LISTINGS",
    "YOUTUBE_AFFILIATE", "YOUTUBE_SHOPPING", "YOUTUBE_CHECKOUT", "CLOUD_RETAIL",
    "LOCAL_CLOUD_RETAIL", "PRODUCT_REVIEWS", "MERCHANT_REVIEWS",
)
COUNTRY_RE = re.compile(r"[A-Z]{2}")
ACCOUNT_PAGE_CEILING = 500
STATUS_PAGE_CEILING = 250


def country_code(value: str) -> str:
    """Accept only a CLDR/ISO 3166-1 alpha-2 territory code."""
    cleaned = (value or "").strip().upper()
    if not COUNTRY_RE.fullmatch(cleaned):
        raise MerchantError(f"--country must be a two-letter country code such as US, got {value!r}.")
    return cleaned


def reporting_context(value: str) -> str:
    cleaned = (value or "").strip().upper()
    if cleaned not in REPORTING_CONTEXTS:
        raise MerchantError(
            f"--reporting-context must be one of: {', '.join(REPORTING_CONTEXTS)}."
        )
    return cleaned


def status_filter(context: str, country: str) -> str:
    """Build the aggregate-status filter, which accepts only reportingContext and country."""
    terms = []
    if context:
        terms.append(f'reportingContext = "{reporting_context(context)}"')
    if country:
        terms.append(f'country = "{country_code(country)}"')
    return " AND ".join(terms)


def expect_known_shape(row: Dict[str, Any], expected: Sequence[str], noun: str) -> Dict[str, Any]:
    """Refuse a row that carries none of the fields this package knows how to read.

    A shape this package does not recognize is reported rather than rendered as a row
    of empty columns. A blank column reads as "no issues", which is the one wrong answer
    that must never be produced silently.
    """
    if not any(key in row for key in expected):
        raise MerchantError(
            f"Google Merchant returned an unrecognized {noun} shape; expected one of: "
            + ", ".join(expected)
            + "."
        )
    return row


def command_profiles(args: argparse.Namespace) -> None:
    """Which Google accounts Rundesk holds for one OAuth app profile, without asking Google."""
    profile = (args.profile or "").strip()
    if args.auth:
        sign_in(profile)
    rows, trouble = managed_rows(profile)
    emit_rows(("profile", "account", "status"), rows, args.json)
    listed(trouble)


def command_accounts(args: argparse.Namespace) -> None:
    access = selected_access(args)
    limit = bounded_limit(args.limit, 2000)
    token = access.token()
    accounts, truncated = list_rows(
        token, f"{ACCOUNTS_BASE}/accounts", "accounts", "account", limit, ACCOUNT_PAGE_CEILING
    )
    rows = []
    for account in accounts:
        zone = expect_object(account.get("timeZone", {}), "account time zone")
        rows.append(
            {
                "account_id": text_field(account, "accountId"),
                "account_name": text_field(account, "accountName"),
                "language_code": text_field(account, "languageCode"),
                "time_zone": text_field(zone, "id"),
                "adult_content": text_field(account, "adultContent"),
                "test_account": text_field(account, "testAccount"),
                "profile": access.name,
            }
        )
    emit_rows(
        ("account_id", "account_name", "language_code", "time_zone", "adult_content",
         "test_account", "profile"),
        rows,
        args.json,
    )
    warn_truncated(truncated, limit)


def command_status(args: argparse.Namespace) -> None:
    access = selected_access(args)
    account = account_id(args.account)
    limit = bounded_limit(args.limit, 1000)
    params = {}
    selector = status_filter(args.reporting_context or "", args.country or "")
    if selector:
        params["filter"] = selector
    statuses, truncated = list_rows(
        access.token(),
        f"{ISSUES_BASE}/accounts/{account}/aggregateProductStatuses",
        "aggregateProductStatuses",
        "aggregate product status",
        limit,
        STATUS_PAGE_CEILING,
        params=params,
    )
    rows = []
    for status in statuses:
        if "stats" not in status:
            raise MerchantError("Google Merchant returned an aggregate product status without stats.")
        stats = expect_object(status["stats"], "product status stats")
        rows.append(
            {
                "reporting_context": text_field(status, "reportingContext"),
                "country": text_field(status, "country"),
                "active": count_field(stats, "activeCount"),
                "pending": count_field(stats, "pendingCount"),
                "expiring": count_field(stats, "expiringCount"),
                "disapproved": count_field(stats, "disapprovedCount"),
                "issue_count": len(expect_objects(status, "itemLevelIssues", "item level issue")),
                "account_id": account,
                "profile": access.name,
            }
        )
    emit_rows(
        ("reporting_context", "country", "active", "pending", "expiring", "disapproved",
         "issue_count", "account_id", "profile"),
        rows,
        args.json,
    )
    warn_truncated(truncated, limit)


def command_issues(args: argparse.Namespace) -> None:
    access = selected_access(args)
    account = account_id(args.account)
    limit = bounded_limit(args.limit, 1000)
    params = {}
    selector = status_filter(args.reporting_context or "", args.country or "")
    if selector:
        params["filter"] = selector
    # The command limit applies to emitted issues, not to country/context buckets.
    # Read a separately bounded set of aggregate buckets before ranking their issues;
    # otherwise one bucket can produce more rows than the operator requested.
    statuses, statuses_truncated = list_rows(
        access.token(),
        f"{ISSUES_BASE}/accounts/{account}/aggregateProductStatuses",
        "aggregateProductStatuses",
        "aggregate product status",
        1000,
        STATUS_PAGE_CEILING,
        params=params,
    )
    rows = []
    for status in statuses:
        expect_known_shape(status, ("stats", "itemLevelIssues"), "aggregate product status")
        context = text_field(status, "reportingContext")
        country = text_field(status, "country")
        for issue in expect_objects(status, "itemLevelIssues", "item level issue"):
            rows.append(
                {
                    "code": text_field(issue, "code"),
                    "severity": text_field(issue, "severity"),
                    "resolution": text_field(issue, "resolution"),
                    "products": count_field(issue, "productCount"),
                    "attribute": text_field(issue, "attribute"),
                    "reporting_context": context,
                    "country": country,
                    "description": text_field(issue, "description"),
                    # The issueresolution sub-API names this documentationUri; the products
                    # sub-API names the same link documentation. They are not interchangeable.
                    "documentation": text_field(issue, "documentationUri"),
                    "account_id": account,
                    "profile": access.name,
                }
            )
    # Largest blast radius first, so a small --limit still shows what matters most.
    def product_count(row: Dict[str, Any]) -> int:
        try:
            return int(row["products"])
        except (TypeError, ValueError) as exc:
            raise MerchantError("Google Merchant returned a malformed productCount value.") from exc

    rows.sort(key=product_count, reverse=True)
    truncated = statuses_truncated or len(rows) > limit
    rows = rows[:limit]
    emit_rows(
        ("code", "severity", "resolution", "products", "attribute", "reporting_context",
         "country", "description", "documentation", "account_id", "profile"),
        rows,
        args.json,
    )
    warn_truncated(truncated, limit)


# --- Report value rendering ---------------------------------------------------------


def money_amount(value: Dict[str, Any]) -> str:
    """Render a Price as its currency's standard unit. Micros are an int64 sent as a string."""
    raw = value.get("amountMicros", "")
    if raw in ("", None):
        return ""
    try:
        micros = int(raw)
    except (TypeError, ValueError) as exc:
        raise MerchantError("Google Merchant returned a malformed price amount.") from exc
    # Decimal keeps a price exact; binary floats do not represent cents exactly.
    return str(Decimal(micros) / Decimal(1000000))


def report_cell(value: Any) -> str:
    """Render one report field, flattening the shapes Google nests inside a row."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return "|".join(report_cell(item) for item in value)
    if isinstance(value, dict):
        if "amountMicros" in value or "currencyCode" in value:
            return money_amount(value)
        # A google.type.Date arrives as an object here and as a plain string elsewhere.
        if "year" in value and "month" in value and "day" in value:
            return "{0:04d}-{1:02d}-{2:02d}".format(
                int(value.get("year") or 0), int(value.get("month") or 0), int(value.get("day") or 0)
            )
        raise MerchantError("Google Merchant returned an unexpected nested report value.")
    return str(value)


def is_money(value: Any) -> bool:
    """Recognize a Price exactly as report_cell renders one, so the two never disagree."""
    return isinstance(value, dict) and ("amountMicros" in value or "currencyCode" in value)


def report_currency(value: Any) -> str:
    if is_money(value):
        code = value.get("currencyCode", "")
        return str(code) if code else ""
    return ""


def camel(name: str) -> str:
    """Map an MCQL snake_case field to the camelCase key Google returns it under."""
    head, _, tail = name.partition("_")
    return head + "".join(part[:1].upper() + part[1:] for part in tail.split("_") if part)


def report_table(rows: List[Dict[str, Any]], fields: Sequence[str], extra: Dict[str, str]) -> Tuple[List[str], List[Dict[str, str]]]:
    """Flatten report rows into CSV columns, giving any Price field its own currency column."""
    headers: List[str] = []
    for name in fields:
        headers.append(name)
        if name in MONEY_FIELDS or any(is_money(row.get(camel(name))) for row in rows):
            headers.append(f"{name}_currency")
    headers.extend(extra)
    table = []
    for row in rows:
        record: Dict[str, str] = {}
        for name in fields:
            value = row.get(camel(name))
            record[name] = report_cell(value)
            if f"{name}_currency" in headers:
                record[f"{name}_currency"] = report_currency(value)
        record.update(extra)
        table.append(record)
    return headers, table


# --- Bounded reports ----------------------------------------------------------------
#
# Every field name below is a current Merchant API v1 name taken from the reports_v1
# ReportRow reference. Callers choose a breakdown, never a raw field list, so a query
# can only ever be assembled from names checked in here.

PERFORMANCE_METRICS = (
    "clicks", "impressions", "click_through_rate", "conversions", "conversion_value",
    "conversion_rate",
)
MONEY_FIELDS = frozenset({"price", "benchmark_price", "suggested_price", "conversion_value"})
PERFORMANCE_BREAKDOWNS = {
    "date": ("date",),
    "week": ("week",),
    "product": ("offer_id", "title"),
    "brand": ("brand",),
    "category": ("category_l1", "category_l2", "category_l3"),
    "product-type": ("product_type_l1", "product_type_l2", "product_type_l3"),
    "country": ("customer_country_code",),
    "marketing-method": ("marketing_method",),
    "store-type": ("store_type",),
    "custom-label": ("custom_label0",),
}
# A time series reads in order; every other breakdown reads largest first.
TIME_BREAKDOWNS = frozenset({"date", "week"})
MARKETING_METHODS = ("ADS", "ORGANIC")
STORE_TYPES = ("ONLINE_STORE", "LOCAL_STORES")

PRODUCT_FIELDS = (
    "id", "offer_id", "title", "brand", "condition", "availability", "price",
    "aggregated_reporting_context_status", "click_potential", "click_potential_rank",
    "channel", "feed_label", "language_code",
)
PRODUCT_STATUSES = (
    "ELIGIBLE", "ELIGIBLE_LIMITED", "PENDING", "NOT_ELIGIBLE_OR_DISAPPROVED",
)

PRICE_COMPETITIVENESS_FIELDS = (
    "id", "offer_id", "title", "brand", "price", "benchmark_price", "report_country_code",
)
PRICE_INSIGHTS_FIELDS = (
    "id", "offer_id", "title", "brand", "price", "suggested_price", "effectiveness",
    "predicted_impressions_change_fraction", "predicted_clicks_change_fraction",
    "predicted_conversions_change_fraction",
)

BEST_SELLER_VIEWS = {
    "products": (
        "best_sellers_product_cluster_view",
        ("report_date", "report_granularity", "report_country_code", "report_category_id",
         "rank", "previous_rank", "relative_demand", "previous_relative_demand",
         "relative_demand_change", "title", "brand", "inventory_status"),
    ),
    "brands": (
        "best_sellers_brand_view",
        ("report_date", "report_granularity", "report_country_code", "report_category_id",
         "rank", "previous_rank", "relative_demand", "previous_relative_demand",
         "relative_demand_change", "brand"),
    ),
}
GRANULARITIES = {"weekly": "WEEKLY", "monthly": "MONTHLY"}

# The three competitive-visibility views disagree about `date`: the benchmark view
# requires it in SELECT, the top-merchant view forbids it there, and all three require
# it in WHERE. Each view therefore carries its own selected columns.
VISIBILITY_VIEWS = {
    "benchmark": (
        "competitive_visibility_benchmark_view",
        ("date", "report_country_code", "report_category_id", "traffic_source",
         "your_domain_visibility_trend", "category_benchmark_visibility_trend"),
        "",
    ),
    "competitor": (
        "competitive_visibility_competitor_view",
        ("date", "domain", "is_your_domain", "report_country_code", "report_category_id",
         "traffic_source", "rank", "ads_organic_ratio", "page_overlap_rate",
         "higher_position_rate", "relative_visibility"),
        "rank",
    ),
    "top-merchant": (
        "competitive_visibility_top_merchant_view",
        ("domain", "is_your_domain", "report_country_code", "report_category_id",
         "traffic_source", "rank", "ads_organic_ratio", "page_overlap_rate",
         "higher_position_rate"),
        "rank",
    ),
}
TRAFFIC_SOURCES = ("ORGANIC", "ADS", "ALL")


def category_id(value: str) -> str:
    """Google's numeric product-category ID, which its own samples send unquoted."""
    cleaned = (value or "").strip()
    if not cleaned.isdigit():
        raise MerchantError(f"--category must be a numeric Google product category ID, got {value!r}.")
    return cleaned


def enum_choice(value: str, allowed: Sequence[str], option: str) -> str:
    cleaned = (value or "").strip().upper().replace("-", "_")
    if cleaned not in allowed:
        raise MerchantError(f"{option} must be one of: {', '.join(allowed).lower()}.")
    return cleaned


def run_report(
    args: argparse.Namespace,
    table: str,
    fields: Sequence[str],
    where: Sequence[str],
    order_by: str = "",
    descending: bool = True,
    notes: Sequence[str] = (),
) -> None:
    access = selected_access(args)
    account = account_id(args.account)
    limit = bounded_limit(args.limit)
    query = Query(table, tuple(fields), tuple(where), order_by, descending, limit + 1)
    # Assemble and check the query before refreshing a token, so a rejected value costs
    # no network round trip and no credential use.
    query.text()
    rows, transport_truncated = search_rows(
        access.token(), account, query, limit + 1, camel(table)
    )
    truncated = transport_truncated or len(rows) > limit
    rows = rows[:limit]
    headers, table_rows = report_table(
        rows, fields, {"account_id": account, "profile": access.name}
    )
    emit_rows(headers, table_rows, args.json)
    for note in notes:
        print(f"NOTE: {note}", file=sys.stderr)
    warn_truncated(truncated, limit)


def date_condition(args: argparse.Namespace) -> str:
    """Resolve the required date condition from an explicit window or a relative range.

    Defaulting to Google's own DURING constant keeps the query free of this machine's
    clock, so a report asks Google what "the last 30 days" means in the account's own
    time zone rather than guessing it here.
    """
    if args.start_date or args.end_date:
        if not (args.start_date and args.end_date):
            raise MerchantError("--start-date and --end-date must be given together.")
        return between_dates("date", args.start_date, args.end_date)
    return during("date", args.during.strip().upper())


def command_performance(args: argparse.Namespace) -> None:
    segments = PERFORMANCE_BREAKDOWNS[args.breakdown]
    # Google requires a date condition on every performance query and requires at least
    # one metric beside any segment, so both are structural here rather than optional.
    where = [date_condition(args)]
    if args.marketing_method:
        where.append(
            equals("marketing_method", enum_choice(args.marketing_method, MARKETING_METHODS, "--marketing-method"))
        )
    if args.country:
        where.append(equals("customer_country_code", country_code(args.country)))
    if args.store_type:
        where.append(equals("store_type", enum_choice(args.store_type, STORE_TYPES, "--store-type")))
    time_series = args.breakdown in TIME_BREAKDOWNS
    run_report(
        args,
        "product_performance_view",
        tuple(segments) + PERFORMANCE_METRICS,
        where,
        order_by=segments[0] if time_series else "clicks",
        descending=not time_series,
        notes=(
            "Dates are days in the Merchant Center account time zone.",
            "Google reports conversions, conversion value, and conversion rate only for the "
            "free traffic source, so ads rows leave them empty.",
            "A row carrying a price metric is returned once per currency, separately from the "
            "non-price metrics; do not sum the two kinds of row together.",
        ),
    )


def command_products(args: argparse.Namespace) -> None:
    where = []
    if args.status:
        where.append(
            equals("aggregated_reporting_context_status", enum_choice(args.status, PRODUCT_STATUSES, "--status"))
        )
    if args.brand:
        where.append(equals("brand", args.brand))
    if args.reporting_context:
        # reporting_context is filterable only; Google refuses it in a SELECT clause.
        where.append(equals("reporting_context", reporting_context(args.reporting_context)))
    run_report(
        args,
        "product_view",
        PRODUCT_FIELDS,
        where,
        order_by="click_potential_rank",
        descending=False,
        notes=(
            "Click potential rank runs from 1, the highest potential, to 1000.",
            "Google does not allow filtering or sorting on per-context status or item issues; "
            "use the issues command for issue diagnostics.",
        ),
    )


def command_price_competitiveness(args: argparse.Namespace) -> None:
    where = [equals("report_country_code", country_code(args.country))] if args.country else []
    run_report(
        args,
        "price_competitiveness_product_view",
        PRICE_COMPETITIVENESS_FIELDS,
        where,
        notes=("Benchmark price is the latest benchmark for the product's catalog in the benchmark country.",),
    )


def command_price_insights(args: argparse.Namespace) -> None:
    run_report(
        args,
        "price_insights_product_view",
        PRICE_INSIGHTS_FIELDS,
        (),
        notes=(
            "Predicted change fractions are Google's forecast for adopting the suggested price.",
        ),
    )


def command_best_sellers(args: argparse.Namespace) -> None:
    table, fields = BEST_SELLER_VIEWS[args.view]
    # Google requires granularity and country conditions; date and category are optional
    # and default to the latest report and to every top-level category.
    where = [
        equals("report_granularity", GRANULARITIES[args.granularity]),
        equals("report_country_code", country_code(args.country)),
    ]
    if args.category:
        where.append(f"report_category_id = {category_id(args.category)}")
    if args.date:
        where.append(f"report_date = {mcql_date(args.date, '--date')}")
    run_report(
        args,
        table,
        fields,
        where,
        order_by="rank",
        descending=False,
        notes=(
            "Without --date Google returns its latest available report.",
            "Inventory status ignores the report country filter.",
        ),
    )


def command_competitive_visibility(args: argparse.Namespace) -> None:
    table, fields, ranked_by = VISIBILITY_VIEWS[args.view]
    # Google requires a date, a country, and a category on every competitive-visibility
    # query, and warns that spanning several countries or categories can time out, so
    # this command sends exactly one of each.
    where = [
        date_condition(args),
        equals("report_country_code", country_code(args.country)),
        f"report_category_id = {category_id(args.category)}",
    ]
    if args.traffic_source:
        where.append(equals("traffic_source", enum_choice(args.traffic_source, TRAFFIC_SOURCES, "--traffic-source")))
    run_report(
        args,
        table,
        fields,
        where,
        order_by=ranked_by,
        descending=False,
        notes=("Competitive visibility covers one country and one category per request.",),
    )


# --- Command line -------------------------------------------------------------------


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", help="Which Google OAuth app profile Rundesk signed in with")
    parser.add_argument("--email", help="Which signed-in Google account to use when Rundesk holds more than one")
    parser.add_argument("--auth", action="store_true", help="Run `rundesk login google` first, with --profile when given")
    parser.add_argument("--json", action="store_true", help="Emit normalized JSON")


def add_account_option(parser: argparse.ArgumentParser, default_limit: int) -> None:
    parser.add_argument("--account", required=True, help="Merchant Center account ID")
    parser.add_argument("--limit", type=int, default=default_limit)


def add_date_window(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--during", default="LAST_30_DAYS",
        help="Relative range: " + ", ".join(DURING_RANGES),
    )
    parser.add_argument("--start-date", help="ISO 8601 start date; requires --end-date")
    parser.add_argument("--end-date", help="ISO 8601 end date; requires --start-date")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="google-merchant", description="Read bounded Google Merchant Center data."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    profiles = subparsers.add_parser("profiles", help="List the Google accounts Rundesk holds, without a network request")
    profiles.add_argument("--profile", help="OAuth app profile to list Rundesk's signed-in accounts for")
    profiles.add_argument("--auth", action="store_true", help="Run `rundesk login google` first, with --profile when given")
    profiles.add_argument("--json", action="store_true", help="Emit normalized JSON")
    profiles.set_defaults(handler=command_profiles)

    accounts = subparsers.add_parser("accounts", help="List accessible Merchant Center accounts")
    add_common_options(accounts)
    accounts.add_argument("--limit", type=int, default=25)
    accounts.set_defaults(handler=command_accounts)

    status = subparsers.add_parser("status", help="Report product counts by reporting context and country")
    add_common_options(status)
    add_account_option(status, 50)
    status.add_argument("--reporting-context", help="Restrict to one reporting context")
    status.add_argument("--country", help="Restrict to one two-letter country code")
    status.set_defaults(handler=command_status)

    issues = subparsers.add_parser("issues", help="Report item-level issues and how many products each affects")
    add_common_options(issues)
    add_account_option(issues, 50)
    issues.add_argument("--reporting-context", help="Restrict to one reporting context")
    issues.add_argument("--country", help="Restrict to one two-letter country code")
    issues.set_defaults(handler=command_issues)

    products = subparsers.add_parser("products", help="List products with their serving status")
    add_common_options(products)
    add_account_option(products, 50)
    products.add_argument("--status", help="Restrict to one status: " + ", ".join(PRODUCT_STATUSES))
    products.add_argument("--brand", help="Restrict to one exact brand")
    products.add_argument("--reporting-context", help="Restrict statuses to one reporting context")
    products.set_defaults(handler=command_products)

    performance = subparsers.add_parser("performance", help="Report product impressions, clicks, and conversions")
    add_common_options(performance)
    add_account_option(performance, 25)
    add_date_window(performance)
    performance.add_argument("--breakdown", choices=sorted(PERFORMANCE_BREAKDOWNS), default="product")
    performance.add_argument("--marketing-method", help="Restrict to ads or organic")
    performance.add_argument("--country", help="Restrict to one customer country code")
    performance.add_argument("--store-type", help="Restrict to online_store or local_stores")
    performance.set_defaults(handler=command_performance)

    competitiveness = subparsers.add_parser(
        "price-competitiveness", help="Compare product prices against Google's benchmark"
    )
    add_common_options(competitiveness)
    add_account_option(competitiveness, 50)
    competitiveness.add_argument("--country", help="Restrict to one benchmark country code")
    competitiveness.set_defaults(handler=command_price_competitiveness)

    insights = subparsers.add_parser("price-insights", help="Report Google's suggested prices and forecasts")
    add_common_options(insights)
    add_account_option(insights, 50)
    insights.set_defaults(handler=command_price_insights)

    best_sellers = subparsers.add_parser("best-sellers", help="Report the best selling products or brands on Google")
    add_common_options(best_sellers)
    add_account_option(best_sellers, 50)
    best_sellers.add_argument("--view", choices=sorted(BEST_SELLER_VIEWS), default="products")
    best_sellers.add_argument("--granularity", choices=sorted(GRANULARITIES), default="weekly")
    best_sellers.add_argument("--country", required=True, help="Two-letter country code")
    best_sellers.add_argument("--category", help="Numeric Google product category ID")
    best_sellers.add_argument("--date", help="ISO 8601 report date; defaults to Google's latest report")
    best_sellers.set_defaults(handler=command_best_sellers)

    visibility = subparsers.add_parser(
        "competitive-visibility", help="Report visibility against competing domains"
    )
    add_common_options(visibility)
    add_account_option(visibility, 50)
    add_date_window(visibility)
    visibility.add_argument("--view", choices=sorted(VISIBILITY_VIEWS), default="benchmark")
    visibility.add_argument("--country", required=True, help="Two-letter country code")
    visibility.add_argument("--category", required=True, help="Numeric Google product category ID")
    visibility.add_argument("--traffic-source", help="Restrict to organic, ads, or all")
    visibility.set_defaults(handler=command_competitive_visibility)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.handler(args)
    except MerchantError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
