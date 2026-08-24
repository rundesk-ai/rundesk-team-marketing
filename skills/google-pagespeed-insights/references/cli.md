# Google PageSpeed Insights CLI reference

## Commands

```text
google-pagespeed-insights profiles
google-pagespeed-insights analyze --profile example --url https://www.example.test/
google-pagespeed-insights analyze --profile example --url https://www.example.test/ --strategy desktop --category performance --category accessibility --category best-practices --category seo --audit-limit 10
google-pagespeed-insights analyze --profile example --url https://www.example.test/ --field-data distributions --field-limit 100
google-pagespeed-insights analyze --profile example --url https://www.example.test/ --field-data none
```

The service command is read-only. Text is compact CSV by default; pass `--json` for structured
output. `analyze` defaults to the mobile strategy, the performance category, and 10 failed or
informative audits. `--audit-limit` accepts 0 through 50; zero emits scores and metrics without
individual audit findings. Repeat `--category` to request multiple Lighthouse categories.

`--field-data` accepts `none` (the default), `summary`, and `distributions`. It selects which rows
of the Chrome UX Report field data already present in the response are reported; it never changes
the request. The default is `none` so that a caller written before field data existed receives
byte-for-byte the same CSV header, CSV body, and JSON row set it always received.

`--field-limit` bounds how many field rows are emitted. It accepts 0 through 500 and defaults to
100, which holds a complete current response for both scopes with distributions; zero emits no
field row at all. Rows are dropped from the end of the emission order, so the requested page's
scope survives a small bound before the origin's does, and a drop is always reported on stderr.

## Exit status

`analyze` exits 0 only when every section the invocation asked for was produced. It exits 2 when a
requested section could not be produced, and whatever valid rows do exist are still written to
stdout so a usable result is never thrown away with the unusable one:

| Situation | stdout | stderr | Status |
|---|---|---|---|
| Everything requested was produced | all rows | nothing, or a bound or empty-data note | 0 |
| Output reached `--audit-limit` or `--field-limit` | the bounded rows | `WARNING:` truncation notice | 0 |
| Field data requested and Google returned none | lab rows | `NOTE:` no field data | 0 |
| Field data requested and its payload is malformed | lab rows | `ERROR:` naming the field-data problem | 2 |
| Lighthouse reported a `runtimeError` | valid field rows, if any | `ERROR:` naming the lab failure | 2 |
| Lighthouse and requested field data both failed | field rows, if any survived | one `ERROR:` per failed section | 2 |
| The response has no `lighthouseResult`, or is malformed outside the field data | nothing | `ERROR:` | 2 |

Three stderr prefixes carry that grammar: `ERROR:` marks requested work that did not happen and
always accompanies status 2, `WARNING:` marks output a documented bound truncated, and `NOTE:`
marks a section Google legitimately had nothing to report for. Neither `WARNING:` nor `NOTE:`
changes the exit status. A malformed optional field-data payload never suppresses the lab
assessment, because the lab result is the work the caller asked for and it succeeded.

The command reports category scores, selected lab metrics, and the highest-weighted audits whose
score is below 1. Audits without a numeric score are omitted from the compact finding list. Google
may return a final analyzed URL after redirects; both requested and final URLs are reported.

`--strategy` and `--category` stay lowercase at the command line and in output. The request maps
them to the uppercase enums the v5 discovery document defines: `MOBILE` and `DESKTOP`, and
`PERFORMANCE`, `ACCESSIBILITY`, `BEST_PRACTICES`, and `SEO`. The lowercase names are also the keys
Lighthouse uses inside the response, so they are what appears in the `category` column.

## Field data

The same `runPagespeed` response carries Chrome UX Report field data, so reporting it needs no
second request, no additional API, and no additional key or scope. `loadingExperience` describes the
requested page and `originLoadingExperience` describes the whole origin; they are reported as the
separate `url` and `origin` scopes rather than merged.

Per Google's About page, field data covers real users' experiences over a trailing 28-day window,
is updated daily, and reports FCP, INP, LCP, CLS, and the experimental TTFB.

Row types and the columns each one fills:

- `field_summary` — one per field-data object: `requested_scope`, `effective_scope`,
  `origin_fallback`, `field_id`, and `field_category` holding that object's `overall_category`.
- `field_metric` — one per metric: `metric`, `field_metric_key`, `unit`, `percentile`, and
  `field_category` holding that metric's `category`.
- `field_distribution` — only with `--field-data distributions`: `bucket_min`, `bucket_max`, and
  `proportion`, exactly as Google returned them. The final bucket may be open-ended, in which case
  its `bucket_max` is empty.

Every field row repeats `requested_scope`, `effective_scope`, `origin_fallback`, and `field_id`, and
every metric and distribution row also repeats `field_metric_key` and `unit`, so no single row has
to be interpreted from its neighbours.

### Scope and fallback

`requested_scope` names the object Google was asked about and `effective_scope` names what the data
describes:

| Response shape | `requested_scope` | `effective_scope` | `origin_fallback` |
|---|---|---|---|
| `loadingExperience` without `origin_fallback` | `url` | `url` | `false` |
| `loadingExperience` with `origin_fallback: false` | `url` | `url` | `false` |
| `loadingExperience` with `origin_fallback: true` | `url` | `origin` | `true` |
| `originLoadingExperience`, which never carries the field | `origin` | `origin` | `false` |
| `originLoadingExperience` carrying the field at all | refused | refused | refused |
| either object with `origin_fallback: null` | refused | refused | refused |

Google omits `origin_fallback` entirely in the common case rather than sending `false`. Absent and
an explicit `false` mean the same thing — this reading is not an origin fallback — so both are
reported as `false` and the column has one spelling. Only a value Google actually sent as `true`
produces `true`, and only that value moves `effective_scope` to `origin`.

Two shapes are refused rather than interpreted, and both would otherwise be read as a confident
`false`:

- **`origin_fallback` on `originLoadingExperience`.** The flag says "this URL had too few samples,
  so you are reading the origin's data" — which origin-level data cannot say about itself. Google
  never sends it there, so a response that does is not one this command understands.
- **An explicit `origin_fallback: null`.** Absent means Google had nothing to say; `null` means it
  answered, and what it answered is not a boolean. Read alike, a malformed response would arrive as
  the ordinary case.

The absent case therefore stays distinct from a malformed one inside the command: the parser
returns "absent" only for a key that is not present, the boolean for a reported one, and refuses
anything else. A response can never be read as "not a fallback" because its flag arrived in the
wrong type or in the wrong place.

Reading `effective_scope` alone cannot distinguish a page that fell back from a genuine origin
reading, so both scope columns are needed to attribute a row. Booleans are rendered as `true` and
`false` in both output modes.

### Percentile, units, and metric names

`percentile` is reported as the API returned it and is named for the API field rather than for a
specific percentile. Google's About page presents the 75th percentile, while the v5 discovery
document still describes the field as the 90th; this package does not assert either as certain.

`unit` states how to read `percentile` and the bucket bounds:

- `milliseconds` — a duration: `FIRST_CONTENTFUL_PAINT_MS`, `LARGEST_CONTENTFUL_PAINT_MS`,
  `INTERACTION_TO_NEXT_PAINT`, `FIRST_INPUT_DELAY_MS`, and `EXPERIMENTAL_TIME_TO_FIRST_BYTE`.
- `api_integer` — `CUMULATIVE_LAYOUT_SHIFT_SCORE` only. The API types this metric as an integer
  while Lighthouse reports CLS as a unitless ratio, and no Google page states the relationship
  between them. Values are passed through untouched and no `/100` scaling is invented, so a
  `percentile` or bucket bound of `10` or `25` is the integer Google sent and is **not** a CLS score
  of 0.10 or 0.25. The metric is named `cumulative_layout_shift_score_raw` precisely so it cannot be
  compared with a Lighthouse `cumulative_layout_shift` row.
- `api_value` — a metric key this package does not recognize. Its unit is unknown and unclaimed.

Field metrics share a lab metric name only where both measure the same quantity in the same unit:
`first_contentful_paint`, `largest_contentful_paint`, and `interaction_to_next_paint`.
`FIRST_INPUT_DELAY_MS` maps to `first_input_delay` and `EXPERIMENTAL_TIME_TO_FIRST_BYTE` to
`experimental_time_to_first_byte`. The v5 reference documents the metrics map key only as `(key)`,
so an unrecognized key is reported lowercased instead of being dropped. The raw key is always
available in `field_metric_key`, so a display name never has to carry the whole meaning.

### Absent data

Absent data is never rendered as zero. A metric Google does not return, or returns with no
percentile, no category, and no distributions, produces no row. A missing or null field-data object
produces no rows for that object. When neither object has data, a note is written to stderr. An
empty `percentile` means no value was reported, while `0` is a real measurement.

`fetch_time` and `lighthouse_version` on a field row describe the lab run in the same response, not
the field-data window.

### Bounded field rows

Field rows are bounded like every other read in this catalog. `--field-limit` defaults to 100, which
holds a complete current response — two scopes, six documented metrics, three buckets each — so the
bound does not silently shorten a normal reading. When Google returns more rows than the bound,
`WARNING: field output truncated to <limit> rows.` is written to stderr and the exit status stays 0,
because the bound was honoured rather than requested work failing. Rows are dropped from the end of
the emission order, which is the `url` scope followed by the `origin` scope, each as a summary then
its metrics and their buckets. `--field-limit 0` emits no field row and still reports the drop, so
an empty field section is never mistaken for Google having no data.

### Partial results

`analyze` treats the lab assessment and the optional field data as two sections and reports each on
its own terms. A refused optional section never removes a section that succeeded.

When Lighthouse reports a `runtimeError`, the lab assessment does not exist and no score, metric, or
audit row is invented from it. If field data was requested and passed validation, those rows are
written to stdout, the Lighthouse failure is reported on stderr, and the command exits 2 because
`analyze` was only partly satisfied. If field data was not requested, none was returned, or it also
failed validation, nothing is written to stdout and the command exits 2. A response with no
`lighthouseResult` at all remains a hard failure with no output.

When Lighthouse succeeded and only the requested field data is malformed, the lab rows are written
to stdout exactly as they would have been, the field-data problem is named on stderr as an `ERROR:`,
and the command exits 2. The caller keeps the assessment it asked for and still learns, from both
stderr and the status, that the optional section it also asked for did not happen. Losing a valid
lab result to a malformed optional payload would discard work Google did do.

The Lighthouse result is validated before use: the result, its `categories` and `audits` objects,
each category object, each `auditRefs` list and element, and each audit object must have the shape
the API documents. Field data is validated the same way: each field-data object, its `metrics`
object, each metric object, each `distributions` list and element, and `id` must have the documented
shape, `origin_fallback` must be a JSON boolean, and percentiles, bucket bounds, and proportions
must be finite numbers. `overall_category` and each metric `category`, when present, must be one of
`FAST`, `AVERAGE`, `SLOW`, or `NONE`.

A `distributions` field is not required and an empty list is accepted, but a list Google did send
must be complete and consistent, because a partial one silently understates how many experiences
were poor. Every bucket must carry a `proportion` in `[0, 1]` and a non-negative `min`; a `max`,
when present, must be non-negative and at least `min`; buckets must be ordered and must not overlap;
at most one bucket may be open-ended and it must be the last; and the proportions must total 1
within 0.02, which allows for the rounding in the returned values. A lower bound is required because
ordering and overlap cannot be judged without it.

Requested field data is validated before anything is written, including when Lighthouse also failed,
and distribution buckets are validated whether or not `--field-data` prints them, so neither the
output mode nor a lab failure decides which responses are refused. A field-data refusal is reported
and costs the exit status; it does not cost a lab assessment that succeeded. Scores, audit-reference weights,
and numeric metric values must be finite numbers. A malformed, null, or wrong-shaped response is reported on stderr and exits 2 rather than
producing a partial reading, and JSON output never contains `NaN` or `Infinity`, which are not
valid JSON.

## API key and profiles

Create an API key in a Google Cloud project with the PageSpeed Insights API enabled, restrict it to
the PageSpeed Insights API where practical, and store it through Rundesk. Never commit or send it
through chat.

Required variable from `rundesk.json`:

```text
GOOGLE_PAGESPEED_INSIGHTS_API_KEY
```

Optional variables are `GOOGLE_PAGESPEED_INSIGHTS_LABEL` and
`GOOGLE_PAGESPEED_INSIGHTS_DEFAULT_PROFILE`. A Rundesk-managed named profile appends a normalized
double-underscore suffix:

```dotenv
GOOGLE_PAGESPEED_INSIGHTS_API_KEY__EXAMPLE=
GOOGLE_PAGESPEED_INSIGHTS_LABEL__EXAMPLE=Example PageSpeed
```

The command also supports local profile discovery through
`GOOGLE_PAGESPEED_INSIGHTS_PROFILES=example`. Resolution order is process environment,
`--env-file`, `GOOGLE_PAGESPEED_INSIGHTS_ENV_FILE`, `RUNDESK_INTEGRATIONS_ENV`,
`${XDG_CONFIG_HOME:-$HOME/.config}/rundesk/integrations/google-pagespeed-insights/env`, then the
legacy `${XDG_CONFIG_HOME:-$HOME/.config}/google-pagespeed-insights/env`.

`profiles` does not contact Google and never prints API-key values. A service command requires an
explicit profile when more than one is configured. A named profile never falls back to the default
profile's API key.

## Output

- Summary rows: requested URL, final URL, strategy, category, score, fetch time, Lighthouse version,
  and profile.
- Metric rows: First Contentful Paint, Largest Contentful Paint, Speed Index, Total Blocking Time,
  Cumulative Layout Shift, and Interaction to Next Paint when returned by Lighthouse.
- Audit rows: audit identifier, title, score, display value, weighted impact, and profile.
- Field rows: requested and effective scope, origin fallback, CrUX identifier, metric, raw metric
  key, unit, percentile, category, and, when requested, distribution bucket bounds and proportions.
  Bounded by `--field-limit`.

Rows are emitted as category summaries, lab metrics, field data, then audit findings. Column order
is stable, and the field and distribution columns are present only when those rows were requested.

Errors and truncation warnings go to stderr. API keys and request URLs containing the `key` query
parameter are never printed.

## Validation

```sh
python3 skills/google-pagespeed-insights/scripts/google-pagespeed-insights.d/test-google-pagespeed-insights.py -q
skills/google-pagespeed-insights/scripts/google-pagespeed-insights --help
skills/google-pagespeed-insights/scripts/google-pagespeed-insights profiles
```

Tests are offline and replace the Google API network boundary with synthetic responses, including
hostile fixtures for null, wrong-shaped, and non-finite values.

## Official references

- [PageSpeed Insights API](https://developers.google.com/speed/docs/insights/rest)
- [Get started](https://developers.google.com/speed/docs/insights/v5/get-started)
- [runPagespeed method](https://developers.google.com/speed/docs/insights/rest/v5/pagespeedapi/runpagespeed)
- [About PageSpeed Insights](https://developers.google.com/speed/docs/insights/v5/about)
- [Release notes](https://developers.google.com/speed/docs/insights/release_notes)
- [CrUX data on PageSpeed Insights](https://developer.chrome.com/docs/crux/guides/pagespeed-insights)
- [PageSpeed Insights v5 discovery document](https://pagespeedonline.googleapis.com/$discovery/rest?version=v5)

The runPagespeed reference defines the response fields, including the snake_case `overall_category`,
`initial_url`, and the optional `origin_fallback`, and the metric shape of `percentile`, `distributions` with
`min`, `max`, and `proportion`, and a `category` of `FAST`, `AVERAGE`, `SLOW`, or `NONE`. The About
page defines the 28-day window and daily updates, names the reported metrics, and presents the
75th percentile.

Two gaps in the published contract shape this package:

- The reference documents the metrics map key only as `(key)` and never enumerates the metric names.
  The names used here come from Google's own example response (`FIRST_CONTENTFUL_PAINT_MS`,
  `FIRST_INPUT_DELAY_MS`), the codelab (`LARGEST_CONTENTFUL_PAINT_MS`), and the release notes, which
  record `EXPERIMENTAL_INTERACTION_TO_NEXT_PAINT` being replaced by `INTERACTION_TO_NEXT_PAINT` on
  8 August 2023. `CUMULATIVE_LAYOUT_SHIFT_SCORE` and `EXPERIMENTAL_TIME_TO_FIRST_BYTE` are not
  confirmed verbatim by a current Google page. Unrecognized keys are therefore reported rather than
  dropped, and no name is required to be present.
- The v5 discovery document still describes `percentile` as the 90th percentile, while the About
  page states PageSpeed Insights reports the 75th. The About page is treated as authoritative, which
  is why the column is named `percentile` rather than a percentile-specific name.

The Get started page states that Google plans to discontinue including Chrome UX Report data in this
API, without a published date, and recommends the CrUX API and CrUX History API instead. No
migration is made here because the field data is still returned and a separate API would need its
own approval. When Google removes it, the `loadingExperience` and `originLoadingExperience` objects
disappear from the response and the command reports no field data rather than failing.
