---
name: google-pagespeed-insights
description: Use when the user needs a current Google PageSpeed Insights or Lighthouse assessment for a specific public webpage, including performance, accessibility, best-practices, or SEO scores, prioritized audit findings, or the recent real-user Core Web Vitals field data Chrome reports for that page and its origin. It supplies bounded read-only lab and field evidence through the PageSpeed Insights API. Do not use for Search Console data, Analytics data, private-page testing, Core Web Vitals history or trends, or changing a website.
---

# Google PageSpeed Insights

Run `$RUNDESK_SKILLS/google-pagespeed-insights/scripts/google-pagespeed-insights`; it resolves the
API key itself, so never inspect or print its source. Read `references/cli.md` only for setup,
environment keys, complete output fields, API behavior, or validation.

List local profiles before analysis. Never guess a profile when more than one is available:

```sh
"$RUNDESK_SKILLS/google-pagespeed-insights/scripts/google-pagespeed-insights" profiles
"$RUNDESK_SKILLS/google-pagespeed-insights/scripts/google-pagespeed-insights" analyze \
  --profile <profile> --url https://www.example.test/ --strategy mobile
```

Default to mobile and the performance category. Add only categories relevant to the question and
keep audit findings bounded:

```sh
"$RUNDESK_SKILLS/google-pagespeed-insights/scripts/google-pagespeed-insights" analyze \
  --profile <profile> --url https://www.example.test/ \
  --category performance --category seo --audit-limit 10
```

Treat Lighthouse scores as a point-in-time lab assessment. Results can vary with page content,
network conditions, Lighthouse versions, and server load. Report the tested URL, strategy,
categories, fetch time, and API-provided Lighthouse version with findings.

## Field data

The same response carries Chrome UX Report field data: real users' experiences over a trailing
28-day window, updated daily. It is off by default and must be asked for:

```sh
"$RUNDESK_SKILLS/google-pagespeed-insights/scripts/google-pagespeed-insights" analyze \
  --profile <profile> --url https://www.example.test/ --field-data summary

"$RUNDESK_SKILLS/google-pagespeed-insights/scripts/google-pagespeed-insights" analyze \
  --profile <profile> --url https://www.example.test/ --field-data distributions
```

`summary` adds `field_summary` and `field_metric` rows; `distributions` also adds the bucket
proportions behind each metric. Without the flag the command reports the Lighthouse assessment
alone, exactly as it always has.

Field data answers a different question than Lighthouse. Never present one as evidence for the
other: a lab metric is one simulated load, a field metric is what Chrome measured for real visitors.

Read these columns together or the reading is wrong:

- `requested_scope` is the object Google was asked about: `url` for the page, `origin` for the site.
- `effective_scope` is what the data actually describes. `url`/`origin` means the page had too few
  samples and Google answered with site-wide data. Report it as the site's, never as the page's.
  `effective_scope` alone cannot tell a fallback from a genuine origin reading; name both.
- `origin_fallback` is `true` only when Google said the page fell back to origin data. Google omits
  the field in the common case, so `false` covers both "Google said false" and "Google said nothing".
- `field_category` is Google's own `FAST`, `AVERAGE`, `SLOW`, or `NONE`. `NONE` means insufficient
  data, not a good result.
- `unit` says how to read `percentile` and the bucket bounds. `milliseconds` is a duration.
  `api_integer` marks `cumulative_layout_shift_score_raw`, whose values are raw API integers: `10`
  and `25` are the values Google sent, not CLS scores of 0.10 and 0.25. Never compare it to a
  Lighthouse `cumulative_layout_shift` row or convert it. `api_value` marks a metric this package
  does not recognize; report it with its `field_metric_key` and claim no unit.

Call `percentile` the API-reported percentile. Google's PageSpeed Insights About page presents the
75th percentile, while the v5 discovery document still describes the field as the 90th; say which
source you are relying on rather than asserting one as certain.

An empty `percentile` means Google reported no value; `0` is a real measurement. A metric or
field-data object with no data produces no row at all, and a note on stderr when neither object has
data. Never fill either with a zero.

Field rows are bounded by `--field-limit`, which defaults to 100 and holds a complete current
response. A drop is always reported on stderr; if you see that warning, say the field reading is
partial rather than presenting it as the whole picture.

Read stderr and the exit status together. `analyze` exits 0 only when every section asked for was
produced. A `WARNING:` is a bound that was honoured and a `NOTE:` is data Google did not have, both
with status 0. An `ERROR:` with status 2 means a requested section did not happen, and any rows on
stdout are the sections that did:

- Lighthouse failed but requested field data is valid: the field rows are printed. Report them and
  say plainly that the lab assessment failed.
- Requested field data is malformed but Lighthouse succeeded: the lab rows are printed in full.
  Report the assessment normally and say the field data could not be read; never treat the non-zero
  status as invalidating the lab result.

This package is read-only. It cannot change a webpage, hosting configuration, Search Console
property, Analytics property, or Google Cloud project.
