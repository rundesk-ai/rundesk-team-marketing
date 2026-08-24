#!/usr/bin/env python3
"""
Read one PostHog project's analytics, bounded and read-only.

Usage:
  posthog profiles
  posthog event-definitions [--name signup] [--exclude-hidden] [--exclude-stale] [--limit 25]
  posthog events [--event '$pageview'] [--distinct-id ID] [--after 2026-08-01] [--before 2026-08-08] [--limit 25]
  posthog persons [--search text] [--email person@example.test] [--distinct-id ID] [--limit 25]
  posthog recordings [--offset 0] [--limit 10]
  posthog web [--days 7] [--no-compare]
  posthog insights [--search text] [--type TRENDS] [--date-from -7d] [--date-to -1d] [--limit 25]
  posthog insight SHORT_ID_OR_ID
  posthog query --sql "SELECT event, count() FROM events GROUP BY event" [--limit 100]
  posthog analytics {trends|traffic|audiences|leads|conversion} [--event NAME] [--days 7]
    [--after 2026-08-01] [--before 2026-08-08] [--limit 100]

Inputs:
  Reads process env or an explicit/shared/isolated dotenv. A Rundesk-managed account appends
  __<PROFILE> to the plain variable name, such as POSTHOG_PERSONAL_API_KEY__EXAMPLE, with the
  plain POSTHOG_PERSONAL_API_KEY as the default account; the older POSTHOG_<PROFILE>_<FIELD>
  keys still resolve. See references/cli.md for setup. Secrets must stay in an owner-only
  environment file.

Outputs:
  Writes compact text to stdout, one `key=value | key=value` line per record. Raw JSON only with
  --json. Truncation, legacy-endpoint warnings, and refusals go to stderr. Every command is a
  read: this package has no verb that creates, edits, or deletes anything in PostHog.

  Analytics windows are UTC. A bare date means UTC midnight and the generated HogQL names the
  timezone explicitly, so the same window returns the same rows whatever the project's timezone.
"""

from __future__ import annotations

import argparse
import datetime
import ipaddress
import json
import os
import re
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


DEFAULT_BASE_URL = "https://us.posthog.com"
# PostHog's own cloud regions, named so an owner sees the EU host without searching for it.
KNOWN_REGIONS = ("https://us.posthog.com", "https://eu.posthog.com")
# One request never walks more than this many pages, whatever --limit asks for.
MAX_PAGES = 5
MAX_LIMIT = 1000
MAX_DAYS = 365
MAX_QUERY_NAME = 128
REQUEST_TIMEOUT = 30
MAX_RESPONSE_BYTES = 10 * 1024 * 1024

EMAIL_PATTERN = re.compile(
    r"(?<![\w.+-])([A-Z0-9._%+-]+)@([A-Z0-9.-]+\.[A-Z]{2,})(?![\w.-])",
    re.IGNORECASE,
)
IP_CANDIDATE_PATTERN = re.compile(r"(?<![0-9A-Fa-f:.])\[?[0-9A-Fa-f:.]+\]?(?![0-9A-Fa-f:.])")
ISO_TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?$"
)


def default_env_candidates() -> list[Path]:
    """Explicit shared configuration, then isolated and legacy per-tool files."""
    candidates: list[Path] = []
    for key in ("POSTHOG_ENV_FILE", "RUNDESK_INTEGRATIONS_ENV"):
        value = os.environ.get(key)
        if value:
            candidates.append(Path(value).expanduser())
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")).expanduser()
    candidates.append(xdg / "rundesk" / "integrations" / "posthog" / "env")
    candidates.append(xdg / "posthog" / "env")
    return candidates


def resolve_env_file(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    for path in default_env_candidates():
        if path.is_file():
            return path
    return default_env_candidates()[-1]


DEFAULT_ENV = resolve_env_file()


class PostHogError(RuntimeError):
    pass


@dataclass(frozen=True)
class Profile:
    name: str
    api_key: str
    project_id: str
    base_url: str
    label: str


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    mode = path.stat().st_mode & 0o777
    if mode & 0o077:
        print(
            f"WARNING: dotenv file {path} is accessible by group or others (mode {mode:04o}); "
            "restrict it with chmod 600.",
            file=sys.stderr,
        )

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


# Each plain variable name Rundesk manages, paired with the per-profile suffix this repository
# has always used, so both spellings resolve to the same field. The keys are exactly the names
# declared in rundesk.json plus the optional ones a command only uses when present.
PROFILE_FIELDS = {
    "POSTHOG_PERSONAL_API_KEY": "KEY",
    "POSTHOG_PROJECT_ID": "PROJECT_ID",
    "POSTHOG_BASE_URL": "BASE_URL",
    "POSTHOG_LABEL": "LABEL",
}
REQUIRED_FIELDS = ("POSTHOG_PERSONAL_API_KEY", "POSTHOG_PROJECT_ID")
# A Rundesk account suffix: uppercase words joined by single underscores, because a double
# underscore is what separates the field name from the account name.
ACCOUNT_SUFFIX_RE = re.compile(r"[A-Z0-9]+(?:_[A-Z0-9]+)*")
# Words that are part of a plain variable name, never an account name: without PERSONAL_API the
# legacy scan would read POSTHOG_PERSONAL_API_KEY as an account called `personal-api`.
RESERVED_PROFILE_WORDS = frozenset({"PERSONAL_API", "DEFAULT", "ENV"})


def normalize_profile(profile: str) -> str:
    """A profile name as an environment-variable fragment: `example-two` to `EXAMPLE_TWO`."""
    return re.sub(r"[^A-Za-z0-9]+", "_", profile or "").strip("_").upper()


def profile_label(suffix: str) -> str:
    """The inverse of `normalize_profile`, so a discovered account reads as a profile name."""
    return suffix.lower().replace("_", "-")


def env_name(profile: str, suffix: str) -> str:
    return f"POSTHOG_{normalize_profile(profile)}_{suffix}"


def is_default_profile(profile: str) -> bool:
    """Rundesk stores the default account under the plain, unsuffixed variable names."""
    normalized = normalize_profile(profile)
    if not normalized or normalized == "DEFAULT":
        return True
    return normalized == normalize_profile(os.environ.get("POSTHOG_DEFAULT_PROFILE", ""))


def missing_name(profile: str, field: str) -> str:
    """The variable an owner must set, spelled the way Rundesk stores it."""
    return field if is_default_profile(profile) else f"{field}__{normalize_profile(profile)}"


def profile_value(profile: str, field: str) -> str:
    """Read one field for one profile.

    Rundesk's `<FIELD>__<PROFILE>` wins, then this repository's `POSTHOG_<PROFILE>_<FIELD>`,
    then the plain `<FIELD>` — which belongs to the default account only, so a named account
    never pairs one region's host with another organization's key.
    """
    normalized = normalize_profile(profile)
    if normalized:
        for name in (f"{field}__{normalized}", env_name(profile, PROFILE_FIELDS[field])):
            value = os.environ.get(name, "")
            if value:
                return value
    if not is_default_profile(profile):
        return ""
    return os.environ.get(field, "")


def split_csv(value: str | None) -> list[str]:
    if not value:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


def configured_profile_names() -> list[str]:
    names = split_csv(os.environ.get("POSTHOG_PROFILES"))
    default = os.environ.get("POSTHOG_DEFAULT_PROFILE", "")
    if default and default not in names:
        names.insert(0, default)
    return names or discovered_profile_names()


def discovered_profile_names() -> list[str]:
    """Accounts present in the environment, so adding one needs no declaration.

    Both spellings are scanned: Rundesk's `<FIELD>__<ACCOUNT>` suffix and this repository's
    `POSTHOG_<PROFILE>_<FIELD>` infix.

    The plain names are one more account — the default one — listed even when only partly
    configured, so it carries its own error instead of vanishing. It is suppressed when the
    infix spelling is in use: there a plain value was a fallback shared by every profile, not
    an account of its own, and inventing one would make every command ambiguous for an owner
    whose dotenv predates Rundesk.
    """
    suffixed: set[str] = set()
    infixed: set[str] = set()
    legacy = re.compile(
        rf"^POSTHOG_({ACCOUNT_SUFFIX_RE.pattern})_({'|'.join(PROFILE_FIELDS.values())})$"
    )
    for key in os.environ:
        for field in PROFILE_FIELDS:
            prefix = f"{field}__"
            if key.startswith(prefix) and ACCOUNT_SUFFIX_RE.fullmatch(key[len(prefix):]):
                suffixed.add(profile_label(key[len(prefix):]))
        match = legacy.match(key)
        if not match:
            continue
        word = match.group(1)
        if word == "DEFAULT":
            # `<SKILL>_DEFAULT_<FIELD>` is the infix spelling of the default account, not an
            # account named `default` that resolution would then never find.
            infixed.add("default")
        elif word not in RESERVED_PROFILE_WORDS:
            infixed.add(profile_label(word))
    names = suffixed | infixed
    if not infixed and any(profile_value("", field) for field in REQUIRED_FIELDS):
        names.add(os.environ.get("POSTHOG_DEFAULT_PROFILE") or "default")
    return sorted(names)


def validate_base_url(value: str) -> str:
    """Accept only an HTTPS origin, so a self-hosted host cannot smuggle a path or credentials."""
    try:
        parsed = urllib.parse.urlsplit(value)
        parsed.port
    except ValueError as exc:
        raise PostHogError(
            f"Invalid PostHog base URL: {value!r}. Configure an HTTPS origin only."
        ) from exc

    if (
        not value
        or any(character.isspace() or ord(character) < 32 for character in value)
        or parsed.scheme.lower() != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise PostHogError(
            f"Invalid PostHog base URL: {value!r}. Configure an HTTPS origin only, without "
            f"credentials or a path, such as {' or '.join(KNOWN_REGIONS)}."
        )

    return value.rstrip("/")


def validate_project_id(value: str) -> str:
    """PostHog project paths use the numeric project identifier."""
    candidate = value.strip()
    if re.fullmatch(r"\d+", candidate):
        return candidate
    raise PostHogError(
        f"Invalid PostHog project id: {value!r}. Use the numeric project id from "
        "Settings > Project, or from the PostHog project URL."
    )


def url_origin(value: str) -> tuple[str, str, int | None]:
    parsed = urllib.parse.urlsplit(value)
    port = parsed.port
    if port is None:
        scheme = parsed.scheme.lower()
        port = 443 if scheme == "https" else 80 if scheme == "http" else None
    return parsed.scheme.lower(), (parsed.hostname or "").lower(), port


class SameOriginRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if url_origin(req.full_url) != url_origin(newurl):
            raise PostHogError("PostHog API refused an unexpected cross-origin redirect.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_url(req: urllib.request.Request, timeout: int):
    return urllib.request.build_opener(SameOriginRedirectHandler()).open(req, timeout=timeout)


def get_profile(name: str) -> Profile:
    api_key = profile_value(name, "POSTHOG_PERSONAL_API_KEY")
    project_id = profile_value(name, "POSTHOG_PROJECT_ID")
    base_url = profile_value(name, "POSTHOG_BASE_URL") or DEFAULT_BASE_URL
    label = profile_value(name, "POSTHOG_LABEL") or name

    missing = [
        missing_name(name, field)
        for field, value in (
            ("POSTHOG_PERSONAL_API_KEY", api_key),
            ("POSTHOG_PROJECT_ID", project_id),
        )
        if not value
    ]

    if missing:
        raise PostHogError(
            "Missing PostHog config: "
            + ", ".join(missing)
            + ". Run `rundesk skills configure`, add it to the secrets dotenv, or export it in "
            "the shell."
        )

    return Profile(
        name=name,
        api_key=api_key,
        project_id=validate_project_id(project_id),
        base_url=validate_base_url(base_url),
        label=label,
    )


def mask_email(match: re.Match[str]) -> str:
    """Keep enough of an address to correlate a person without printing the address."""
    local, domain = match.group(1), match.group(2)
    return f"{local[0]}***@{domain}"


def redact_sensitive(value: str) -> str:
    """Mask email local parts and drop IP addresses from human-readable output."""
    value = EMAIL_PATTERN.sub(mask_email, value)

    def replace_ip(match: re.Match[str]) -> str:
        candidate = match.group(0)
        unwrapped = (
            candidate[1:-1] if candidate.startswith("[") and candidate.endswith("]") else candidate
        )
        if "." not in unwrapped and ":" not in unwrapped:
            return candidate
        try:
            ipaddress.ip_address(unwrapped)
        except ValueError:
            return candidate
        return "[redacted-ip]"

    return IP_CANDIDATE_PATTERN.sub(replace_ip, value)


def text(value: Any, fallback: str = "-") -> str:
    if value is None:
        return fallback

    value = redact_sensitive(str(value).replace("\n", " ").strip())
    return value if value else fallback


def truncate(value: Any, limit: int = 180) -> str:
    value = text(value)
    if len(value) <= limit:
        return value

    if limit <= 3:
        return value[:limit]

    return value[: limit - 3].rstrip() + "..."


def compact_date(value: Any) -> str:
    value = text(value)
    if value == "-":
        return value

    match = re.match(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})", value)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return value.replace("T", " ").replace("Z", "")


def display_url(value: Any, limit: int = 120) -> str:
    """Print an origin and path only: a captured URL's query string carries tokens and PII."""
    raw = text(value)
    if raw == "-":
        return raw
    parsed = urllib.parse.urlsplit(raw)
    if not parsed.scheme or not parsed.netloc:
        return truncate(raw.split("?", 1)[0], limit)
    trimmed = urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
    return truncate(trimmed, limit)


def line(pairs: list[tuple[str, str]]) -> str:
    return "- " + " | ".join(f"{key}={value}" for key, value in pairs)


def note(message: str) -> None:
    """Operational warnings and truncation never contaminate the parsed stdout stream."""
    print(message, file=sys.stderr)


def require_same_origin(profile: Profile, url: str) -> str:
    """A follow-on URL PostHog handed back still has to be this profile's own HTTPS origin."""
    if url_origin(url) != url_origin(profile.base_url):
        raise PostHogError(
            f"Refusing to follow a PostHog URL outside the configured origin: {url!r}."
        )
    return url


def request_url(
    profile: Profile,
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    retries: int = 2,
) -> tuple[Any, dict[str, str]]:
    require_same_origin(profile, url)

    body = None
    headers = {
        "Authorization": f"Bearer {profile.api_key}",
        "Accept": "application/json",
        "User-Agent": "workspace-posthog/1.0",
    }

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    for attempt in range(retries + 1):
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with open_url(req, timeout=REQUEST_TIMEOUT) as response:
                body_bytes = response.read(MAX_RESPONSE_BYTES + 1)
                if len(body_bytes) > MAX_RESPONSE_BYTES:
                    raise PostHogError(
                        f"PostHog response exceeded {MAX_RESPONSE_BYTES} bytes "
                        f"profile={profile.name}. Narrow the read."
                    )
                raw = body_bytes.decode("utf-8", errors="replace")
                try:
                    data = json.loads(raw) if raw else None
                except json.JSONDecodeError as exc:
                    raise PostHogError(
                        f"PostHog returned a non-JSON body profile={profile.name}: "
                        f"{truncate(raw, 200)}"
                    ) from exc
                return data, dict(response.headers)
        except urllib.error.HTTPError as exc:
            raw = exc.read(MAX_RESPONSE_BYTES + 1)[:MAX_RESPONSE_BYTES].decode(
                "utf-8", errors="replace"
            )
            # PostHog rate-limits personal API keys per key and per endpoint family; only a
            # read is safe to repeat.
            if method in ("GET", "POST") and exc.code == 429 and attempt < retries:
                retry_after = exc.headers.get("Retry-After")
                delay = int(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
                time.sleep(min(delay, 30))
                continue
            raise PostHogError(describe_api_error(profile, exc.code, raw)) from exc
        except urllib.error.URLError as exc:
            raise PostHogError(
                f"PostHog API request failed profile={profile.name}: {exc.reason}"
            ) from exc

    raise PostHogError(f"PostHog API request exhausted retries profile={profile.name}")


def describe_api_error(profile: Profile, status: int, raw: str) -> str:
    """PostHog errors are `{type, code, detail, attr}`; a proxy or gateway sends anything."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = None

    if isinstance(data, dict):
        detail = data.get("detail") or data.get("error") or data.get("message") or raw[:300]
        parts = [f"PostHog API {status} profile={profile.name}: {truncate(detail, 300)}"]
        kind = data.get("type")
        code = data.get("code")
        if kind or code:
            parts.append(f"(type={text(kind, '-')} code={text(code, '-')})")
        if status == 403:
            parts.append(
                "A 403 from a personal API key is a missing scope or a project the key does "
                "not cover, not missing data."
            )
        return " ".join(parts)

    return f"PostHog API {status} profile={profile.name}: {truncate(raw[:300], 300)}"


def request(
    profile: Profile,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    retries: int = 2,
) -> tuple[Any, dict[str, str]]:
    url = profile.base_url + "/api/" + path.lstrip("/")
    if params:
        clean = {key: value for key, value in params.items() if value not in (None, "")}
        if clean:
            url += "?" + urllib.parse.urlencode(clean, doseq=True)
    return request_url(profile, method, url, payload=payload, retries=retries)


def project_path(profile: Profile, suffix: str) -> str:
    return f"projects/{profile.project_id}/{suffix.lstrip('/')}"


def page_results(data: Any, path: str) -> list[dict[str, Any]]:
    """Validate the envelope before trusting it: a proxy login page is also valid JSON."""
    if not isinstance(data, dict):
        raise PostHogError(f"Unexpected PostHog response for /api/{path}: expected an object.")
    results = data.get("results")
    if not isinstance(results, list):
        raise PostHogError(
            f"Unexpected PostHog response for /api/{path}: no `results` list in the payload."
        )
    if any(not isinstance(item, dict) for item in results):
        raise PostHogError(
            f"Unexpected PostHog response for /api/{path}: `results` contains a non-object item."
        )
    return results


def paginate(
    profile: Profile,
    path: str,
    params: dict[str, Any] | None,
    limit: int,
    max_pages: int = MAX_PAGES,
) -> tuple[list[dict[str, Any]], bool]:
    """Collect at most `limit` records across at most `max_pages` pages.

    Returns the records and whether PostHog still had more, so the caller can say so rather
    than presenting a bounded read as a complete one.
    """
    query = dict(params or {})
    query["limit"] = min(limit, MAX_LIMIT)

    collected: list[dict[str, Any]] = []
    data, _ = request(profile, "GET", path, params=query)
    pages = 1

    while True:
        collected.extend(page_results(data, path))
        next_url = data.get("next") if isinstance(data, dict) else None
        if (
            len(collected) >= limit
            or pages >= max_pages
            or not isinstance(next_url, str)
            or not next_url
        ):
            break
        data, _ = request_url(profile, "GET", require_same_origin(profile, next_url))
        pages += 1

    remaining = bool(isinstance(data, dict) and (data.get("next") or data.get("has_next")))
    return collected[:limit], len(collected) > limit or remaining


def report_truncation(more: bool, shown: int, limit: int, hint: str = "") -> None:
    if not more:
        return
    message = (
        f"truncated: showed {shown} record(s) at --limit {limit}; PostHog has more. "
        "Treat this as a partial answer."
    )
    note(message + (f" {hint}" if hint else ""))


# Comments and quoted literals are removed before the guard reads a statement, so a query that
# merely mentions `delete` inside a string is not refused and a `--` inside a string is not
# mistaken for a comment. String alternatives come first so they win that overlap.
SQL_SKELETON_PATTERN = re.compile(
    r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"|`[^`]*`|--[^\n]*|/\*.*?\*/",
    re.S,
)
FORBIDDEN_SQL_KEYWORDS = (
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE", "TRUNCATE",
    "GRANT", "REVOKE", "ATTACH", "DETACH", "RENAME", "OPTIMIZE", "SYSTEM", "KILL",
)


def sql_skeleton(sql: str) -> str:
    return SQL_SKELETON_PATTERN.sub(" ", sql)


def validate_hogql(sql: str) -> str:
    """Refuse anything but a single read statement.

    PostHog's query endpoint is read-only on its own; this guard exists so a confused turn
    fails locally with an explanation instead of sending a write-shaped statement at all.
    """
    statement = sql.strip()
    if not statement:
        raise PostHogError("Empty --sql. Pass a single HogQL SELECT statement.")

    skeleton = sql_skeleton(statement)
    if not re.match(r"\s*(?:SELECT|WITH)\b", skeleton, re.IGNORECASE):
        raise PostHogError("Refusing --sql: a HogQL read must start with SELECT or WITH.")

    for keyword in FORBIDDEN_SQL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", skeleton, re.IGNORECASE):
            raise PostHogError(
                f"Refusing --sql: it contains the write or DDL keyword {keyword}. "
                "This package reads PostHog and never changes it."
            )

    if ";" in skeleton.rstrip().rstrip(";"):
        raise PostHogError("Refusing --sql: pass exactly one statement, without extra `;`.")

    return statement.rstrip().rstrip(";").rstrip()


def top_level_limit(sql: str) -> tuple[int, bool] | None:
    """Return a statement-level LIMIT and whether it is the per-group `LIMIT n BY` form."""
    skeleton = sql_skeleton(sql)
    depth = 0
    tokens = re.finditer(r"\(|\)|\bLIMIT\s+(\d+)\b", skeleton, re.IGNORECASE)
    for token in tokens:
        if token.group(0) == "(":
            depth += 1
        elif token.group(0) == ")":
            depth = max(0, depth - 1)
        elif depth == 0:
            tail = skeleton[token.end():]
            return int(token.group(1)), bool(re.match(r"\s+BY\b", tail, re.IGNORECASE))
    return None


def ensure_limit(sql: str, limit: int) -> str:
    """Append a statement bound or reject one that is larger or only per-group."""
    explicit = top_level_limit(sql)
    if explicit:
        requested, per_group = explicit
        if per_group:
            raise PostHogError(
                "Refusing --sql: LIMIT n BY is a per-group limit, not a total result bound."
            )
        if requested > limit:
            raise PostHogError(
                f"Refusing --sql: its LIMIT {requested} exceeds the command limit {limit}."
            )
        return sql
    return f"{sql} LIMIT {limit}"


def run_hogql(
    profile: Profile, sql: str, limit: int, name: str
) -> tuple[dict[str, Any], bool]:
    payload = {
        "query": {"kind": "HogQLQuery", "query": ensure_limit(sql, limit)},
        "name": name,
    }
    data, _ = request(profile, "POST", project_path(profile, "query/"), payload=payload)
    if not isinstance(data, dict):
        raise PostHogError("Unexpected PostHog query response: expected an object.")
    results = data.get("results")
    if not isinstance(results, list):
        raise PostHogError(
            "Unexpected PostHog query response: no `results` list in the payload."
        )
    bounded_data = dict(data)
    bounded_data["results"] = results[:limit]
    return bounded_data, len(results) > limit


def query_rows(data: dict[str, Any]) -> tuple[list[str], list[list[Any]]]:
    columns = data.get("columns")
    columns = [str(name) for name in columns] if isinstance(columns, list) else []
    rows = [row if isinstance(row, list) else [row] for row in data.get("results", [])]
    return columns, rows


def bounded(value: int, name: str, minimum: int, maximum: int) -> int:
    if value < minimum or value > maximum:
        raise PostHogError(f"{name} must be between {minimum} and {maximum}; got {value}.")
    return value


def validate_timestamp(value: str | None, option: str) -> str | None:
    if value in (None, ""):
        return None
    if not ISO_TIMESTAMP_PATTERN.fullmatch(value.strip()):
        raise PostHogError(
            f"{option} must be an ISO 8601 date or timestamp, such as 2026-08-01 or "
            f"2026-08-01T12:00:00Z; got {value!r}."
        )
    return value.strip()


def timestamp_value(value: str) -> datetime.datetime:
    """One accepted `--after`/`--before` spelling as a UTC instant.

    A bare date or a naive timestamp is read as UTC, so a window means the same thing whatever
    the project's own timezone is. `fromisoformat` on the Python 3.9 floor rejects the compact
    `+HHMM` offset the option pattern accepts, so widen it here rather than let a valid input
    escape as a traceback.
    """
    normalized = value.strip().replace("Z", "+00:00")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
        normalized += "T00:00:00+00:00"
    elif "T" not in normalized and " " in normalized:
        normalized = normalized.replace(" ", "T", 1)
    normalized = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", normalized)
    try:
        parsed = datetime.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise PostHogError(
            f"Unsupported timestamp {value!r}. Use an ISO 8601 date or timestamp, such as "
            "2026-08-01 or 2026-08-01T12:00:00Z."
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def validate_window(after: str | None, before: str | None) -> tuple[str | None, str | None]:
    after_value = validate_timestamp(after, "--after")
    before_value = validate_timestamp(before, "--before")
    if after_value and before_value:
        if timestamp_value(after_value) >= timestamp_value(before_value):
            raise PostHogError("--after must be earlier than --before.")
        if timestamp_value(before_value) - timestamp_value(after_value) > datetime.timedelta(days=365):
            raise PostHogError("The PostHog event window must be shorter than one year.")
    return after_value, before_value


def days_ago(days: int) -> str:
    moment = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def profile_names_for_args(args: argparse.Namespace) -> list[str]:
    names = configured_profile_names()
    if args.profile and args.all_profiles:
        raise PostHogError("Choose --profile or --all-profiles, not both.")
    if args.profile:
        return [args.profile]
    if args.all_profiles:
        if not names:
            raise PostHogError("No PostHog profiles are configured.")
        return names
    if len(names) == 1:
        return names
    if len(names) > 1:
        raise PostHogError(
            "Multiple PostHog profiles are configured. Pass --profile <name> or --all-profiles."
        )
    raise PostHogError(
        "No PostHog profile is configured. Run `rundesk skills configure`, or set the required "
        "environment values."
    )


def selected_profile_name(args: argparse.Namespace) -> str:
    """Compatibility helper used by catalog-level profile tests and simple callers."""
    names = configured_profile_names()
    if args.profile:
        return args.profile
    if len(names) == 1:
        return names[0]
    if len(names) > 1:
        raise PostHogError(
            "Multiple PostHog profiles are configured. Pass --profile <name> or --all-profiles."
        )
    raise PostHogError("No PostHog profile is configured.")


def profile_summary(name: str) -> dict[str, Any]:
    missing = [
        field
        for field in REQUIRED_FIELDS
        if not profile_value(name, field)
    ]
    base_url = profile_value(name, "POSTHOG_BASE_URL") or DEFAULT_BASE_URL
    try:
        base_url = validate_base_url(base_url)
    except PostHogError:
        base_url = "invalid"
    return {
        "profile": name,
        "label": profile_value(name, "POSTHOG_LABEL") or name,
        "project_id": profile_value(name, "POSTHOG_PROJECT_ID") or "-",
        "base_url": base_url,
        "configured": not missing,
        "missing": missing,
    }


def emit_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str))


def output_value(key: str, value: Any) -> str:
    lowered = key.lower()
    if "url" in lowered or lowered in {"href", "referrer", "referring_domain"}:
        return display_url(value)
    if isinstance(value, (dict, list)):
        return truncate(json.dumps(value, ensure_ascii=False, sort_keys=True), 220)
    return truncate(value)


def emit_records(records: list[dict[str, Any]], fields: tuple[str, ...], profile: str) -> None:
    for record in records:
        pairs: list[tuple[str, str]] = [("profile", profile)]
        for field in fields:
            if field in record:
                pairs.append((field, output_value(field, record.get(field))))
        print(line(pairs))


def emit_query(data: dict[str, Any], profile: str, raw_json: bool) -> None:
    if raw_json:
        emit_json(data)
        return
    columns, rows = query_rows(data)
    if columns:
        print("- " + " | ".join(columns))
    for row in rows:
        pairs = [(columns[index] if index < len(columns) else f"column_{index + 1}", value)
                 for index, value in enumerate(row)]
        print(line([("profile", profile), *[(key, output_value(key, value)) for key, value in pairs]]))


def event_definition_records(profile: Profile, args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    params: dict[str, Any] = {
        "names": args.name,
        "exclude_hidden": "true" if args.exclude_hidden else None,
        "exclude_stale": "true" if args.exclude_stale else None,
    }
    return paginate(profile, project_path(profile, "event_definitions/"), params, args.limit)


def event_records(profile: Profile, args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    after, before = validate_window(args.after, args.before)
    params = {
        "event": args.event,
        "distinct_id": args.distinct_id,
        "person_id": args.person_id,
        "after": after,
        "before": before,
        "include_person": "true" if args.include_person else None,
        "select": args.select,
    }
    note("warning: PostHog marks the direct events endpoint for future removal; prefer query or analytics.")
    return paginate(profile, project_path(profile, "events/"), params, args.limit)


def person_records(profile: Profile, args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    params = {
        "search": args.search,
        "email": args.email,
        "distinct_id": args.distinct_id,
    }
    return paginate(profile, project_path(profile, "persons/"), params, args.limit)


def recording_records(profile: Profile, args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    params = {"offset": args.offset}
    return paginate(profile, project_path(profile, "session_recordings/"), params, args.limit)


def insight_records(profile: Profile, args: argparse.Namespace) -> tuple[list[dict[str, Any]], bool]:
    params = {
        "search": args.search,
        "insight": args.type,
        "date_from": args.date_from,
        "date_to": args.date_to,
    }
    return paginate(profile, project_path(profile, "insights/"), params, args.limit)


def web_analytics(profile: Profile, args: argparse.Namespace) -> Any:
    days = bounded(args.days, "--days", 1, MAX_DAYS)
    params = {"days": days, "compare": "true" if args.compare else "false"}
    data, _ = request(profile, "GET", project_path(profile, "web_analytics/recap/"), params=params)
    if not isinstance(data, dict):
        raise PostHogError("Unexpected PostHog web analytics response: expected an object.")
    return data


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def sql_timestamp(value: str) -> str:
    """One window bound as an explicitly UTC HogQL expression.

    HogQL reads an unqualified `toDateTime('...')` literal in the project's own timezone, so a
    UTC clock reading pasted in bare shifts the window by that project's offset and quietly
    answers a different question. An offset-bearing input also has to be converted rather than
    concatenated, because ClickHouse cannot parse `'2026-08-01 12:00:00+02:00'` at all.
    """
    moment = timestamp_value(value)
    return f"toDateTime({sql_literal(moment.strftime('%Y-%m-%d %H:%M:%S'))}, 'UTC')"


def analytics_window(args: argparse.Namespace, include_event: bool = True) -> str:
    after, before = validate_window(args.after, args.before)
    after = after or days_ago(bounded(args.days, "--days", 1, MAX_DAYS))
    if before and timestamp_value(after) >= timestamp_value(before):
        raise PostHogError("--after must be earlier than --before.")
    clauses = [f"timestamp >= {sql_timestamp(after)}"]
    if before:
        clauses.append(f"timestamp < {sql_timestamp(before)}")
    if include_event and args.event:
        values = ", ".join(sql_literal(event) for event in args.event)
        clauses.append(f"event IN ({values})")
    return " AND ".join(clauses)


def analytics_sql(args: argparse.Namespace) -> str:
    window = analytics_window(args)
    limit = args.limit
    if args.mode == "trends":
        return (
            "SELECT toDate(timestamp) AS day, count() AS events, uniq(distinct_id) AS visitors "
            f"FROM events WHERE {window} GROUP BY day ORDER BY day LIMIT {limit}"
        )
    if args.mode == "traffic":
        if args.event:
            raise PostHogError(
                "analytics traffic always reads $pageview; omit --event because it cannot be applied."
            )
        window = analytics_window(args, include_event=False)
        return (
            "SELECT properties.$current_url AS url, properties.$referring_domain AS referring_domain, "
            "count() AS pageviews, uniq(distinct_id) AS visitors "
            f"FROM events WHERE event = '$pageview' AND {window} "
            f"GROUP BY url, referring_domain ORDER BY pageviews DESC LIMIT {limit}"
        )
    if args.mode == "audiences":
        return (
            "SELECT distinct_id, any(coalesce(person.properties.email, properties.email)) AS email, "
            "uniq(event) AS event_types, "
            "count() AS events "
            f"FROM events WHERE {window} GROUP BY distinct_id ORDER BY events DESC LIMIT {limit}"
        )
    if args.mode == "leads":
        if len(args.event) != 1:
            raise PostHogError("analytics leads requires exactly one --event, such as --event lead.")
        return (
            "SELECT coalesce(person.properties.email, properties.email) AS email, "
            "count() AS lead_events, uniq(distinct_id) AS leads "
            f"FROM events WHERE {window} GROUP BY email ORDER BY lead_events DESC LIMIT {limit}"
        )
    if args.mode == "conversion":
        if len(args.event) < 2:
            raise PostHogError(
                "analytics conversion requires at least two --event values, such as "
                "--event signup --event purchase."
            )
        return (
            "SELECT event, count() AS conversions, uniq(distinct_id) AS people "
            f"FROM events WHERE {window} GROUP BY event ORDER BY conversions DESC LIMIT {limit}"
        )
    raise PostHogError(f"Unknown analytics mode: {args.mode}")


def add_profile_options(command: argparse.ArgumentParser) -> None:
    command.add_argument("--profile", help="configured PostHog profile")
    command.add_argument("--all-profiles", action="store_true", help="read every configured profile")
    command.add_argument("--json", action="store_true", help="emit raw JSON")


def add_limit(command: argparse.ArgumentParser, default: int = 25) -> None:
    command.add_argument("--limit", type=int, default=default, help=f"maximum records to show (default {default})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read bounded PostHog project analytics.")
    parser.add_argument("--env-file", help="explicit dotenv path")
    sub = parser.add_subparsers(dest="command", required=True)

    profiles = sub.add_parser("profiles", help="list configured profiles without network access")
    profiles.add_argument("--json", action="store_true", help="emit JSON")

    definitions = sub.add_parser("event-definitions", help="list tracked event definitions")
    add_profile_options(definitions)
    definitions.add_argument("--name", action="append", help="filter by one or more event names")
    definitions.add_argument("--exclude-hidden", action="store_true")
    definitions.add_argument("--exclude-stale", action="store_true")
    add_limit(definitions)

    events = sub.add_parser("events", help="list bounded events (legacy endpoint)")
    add_profile_options(events)
    events.add_argument("--event")
    events.add_argument("--distinct-id")
    events.add_argument("--person-id")
    events.add_argument("--after")
    events.add_argument("--before")
    events.add_argument("--include-person", action="store_true")
    events.add_argument("--select", action="append")
    add_limit(events)

    persons = sub.add_parser("persons", help="list persons")
    add_profile_options(persons)
    persons.add_argument("--search")
    persons.add_argument("--email")
    persons.add_argument("--distinct-id")
    add_limit(persons)

    recordings = sub.add_parser("recordings", help="list session recording metadata")
    add_profile_options(recordings)
    recordings.add_argument("--offset", type=int, default=0)
    add_limit(recordings, 10)

    web = sub.add_parser("web", help="retrieve web analytics recap")
    add_profile_options(web)
    web.add_argument("--days", type=int, default=7)
    web.add_argument("--compare", action=argparse.BooleanOptionalAction, default=True)

    insights = sub.add_parser("insights", help="list saved insights")
    add_profile_options(insights)
    insights.add_argument("--search")
    insights.add_argument("--type", choices=("FUNNELS", "JOURNEYS", "JSON", "LIFECYCLE", "PATHS", "RETENTION", "SQL", "STICKINESS", "TRENDS"))
    insights.add_argument("--date-from")
    insights.add_argument("--date-to")
    add_limit(insights)

    insight = sub.add_parser("insight", help="retrieve one saved insight")
    add_profile_options(insight)
    insight.add_argument("insight_id")

    query = sub.add_parser("query", help="run one bounded read-only HogQL query")
    add_profile_options(query)
    query.add_argument("--sql", required=True)
    query.add_argument("--name", default="rundesk posthog query")
    add_limit(query, 100)

    analytics = sub.add_parser("analytics", help="run a common analytics query preset")
    add_profile_options(analytics)
    analytics.add_argument("mode", choices=("trends", "traffic", "audiences", "leads", "conversion"))
    analytics.add_argument("--event", action="append", default=[])
    analytics.add_argument("--after")
    analytics.add_argument("--before")
    analytics.add_argument("--days", type=int, default=7)
    add_limit(analytics, 100)
    return parser


def run_command(args: argparse.Namespace) -> int:
    if args.command == "profiles":
        records = [profile_summary(name) for name in configured_profile_names()]
        if args.json:
            emit_json(records)
        elif not records:
            print("No PostHog profiles configured.")
        else:
            for record in records:
                missing = ",".join(record["missing"]) if record["missing"] else "-"
                print(line([(key, output_value(key, value)) for key, value in (
                    ("profile", record["profile"]), ("label", record["label"]),
                    ("project_id", record["project_id"]), ("base_url", record["base_url"]),
                    ("configured", record["configured"]), ("missing", missing),
                )]))
        return 0

    profiles = [get_profile(name) for name in profile_names_for_args(args)]
    if args.command == "web":
        for profile in profiles:
            data = web_analytics(profile, args)
            if args.json:
                emit_json({"profile": profile.name, "data": data})
            else:
                print(line([
                    ("profile", profile.name),
                    *[(key, output_value(key, value)) for key, value in data.items()],
                ]))
        return 0
    if args.command == "insight":
        for profile in profiles:
            data, _ = request(profile, "GET", project_path(profile, f"insights/{urllib.parse.quote(args.insight_id, safe='')}"))
            if not isinstance(data, dict):
                raise PostHogError("Unexpected PostHog insight response: expected an object.")
            if args.json:
                emit_json({"profile": profile.name, "data": data})
            else:
                emit_records([data], tuple(data.keys()), profile.name)
        return 0
    if args.command in {"query", "analytics"}:
        for profile in profiles:
            if args.command == "query":
                sql = validate_hogql(args.sql)
                if len(args.name) > MAX_QUERY_NAME:
                    raise PostHogError(
                        f"--name must be at most {MAX_QUERY_NAME} characters; got {len(args.name)}."
                    )
                limit = bounded(args.limit, "--limit", 1, MAX_LIMIT)
                data, more = run_hogql(profile, sql, limit, args.name)
            else:
                sql = analytics_sql(args)
                limit = bounded(args.limit, "--limit", 1, MAX_LIMIT)
                data, more = run_hogql(profile, sql, limit, f"rundesk analytics {args.mode}")
            emit_query(data, profile.name, args.json)
            report_truncation(more, len(data["results"]), limit)
        return 0

    limit = bounded(args.limit, "--limit", 1, MAX_LIMIT)
    for profile in profiles:
        if args.command == "event-definitions":
            records, more = event_definition_records(profile, args)
            fields = ("id", "name", "description", "verified", "hidden", "last_seen_at")
        elif args.command == "events":
            records, more = event_records(profile, args)
            fields = ("id", "event", "distinct_id", "timestamp", "properties", "person")
        elif args.command == "persons":
            records, more = person_records(profile, args)
            fields = ("id", "distinct_ids", "name", "email", "properties", "created_at", "last_seen_at")
        elif args.command == "recordings":
            if args.offset < 0:
                raise PostHogError("--offset must be zero or greater.")
            records, more = recording_records(profile, args)
            fields = ("id", "distinct_id", "start_time", "end_time", "recording_duration", "start_url")
        elif args.command == "insights":
            records, more = insight_records(profile, args)
            fields = ("id", "short_id", "name", "query_type", "created_at", "last_viewed_at")
        else:
            raise PostHogError(f"Unknown command: {args.command}")
        if args.json:
            emit_json({"profile": profile.name, "results": records, "truncated": more})
        else:
            emit_records(records, fields, profile.name)
            report_truncation(more, len(records), limit)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    load_dotenv(resolve_env_file(args.env_file))
    try:
        return run_command(args)
    except PostHogError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
