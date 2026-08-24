---
name: posthog
description: Use when the user needs PostHog product analytics, event or person data, traffic sources, audiences, leads, conversions, trends, saved insights, session recording metadata, or web analytics pulled across one or more PostHog projects. It supplies profile-scoped, bounded PostHog reads, filtered resources, safe HogQL queries, and common analytics query presets. Do not use it to capture events, change PostHog configuration, manage keys, or mutate analytics data.
---
# PostHog

Run `$RUNDESK_SKILLS/posthog/scripts/posthog`; it resolves credentials without printing or
inspecting their source. Read `references/cli.md` for setup, filters, output fields, API scopes,
analytics presets, and validation.

Start with:

```sh
"$RUNDESK_SKILLS/posthog/scripts/posthog" profiles
```

Select a profile explicitly when more than one is configured. Use `--all-profiles` only when a
cross-project result is intended. Every read is bounded by `--limit`; truncation is reported on
stderr and means the answer is partial.

Use the resource commands for targeted reads:

```sh
"$RUNDESK_SKILLS/posthog/scripts/posthog" event-definitions --profile <profile> --exclude-hidden --limit 50
"$RUNDESK_SKILLS/posthog/scripts/posthog" persons --profile <profile> --search '<term>' --limit 20
"$RUNDESK_SKILLS/posthog/scripts/posthog" events --profile <profile> --event '$pageview' --after 2026-08-01 --before 2026-08-08 --limit 20
"$RUNDESK_SKILLS/posthog/scripts/posthog" insights --profile <profile> --type TRENDS --limit 20
```

Prefer `analytics trends`, `traffic`, `audiences`, `leads`, and `conversion` for common questions;
use `query --sql` when the question needs a custom breakdown. These commands send read-only HogQL
to PostHog and append a result limit when the query does not provide one; an explicit limit larger
than `--limit` is refused.

The direct `events` endpoint is retained for narrow compatibility reads and warns that PostHog has
announced its future removal. Prefer `query` or an analytics preset for event analysis. Use
`--json` only when structured or potentially sensitive raw fields are required; human-readable
output masks email addresses, redacts IP addresses, and removes URL query strings.
