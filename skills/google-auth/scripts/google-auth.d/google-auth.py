#!/usr/bin/env python3
"""Google sign-in for this catalog: the provider Rundesk reads, and the accounts it holds."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import shutil
import signal
import socket
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


class GoogleAuthError(RuntimeError):
    """A safe, user-facing failure of this package."""


# --- Rundesk-managed Google sign-in -------------------------------------------------------------
#
# Rundesk owns the OAuth client, the browser, the refresh token, and where those are kept. This
# package owns none of it and asks the install's own CLI for one short-lived access token, which
# arrives over one connected unnamed local socket held by nothing but these two processes rather
# than through argv, the environment, stdout, or a file. The wire format is Rundesk's hidden
# `_oauth` bridge, version 1. Rundesk refuses a pipe, a named socket, a regular file, and 0, 1, 2.
COMMAND_VARIABLE = "RUNDESK_COMMAND"
BRIDGE = "_oauth"
# The provider this package declares. `oauth-provider.json` beside `SKILL.md` is the definition
# Rundesk reads; this command only reports it and asks about the accounts held for it.
PROVIDER = "google"
DECLARATION = "oauth-provider.json"
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
        raise GoogleAuthError(
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
            raise GoogleAuthError("Rundesk did not answer the Google request in time.")
        connection.settimeout(remaining)
        try:
            part = connection.recv(wanted - len(held))
        except socket.timeout as exc:
            raise GoogleAuthError("Rundesk did not answer the Google request in time.") from exc
        if not part:
            raise GoogleAuthError("Rundesk closed the Google response before answering.")
        held.extend(part)
    return bytes(held)


def read_frame(connection: socket.socket, deadline: float) -> dict[str, Any]:
    """One version 1 frame: four big-endian length bytes, then that much compact UTF-8 JSON.

    `deadline` is a `time.monotonic` instant shared with the wait that follows, so reading and
    reaping cannot each spend the whole allowance.
    """
    size = struct.unpack(">I", read_exactly(connection, 4, deadline))[0]
    if size > MAX_FRAME:
        raise GoogleAuthError("Rundesk sent an oversized Google response.")
    try:
        payload = json.loads(read_exactly(connection, size, deadline).decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise GoogleAuthError("Rundesk sent a malformed Google response.") from exc
    if not isinstance(payload, dict) or payload.get("version") != BRIDGE_VERSION:
        raise GoogleAuthError("Rundesk sent a Google response version this package cannot read.")
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
            trouble: str = "") -> GoogleAuthError:
    if unsupported(code, said):
        return GoogleAuthError(
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
    return GoogleAuthError(
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
    raise GoogleAuthError(f"Rundesk did not finish {doing} in time, and was stopped.")


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
            raise GoogleAuthError(
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
        except GoogleAuthError as exc:
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
        raise GoogleAuthError("Rundesk sent a malformed Google account list.")
    return accounts


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
        raise GoogleAuthError(
            f"Cannot run {command} to sign in to Google: {exc.strerror or exc}."
        ) from exc
    said, code = finished(process, deadline, "signing in to Google")
    if code != 0:
        raise refused(code, said, profile)


def listed(trouble: str) -> None:
    """Raise after a listing has been written, so the rows are seen and the exit is still earned.

    Written first and refused second on purpose: a person gets the table with the reason in it, and
    a script gets a non-zero exit instead of an empty account list it would have believed.
    """
    if trouble:
        raise GoogleAuthError(trouble)


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
    except GoogleAuthError as exc:
        return [{"profile": named, "account": "", "status": str(exc)}], str(exc)
    if not accounts:
        return [{"profile": named, "account": "", "status": f"run: {login_command(profile)}"}], ""
    return [{"profile": named, "account": account, "status": "ready"}
            for account in accounts], ""


def declared_at() -> Path:
    """The declaration beside `SKILL.md`, found from this file rather than from the caller's cwd."""
    return Path(__file__).resolve().parent.parent.parent / DECLARATION


def declaration() -> dict[str, Any]:
    """What this package declares Google to be. Read fresh, and never network."""
    try:
        value = json.loads(declared_at().read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise GoogleAuthError(f"{declared_at()} is not readable JSON.") from exc
    if not isinstance(value, dict) or value.get("provider") != PROVIDER:
        raise GoogleAuthError(f"{declared_at()} does not declare the {PROVIDER} provider.")
    return value


def write_rows(rows: list[dict[str, Any]], columns: list[str], as_json: bool) -> None:
    if as_json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    sys.stdout.write(output.getvalue())


def cmd_provider(args: argparse.Namespace) -> None:
    """What Rundesk reads to sign in to Google, said plainly and without contacting anyone."""
    value = declaration()
    if args.json:
        print(json.dumps(value, indent=2, sort_keys=True))
        return
    rows = [
        {"field": "provider", "value": value["provider"]},
        {"field": "display_name", "value": value["display_name"]},
        {"field": "authorization_endpoint", "value": value["authorization_endpoint"]},
        {"field": "token_endpoint", "value": value["token_endpoint"]},
        {"field": "identity_endpoint", "value": value["identity_endpoint"]},
        {"field": "base_scopes", "value": " ".join(value["base_scopes"])},
        {"field": "client_secret", "value": str(bool(value["client_secret"])).lower()},
    ]
    rows.extend({"field": f"capability {name}", "value": scope}
                for name, scope in sorted(value["capabilities"].items()))
    write_rows(rows, ["field", "value"], args.json)


def cmd_accounts(args: argparse.Namespace) -> None:
    """Every Google account Rundesk holds for one OAuth app profile."""
    profile = (args.profile or "").strip()
    if args.auth:
        sign_in(profile)
    rows, trouble = managed_rows(profile)
    write_rows(rows, ["profile", "account", "status"], args.json)
    listed(trouble)


def cmd_login(args: argparse.Namespace) -> None:
    """Hand the person Rundesk's own browser sign-in, then say what it connected."""
    profile = (args.profile or "").strip()
    sign_in(profile)
    rows, trouble = managed_rows(profile)
    write_rows(rows, ["profile", "account", "status"], args.json)
    listed(trouble)


def parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="Emit normalized JSON")
    profile = argparse.ArgumentParser(add_help=False)
    profile.add_argument("--profile", help="Which Google OAuth app profile Rundesk signed in with")
    result = argparse.ArgumentParser(
        prog="google-auth",
        description="Report this catalog's Google OAuth provider and the accounts Rundesk holds.")
    subs = result.add_subparsers(dest="command", required=True)
    one = subs.add_parser("provider", parents=[common],
                          help="Show the Google OAuth definition this catalog declares.")
    one.set_defaults(func=cmd_provider)
    one = subs.add_parser("accounts", parents=[common, profile],
                          help="List the Google accounts Rundesk holds, without contacting Google.")
    one.add_argument("--auth", action="store_true",
                     help="Run `rundesk login google` first, with --profile when given")
    one.set_defaults(func=cmd_accounts)
    one = subs.add_parser("login", parents=[common, profile],
                          help="Connect a Google account in the browser through Rundesk.")
    one.set_defaults(func=cmd_login)
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        args.func(args)
        return 0
    except GoogleAuthError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
