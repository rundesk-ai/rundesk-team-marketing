#!/usr/bin/env python3
"""Bounded, read-only access to Google PageSpeed Insights."""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


SKILL = "GOOGLE_PAGESPEED_INSIGHTS"
API_KEY = f"{SKILL}_API_KEY"
LABEL = f"{SKILL}_LABEL"
API_URL = "https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed"
PROFILE_RE = re.compile(r"[A-Z0-9]+(?:_[A-Z0-9]+)*")
# The CLI keeps Google's lowercase Lighthouse identifiers, which are also the response keys, while
# the query string must carry the uppercase enums from the v5 discovery document.
STRATEGIES = {"mobile": "MOBILE", "desktop": "DESKTOP"}
CATEGORIES = {
    "performance": "PERFORMANCE",
    "accessibility": "ACCESSIBILITY",
    "best-practices": "BEST_PRACTICES",
    "seo": "SEO",
}
METRICS = {
    "first-contentful-paint": "first_contentful_paint",
    "largest-contentful-paint": "largest_contentful_paint",
    "speed-index": "speed_index",
    "total-blocking-time": "total_blocking_time",
    "cumulative-layout-shift": "cumulative_layout_shift",
    "interaction-to-next-paint": "interaction_to_next_paint",
}
# Field data is the Chrome UX Report summary runPagespeed already returns beside the lab run.
# `loadingExperience` is asked about the requested page and `originLoadingExperience` about the whole
# origin, so each is reported under the scope it was requested for, never merged.
FIELD_SCOPES = (("url", "loadingExperience"), ("origin", "originLoadingExperience"))
# The v5 reference documents the metrics map key only as `(key)`, so the raw key is reported on every
# row and an unrecognized key is passed through lowercased instead of dropped. A display name is only
# shared with a lab metric where the two measure the same quantity in the same unit.
MILLISECONDS = "milliseconds"
# CUMULATIVE_LAYOUT_SHIFT_SCORE is typed as an integer while Lighthouse reports CLS as a unitless
# ratio, and no Google page states the relationship. The name and unit keep the raw integer from
# being read as a Lighthouse CLS value; nothing is rescaled.
API_INTEGER = "api_integer"
API_VALUE = "api_value"
FIELD_METRICS = {
    "FIRST_CONTENTFUL_PAINT_MS": ("first_contentful_paint", MILLISECONDS),
    "LARGEST_CONTENTFUL_PAINT_MS": ("largest_contentful_paint", MILLISECONDS),
    "CUMULATIVE_LAYOUT_SHIFT_SCORE": ("cumulative_layout_shift_score_raw", API_INTEGER),
    "INTERACTION_TO_NEXT_PAINT": ("interaction_to_next_paint", MILLISECONDS),
    "FIRST_INPUT_DELAY_MS": ("first_input_delay", MILLISECONDS),
    "EXPERIMENTAL_TIME_TO_FIRST_BYTE": ("experimental_time_to_first_byte", MILLISECONDS),
}
FIELD_CATEGORIES = ("FAST", "AVERAGE", "SLOW", "NONE")
# Both scopes at their documented six metrics with three buckets each come to fifty rows, so the
# default holds a complete current response while still bounding a response that grows.
FIELD_LIMIT_DEFAULT = 100
FIELD_LIMIT_MAXIMUM = 500
# Returned proportions are rounded, so their total is checked with room for that rounding only.
DISTRIBUTION_TOLERANCE = 0.02
LAB_COLUMNS = ["row_type", "category", "metric", "audit", "title", "score", "value",
               "numeric_value", "display_value", "weight"]
FIELD_COLUMNS = ["requested_scope", "effective_scope", "origin_fallback", "field_id",
                 "field_metric_key", "unit", "percentile", "field_category"]
DISTRIBUTION_COLUMNS = ["bucket_min", "bucket_max", "proportion"]
CONTEXT_COLUMNS = ["requested_url", "final_url", "strategy", "fetch_time", "lighthouse_version",
                   "profile"]


class PageSpeedError(RuntimeError):
    pass


@dataclass(frozen=True)
class Profile:
    name: str
    api_key: str = field(repr=False)
    label: str


def env_candidates() -> list[Path]:
    paths: list[Path] = []
    for key in (f"{SKILL}_ENV_FILE", "RUNDESK_INTEGRATIONS_ENV"):
        if os.environ.get(key):
            paths.append(Path(os.environ[key]).expanduser())
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")).expanduser()
    paths.extend([
        xdg / "rundesk" / "integrations" / "google-pagespeed-insights" / "env",
        xdg / "google-pagespeed-insights" / "env",
    ])
    return paths


def resolve_env_file(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    for path in env_candidates():
        if path.is_file():
            return path
    return env_candidates()[-1]


def load_dotenv(path: Path, *, required: bool = False) -> None:
    if not path.exists():
        if required:
            raise PageSpeedError(f"Environment file does not exist: {path}")
        return
    try:
        mode = path.stat().st_mode & 0o777
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise PageSpeedError(f"Cannot read environment file {path}: {exc.strerror or exc}") from exc
    if mode & 0o077:
        print(f"WARNING: dotenv file {path} is accessible by group or others; use chmod 600.", file=sys.stderr)
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) and key not in os.environ:
            os.environ[key] = value


def normalize(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").upper()


def is_default(name: str) -> bool:
    return normalize(name) in ("", "DEFAULT")


def profile_value(name: str, field: str) -> str:
    suffix = normalize(name)
    if not is_default(name):
        return os.environ.get(f"{field}__{suffix}", "")
    return os.environ.get(field, "")


def discovered_profiles() -> list[str]:
    explicit = [item.strip() for item in os.environ.get(f"{SKILL}_PROFILES", "").split(",") if item.strip()]
    default = os.environ.get(f"{SKILL}_DEFAULT_PROFILE", "")
    if default and default not in explicit:
        explicit.insert(0, default)
    if explicit:
        return explicit
    names = {
        key[len(API_KEY) + 2:].lower().replace("_", "-")
        for key in os.environ
        if key.startswith(f"{API_KEY}__") and PROFILE_RE.fullmatch(key[len(API_KEY) + 2:])
    }
    if os.environ.get(API_KEY):
        names.add("default")
    return sorted(names)


def get_profile(name: str) -> Profile:
    if name and not normalize(name):
        raise PageSpeedError("Profile names must contain at least one letter or digit.")
    api_key = profile_value(name, API_KEY)
    if not api_key:
        missing = API_KEY if is_default(name) else f"{API_KEY}__{normalize(name)}"
        raise PageSpeedError(f"Missing required configuration: {missing}. Run rundesk skills configure for this skill.")
    return Profile(name, api_key, profile_value(name, LABEL) or name)


def selected_profile(args: argparse.Namespace) -> Profile:
    names = discovered_profiles()
    if args.profile:
        return get_profile(args.profile)
    if not names:
        raise PageSpeedError("No configured PageSpeed Insights profiles. Run rundesk skills configure for this skill.")
    if len(names) != 1:
        raise PageSpeedError("Multiple profiles are configured; select one with --profile: " + ", ".join(names))
    return get_profile(names[0])


class RejectRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Keep the API key on the expected Google request boundary."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def open_url(request: urllib.request.Request, timeout: int = 60):
    return urllib.request.build_opener(RejectRedirectHandler()).open(request, timeout=timeout)


def expect_object(value: Any, noun: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PageSpeedError(f"Google returned a malformed {noun}.")
    return value


def expect_list(container: dict[str, Any], key: str, noun: str) -> list[Any]:
    value = container.get(key, [])
    if not isinstance(value, list):
        raise PageSpeedError(f"Google returned a malformed {noun} collection.")
    return value


def expect_objects(container: dict[str, Any], key: str, noun: str) -> list[dict[str, Any]]:
    return [expect_object(item, noun) for item in expect_list(container, key, noun)]


def expect_text(container: dict[str, Any], key: str, noun: str) -> str:
    value = container.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise PageSpeedError(f"Google returned a malformed {noun}.")
    return value


def optional_number(container: dict[str, Any], key: str, noun: str) -> int | float | None:
    """Absent stays absent; anything kept must survive rounding, sorting, and RFC 8259 emission."""
    value = container.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PageSpeedError(f"Google returned a malformed {noun}.")
    if not math.isfinite(value):
        raise PageSpeedError(f"Google returned a non-finite {noun}.")
    return value


def optional_flag(container: dict[str, Any], key: str, noun: str) -> bool | None:
    """`None` only for an absent flag, the boolean for a reported one, a refusal for anything else.

    Keeping absent distinct from false in code is what lets a caller decide the meaning of silence
    without confusing it with a value Google sent in the wrong type.

    **Absent and explicitly null are two different answers.** Google omits a flag it has nothing to
    say about; a literal `null` is a payload that said something, and what it said is not a
    boolean. Read alike, a malformed response arrives as the ordinary case and is reported as a
    confident `false` — the one reading nobody would question.
    """
    if key not in container:
        return None
    if not isinstance(container[key], bool):
        raise PageSpeedError(f"Google returned a malformed {noun}.")
    return container[key]


def fallback_text(value: bool | None) -> str:
    """Google omits origin_fallback unless it is true, so absent and false both mean not a fallback."""
    return "true" if value is True else "false"


def expect_category(container: dict[str, Any], key: str, noun: str) -> str:
    """An unlisted value would be reported as though it were a real classification."""
    value = expect_text(container, key, noun)
    if value and value not in FIELD_CATEGORIES:
        raise PageSpeedError(f"Google returned an unknown {noun}: {value}.")
    return value


def check_buckets(buckets: list[tuple[Any, Any, Any]], noun: str) -> None:
    """A distribution is only readable if its buckets tile a range once and account for everyone.

    An absent or empty list stays acceptable; a list Google did send must be complete, because a
    partial one silently understates how many experiences were poor.
    """
    if not buckets:
        return
    total = 0.0
    previous_max = None
    for index, (minimum, maximum, proportion) in enumerate(buckets):
        if proportion is None:
            raise PageSpeedError(f"Google returned a {noun} bucket without a proportion.")
        if not 0 <= proportion <= 1:
            raise PageSpeedError(f"Google returned a {noun} proportion outside 0 to 1: {proportion}.")
        total += proportion
        # Ordering and overlap cannot be judged without a lower bound, so one is required here.
        if minimum is None:
            raise PageSpeedError(f"Google returned a {noun} bucket without a minimum.")
        if minimum < 0 or (maximum is not None and maximum < 0):
            raise PageSpeedError(f"Google returned a negative {noun} bound.")
        # Only the final bucket may be open ended, which also allows at most one of them.
        if maximum is None and index != len(buckets) - 1:
            raise PageSpeedError(f"Google returned an open-ended {noun} bucket before the last one.")
        if maximum is not None and maximum < minimum:
            raise PageSpeedError(f"Google returned a {noun} bucket ending before it starts.")
        if previous_max is not None and minimum < previous_max:
            raise PageSpeedError(f"Google returned overlapping or unordered {noun} buckets.")
        previous_max = maximum
    if abs(total - 1) > DISTRIBUTION_TOLERANCE:
        raise PageSpeedError(f"Google returned {noun} proportions totalling {total:.4f} rather than 1.")


def refuse_non_finite(token: str) -> float:
    raise PageSpeedError(f"Google returned the non-finite JSON value {token}.")


def request_json(params: list[tuple[str, str]], opener: Callable[..., Any] | None = None) -> dict[str, Any]:
    # Resolving the opener per call keeps open_url patchable; a default bound it at import time.
    opener = opener or open_url
    request = urllib.request.Request(API_URL + "?" + urllib.parse.urlencode(params), method="GET")
    api_key = next((value for name, value in params if name == "key"), "")
    try:
        with opener(request, timeout=60) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            message = json.loads(detail).get("error", {}).get("message", "")
        except (ValueError, AttributeError):
            message = ""
        if api_key:
            message = message.replace(api_key, "[REDACTED]")
        raise PageSpeedError(f"Google API request failed with HTTP {exc.code}" + (f": {message}" if message else ".")) from exc
    except urllib.error.URLError as exc:
        raise PageSpeedError(f"Google API request failed: {exc.reason}") from exc
    if not payload:
        return {}
    try:
        # json.loads accepts the NaN and Infinity literals by default; PageSpeed output cannot.
        result = json.loads(payload, parse_constant=refuse_non_finite)
    except ValueError as exc:
        raise PageSpeedError("Google API returned invalid JSON.") from exc
    return expect_object(result, "API response")


def write_rows(rows: list[dict[str, Any]], columns: list[str], as_json: bool) -> None:
    if as_json:
        try:
            # allow_nan=False refuses to emit NaN or Infinity, which are not valid JSON.
            print(json.dumps(rows, indent=2, sort_keys=True, allow_nan=False))
        except ValueError as exc:
            raise PageSpeedError("Refused to emit a non-finite value as JSON.") from exc
        return
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    sys.stdout.write(output.getvalue())


def cmd_profiles(args: argparse.Namespace) -> int:
    rows = [{
        "profile": name,
        "label": profile_value(name, LABEL) or name,
        "status": "ready" if profile_value(name, API_KEY) else "missing 1",
    } for name in discovered_profiles()]
    write_rows(rows, ["profile", "label", "status"], args.json)
    return 0


def valid_url(value: str) -> str:
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username or parsed.password:
        raise argparse.ArgumentTypeError("URL must be an absolute HTTP or HTTPS URL without credentials.")
    return value


def scope_rows(experience: dict[str, Any], scope: str, common: dict[str, Any], *, distributions: bool) -> list[dict[str, Any]]:
    raw_metrics = experience.get("metrics")
    metrics = {} if raw_metrics is None else expect_object(raw_metrics, f"{scope} field metrics object")
    # Documented metrics keep their published order and anything Google adds later follows sorted,
    # so row order does not depend on JSON key order.
    ordered = [key for key in FIELD_METRICS if key in metrics]
    ordered += sorted(key for key in metrics if key not in FIELD_METRICS)
    # **Only the page-level reading can be a fallback.** `origin_fallback` says "this URL had too
    # few samples, so what you are reading is the origin's" — a statement origin-level data cannot
    # make about itself, and one Google never puts there. A payload that does is not one this
    # command understands, and deciding what it might have meant would put a claim in the output
    # that Google did not make.
    if scope != "url" and "origin_fallback" in experience:
        raise PageSpeedError(
            f"Google returned an origin fallback on {scope} field data, which it does not report.")
    # Google sends origin_fallback only when it is true, so an absent flag is the common case and
    # means the reading is not a fallback. `is True` keeps that apart from a wrong-typed value,
    # which optional_flag has already refused.
    fallback = optional_flag(experience, "origin_fallback", f"{scope} field origin fallback")
    # A page without enough samples is answered with origin data. Reporting only the scope that was
    # asked about would present site-wide data as the page's, so both are named on every row.
    attribution = {
        **common,
        "requested_scope": scope,
        "effective_scope": "origin" if scope == "url" and fallback is True else scope,
        "origin_fallback": fallback_text(fallback),
        "field_id": expect_text(experience, "id", f"{scope} field data id"),
    }
    rows = [{
        **attribution,
        "row_type": "field_summary",
        "field_category": expect_category(experience, "overall_category", f"{scope} field overall category"),
    }]
    for key in ordered:
        metric = expect_object(metrics[key], f"{scope} {key} field metric object")
        percentile = optional_number(metric, "percentile", f"{scope} {key} field metric percentile")
        category = expect_category(metric, "category", f"{scope} {key} field metric category")
        # Buckets are parsed and checked whether or not they are printed, so --field-data never
        # decides which responses are refused.
        buckets = [(
            optional_number(bucket, "min", f"{scope} {key} field distribution minimum"),
            optional_number(bucket, "max", f"{scope} {key} field distribution maximum"),
            optional_number(bucket, "proportion", f"{scope} {key} field distribution proportion"),
        ) for bucket in expect_objects(metric, "distributions", f"{scope} {key} field distribution")]
        check_buckets(buckets, f"{scope} {key} field distribution")
        if percentile is None and not category and not buckets:
            continue
        name, unit = FIELD_METRICS.get(key, (key.lower(), API_VALUE))
        # The raw key travels with every row so a display name never has to carry the whole meaning.
        measured = {**attribution, "metric": name, "field_metric_key": key, "unit": unit}
        rows.append({**measured, "row_type": "field_metric",
                     "percentile": "" if percentile is None else percentile,
                     "field_category": category})
        if not distributions:
            continue
        for minimum, maximum, proportion in buckets:
            rows.append({**measured, "row_type": "field_distribution",
                         "bucket_min": "" if minimum is None else minimum,
                         "bucket_max": "" if maximum is None else maximum,
                         "proportion": "" if proportion is None else proportion})
    return rows


def field_rows(response: dict[str, Any], common: dict[str, Any], *, distributions: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for scope, key in FIELD_SCOPES:
        raw = response.get(key)
        # A field-data object Google omits or nulls carries no data; a wrong-shaped one is refused.
        if raw is None:
            continue
        experience = expect_object(raw, f"{scope} field data")
        if experience:
            rows.extend(scope_rows(experience, scope, common, distributions=distributions))
    return rows


def analyze_columns(field_data: str) -> list[str]:
    columns = list(LAB_COLUMNS)
    if field_data != "none":
        columns += FIELD_COLUMNS
    if field_data == "distributions":
        columns += DISTRIBUTION_COLUMNS
    return columns + CONTEXT_COLUMNS


def bounded_field_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Field rows are bounded like every other read here, and a drop is never silent.

    Rows are dropped from the end of the emission order, so the requested page's scope survives a
    small bound before the origin's does.
    """
    if len(rows) > limit:
        print(f"WARNING: field output truncated to {limit} rows.", file=sys.stderr)
    return rows[:limit]


def runtime_failure(lighthouse: dict[str, Any]) -> str:
    """The reported reason Lighthouse produced no assessment, or empty when it produced one."""
    runtime_error = expect_object(lighthouse.get("runtimeError", {}), "Lighthouse runtime error")
    if not runtime_error:
        return ""
    code = expect_text(runtime_error, "code", "Lighthouse runtime error code")
    message = expect_text(runtime_error, "message", "Lighthouse runtime error message")
    detail = ": ".join(value for value in (code, message) if value)
    return "Google could not complete the Lighthouse assessment" + (f": {detail}." if detail else ".")


def cmd_analyze(args: argparse.Namespace) -> int:
    profile = selected_profile(args)
    categories = args.category or ["performance"]
    params = [("url", args.url), ("strategy", STRATEGIES[args.strategy])]
    params.extend(("category", CATEGORIES[category]) for category in categories)
    params.append(("key", profile.api_key))
    response = request_json(params)
    lighthouse = expect_object(response.get("lighthouseResult", {}), "Lighthouse result")
    if not lighthouse:
        raise PageSpeedError("Google returned no Lighthouse result for the requested URL.")
    lab_failure = runtime_failure(lighthouse)
    common = {
        "requested_url": expect_text(lighthouse, "requestedUrl", "requested URL") or args.url,
        "final_url": expect_text(lighthouse, "finalUrl", "final URL"),
        "strategy": args.strategy,
        "fetch_time": expect_text(lighthouse, "fetchTime", "fetch time"),
        "lighthouse_version": expect_text(lighthouse, "lighthouseVersion", "Lighthouse version"),
        "profile": profile.name,
    }
    # Field data is an optional extra section. Validating it must never cost the caller the lab
    # assessment they asked for, so a refusal is recorded and reported rather than raised.
    field: list[dict[str, Any]] = []
    field_failure = ""
    field_returned = False
    if args.field_data != "none":
        try:
            field = field_rows(response, common, distributions=args.field_data == "distributions")
        except PageSpeedError as exc:
            field_failure = f"Requested Chrome UX Report field data was not reported. {exc}"
        field_returned = bool(field)
        field = bounded_field_rows(field, args.field_limit)
    columns = analyze_columns(args.field_data)
    if lab_failure:
        # The lab half of the request failed, so no lab row is invented from it. Field data that
        # was asked for and survived validation is still worth reporting.
        print(f"ERROR: {lab_failure}", file=sys.stderr)
        if field_failure:
            print(f"ERROR: {field_failure}", file=sys.stderr)
        if field:
            write_rows(field, columns, args.json)
        return 2
    returned_categories = expect_object(lighthouse.get("categories", {}), "Lighthouse categories object")
    audits = expect_object(lighthouse.get("audits", {}), "Lighthouse audits object")
    summaries = []
    for category in categories:
        result = expect_object(returned_categories.get(category, {}), f"{category} category object")
        score = optional_number(result, "score", f"{category} category score")
        summaries.append({**common, "row_type": "summary", "category": category, "score": "" if score is None else round(score * 100)})
    metrics = []
    for audit_id, metric_name in METRICS.items():
        result = expect_object(audits.get(audit_id, {}), f"{audit_id} audit object")
        display = expect_text(result, "displayValue", f"{audit_id} audit display value")
        numeric = optional_number(result, "numericValue", f"{audit_id} audit numeric value")
        if display or numeric is not None:
            metrics.append({**common, "row_type": "metric", "metric": metric_name, "value": display or numeric, "numeric_value": "" if numeric is None else numeric})
    # Every returned category contributes weights, not only the requested ones, so an audit keeps
    # the highest weight any category assigns it.
    weighted: dict[str, int | float] = {}
    for name, returned in returned_categories.items():
        category_object = expect_object(returned, f"{name} category object")
        for ref in expect_objects(category_object, "auditRefs", f"{name} audit reference"):
            weight = optional_number(ref, "weight", f"{name} audit reference weight")
            if weight is None:
                continue
            ref_id = expect_text(ref, "id", f"{name} audit reference id")
            weighted[ref_id] = max(weighted.get(ref_id, 0), weight)
    findings = []
    for audit_id, result in audits.items():
        result = expect_object(result, f"{audit_id} audit object")
        score = optional_number(result, "score", f"{audit_id} audit score")
        if score is None or score >= 1:
            continue
        findings.append({**common, "row_type": "audit", "audit": audit_id, "title": expect_text(result, "title", f"{audit_id} audit title"), "score": round(score * 100), "display_value": expect_text(result, "displayValue", f"{audit_id} audit display value"), "weight": weighted.get(audit_id, 0)})
    findings.sort(key=lambda item: (-item["weight"], item["score"], item["audit"]))
    if len(findings) > args.audit_limit:
        print(f"WARNING: audit output truncated to {args.audit_limit} findings.", file=sys.stderr)
    if args.field_data != "none":
        if field_failure:
            print(f"ERROR: {field_failure}", file=sys.stderr)
        elif not field_returned:
            # Silence would read as good field data; this URL and origin simply have no CrUX samples.
            print("NOTE: Google returned no Chrome UX Report field data for this URL or origin.", file=sys.stderr)
    write_rows(summaries + metrics + field + findings[:args.audit_limit], columns, args.json)
    # The lab rows the caller asked for are complete, but a requested section that could not be
    # produced is still work that did not happen, so the status records it.
    return 2 if field_failure else 0


def parser() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--env-file")
    parent.add_argument("--json", action="store_true")
    profile = argparse.ArgumentParser(add_help=False)
    profile.add_argument("--profile")
    result = argparse.ArgumentParser(prog="google-pagespeed-insights", description="Read bounded Google PageSpeed Insights evidence.")
    subs = result.add_subparsers(dest="command", required=True)
    command = subs.add_parser("profiles", parents=[parent], help="List locally configured profiles without contacting Google.")
    command.set_defaults(func=cmd_profiles)
    command = subs.add_parser("analyze", parents=[parent, profile], help="Run a Lighthouse assessment for one public webpage.")
    command.add_argument("--url", required=True, type=valid_url)
    command.add_argument("--strategy", choices=list(STRATEGIES), default="mobile")
    command.add_argument("--category", action="append", choices=list(CATEGORIES))
    command.add_argument("--audit-limit", type=int, default=10)
    # Default off: an existing caller's output must not change shape because field data was added.
    command.add_argument("--field-data", choices=["summary", "distributions", "none"], default="none")
    command.add_argument("--field-limit", type=int, default=FIELD_LIMIT_DEFAULT)
    command.set_defaults(func=cmd_analyze)
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        args = parser().parse_args(argv)
        load_dotenv(resolve_env_file(args.env_file), required=bool(args.env_file))
        if hasattr(args, "audit_limit") and not 0 <= args.audit_limit <= 50:
            raise PageSpeedError("--audit-limit must be between 0 and 50.")
        if hasattr(args, "field_limit") and not 0 <= args.field_limit <= FIELD_LIMIT_MAXIMUM:
            raise PageSpeedError(f"--field-limit must be between 0 and {FIELD_LIMIT_MAXIMUM}.")
        return args.func(args)
    except PageSpeedError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
