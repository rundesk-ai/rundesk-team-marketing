# PostHog CLI reference

## Entry points

- `posthog profiles` lists configured profiles without contacting PostHog.
- `posthog event-definitions --profile example --name signup --exclude-hidden --limit 25` lists tracked event definitions.
- `posthog events --profile example --event '$pageview' --after 2026-08-01 --before 2026-08-08 --limit 25` reads a bounded event window.
- `posthog persons --profile example --search alice --limit 25` finds persons.
- `posthog recordings --profile example --offset 0 --limit 10` lists session recording metadata. PostHog does not return replay JSON from this endpoint.
- `posthog web --profile example --days 7 --compare` retrieves the web analytics recap.
- `posthog insights --profile example --type TRENDS --limit 25` lists saved insights.
- `posthog insight SHORT_ID_OR_ID --profile example` retrieves one saved insight.
- `posthog query --profile example --sql "SELECT event, count() FROM events GROUP BY event" --limit 100` runs one read-only HogQL query.

Common analytics presets are bounded, read-only HogQL queries:

- `analytics trends` groups events and unique visitors by day.
- `analytics traffic` groups pageviews by current URL and referring domain.
- `analytics audiences` groups activity by distinct ID and includes a masked person email field,
  falling back to the event email property when available.
- `analytics leads --event lead` groups lead events by person email, falling back to the event email
  property when available.
- `analytics conversion --event signup --event purchase` returns event and unique-person counts for conversion-stage comparison.

Analytics windows are UTC. `--days` counts back from the current UTC moment and a bare `--after`
or `--before` date means UTC midnight; an offset-bearing timestamp is converted to UTC first. The
generated HogQL names the timezone (`toDateTime('...', 'UTC')`) because an unqualified literal is
parsed in the project's own timezone and would shift the window. `analytics traffic` always reads
`$pageview`; passing `--event` is refused because that filter cannot be applied to the pageview
preset.

Pass `--env-file <path>` before the command name for an explicit owner-only dotenv. All resource
commands accept `--profile <name>`, `--all-profiles`, and `--json` where applicable. A command
refuses an ambiguous selection instead of combining credentials across profiles. Text output is
compact and masks email addresses, redacts IP addresses, strips URL query strings, and truncates
long values. JSON is explicit and may contain PostHog's raw person or event fields; do not paste it
into public issues or logs.

## Configuration

Rundesk-managed values are the required `POSTHOG_PERSONAL_API_KEY` and `POSTHOG_PROJECT_ID`. The
personal API key should have only the read scopes needed for the commands in use:

```text
query:read
event_definition:read
person:read
session_recording:read
insight:read
web_analytics:read
```

The default account uses the plain names. A named account uses the double-underscore suffix:

```dotenv
POSTHOG_PERSONAL_API_KEY=
POSTHOG_PROJECT_ID=12345
POSTHOG_BASE_URL=https://us.posthog.com

POSTHOG_PERSONAL_API_KEY__EU_SITE=
POSTHOG_PROJECT_ID__EU_SITE=67890
POSTHOG_BASE_URL__EU_SITE=https://eu.posthog.com
```

The older command-local spelling remains supported in an owner-only dotenv:

```dotenv
POSTHOG_PROFILES=example,eu-site
POSTHOG_DEFAULT_PROFILE=example
POSTHOG_EXAMPLE_KEY=
POSTHOG_EXAMPLE_PROJECT_ID=12345
POSTHOG_EU_SITE_KEY=
POSTHOG_EU_SITE_PROJECT_ID=67890
```

Use `rundesk skills configure rundesk-skills-integrations/posthog` for Rundesk-managed storage.
Never put a key in a command argument, repository, fixture, or output. The default API host is
`https://us.posthog.com`; set `POSTHOG_BASE_URL` to `https://eu.posthog.com` or an HTTPS
self-hosted origin when appropriate. Paths, credentials, queries, and fragments are rejected.

## Filters and API boundaries

`event-definitions` passes documented name, hidden, and stale filters. `events` accepts event,
distinct ID, person ID, ISO date/timestamp `--after` and `--before`, selected fields, and
`--include-person`. `persons` accepts search, email, and distinct ID. `insights` accepts search,
insight type, and date bounds. Session recordings are filtered by the documented offset and limit.

PostHog paginates resource responses with a `next` URL. The CLI follows only same-origin HTTPS
URLs, stops at the requested limit or a bounded page cap, caps each response at 10 MiB, and reports
remaining data. It retries 429 responses for reads using `Retry-After` when present. A 403 normally
indicates that the key is missing the resource scope or cannot access the configured project.

The direct events API is limited by PostHog and marked for future removal. It also defaults to a
recent window when `--after` is omitted and has a maximum date range. Use HogQL for durable event,
trend, traffic, audience, lead, and conversion analysis. `query` accepts only one `SELECT` or
`WITH` statement, refuses write/DDL keywords, adds `LIMIT` when absent, and refuses a supplied
`LIMIT` larger than the command bound, and limits `--name` to PostHog's 128-character API bound.

## Validation

Run the offline package test and the catalog suite:

```sh
python3 skills/posthog/scripts/posthog.d/test-posthog.py -q
python3 -m unittest discover -s tests -v
skills/posthog/scripts/posthog --help
(cd /tmp && "$repository_root/skills/posthog/scripts/posthog" profiles)
git diff --check
```

Tests use synthetic responses and do not need PostHog credentials. Do not use a live account as a
test fixture or run a mutation; this package has no mutation command.

## Official API references

- [API overview](https://posthog.com/docs/api) for authentication, hosts, rate limits, pagination, and response errors.
- [Query API](https://posthog.com/docs/api/query) and [API queries](https://posthog.com/docs/api/queries) for HogQL payloads and result shapes.
- [Events](https://posthog.com/docs/api/events), [event definitions](https://posthog.com/docs/api/event-definitions), and [persons](https://posthog.com/docs/api/persons) for filtered resource reads.
- [Session recordings](https://posthog.com/docs/api/session-recordings), [insights](https://posthog.com/docs/api/insights), and [web analytics](https://posthog.com/docs/api/web-analytics) for the remaining read commands.
