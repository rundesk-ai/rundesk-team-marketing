# Measurement

Read this when a claim needs proving, a check needs automating, or someone asks what SEO work can be
put in CI.

An SEO recommendation without a measurement is an opinion. Everything below produces a number
somebody else can reproduce.

## The data sources that are authoritative

| Source | Answers | Access |
|---|---|---|
| Search Console | What Google indexed, chose as canonical, and showed | UI, Search Console API, bulk export to BigQuery |
| Chrome UX Report | Real-user Core Web Vitals at the 75th percentile | CrUX API, CrUX History API, BigQuery |
| Server logs | Which crawler fetched what, and what it received | your infrastructure |
| The live URL | Status, headers, rendered HTML | `curl`, URL Inspection, Rich Results Test |
| Analytics | What humans did after arriving | GA4 or equivalent |
| CRM or commerce system | Which leads qualified, closed, were lost, and produced recognized value | authorized report or supplied export |

Third-party rank trackers and "AI visibility" tools sample; they do not observe. Google states
plainly that "no third-party tool has access to our internal ranking or AI systems." Use them for
direction, never as evidence.

## Baseline the full organic outcome chain

Search Console records what happened before arrival: impressions, clicks, CTR, and average position.
Analytics records onsite behavior after arrival. A CRM or commerce system establishes whether a lead
qualified, closed, was lost, or produced a sale. Do not collapse these sources into one number or
silently choose between them when they differ.

For a lead business, use the authoritative lifecycle available to the property. GA4 documents the
recommended events `generate_lead`, `working_lead`, `qualify_lead`, `disqualify_lead`,
`close_convert_lead`, and `close_unconvert_lead`; its Lead acquisition report can then break new,
qualified, and converted leads down by channel. Equivalent CRM statuses are valid when their
definitions, transition rules, timestamps, and ownership are recorded. For ecommerce, establish the
`purchase` event against the authoritative order or payment record rather than treating a checkout
view as a sale.

At minimum, retain these baseline layers for the same dated population:

1. Search impressions and clicks by query and canonical landing page.
2. Organic landing sessions and the named onsite key event.
3. Generated leads or purchases.
4. Lead dispositions and reasons, or refunds/cancellations where those determine realized quality.
5. Qualified or converted outcomes and recognized value, with the attribution model stated.

Report each rate with its physical numerator and denominator. A high click count with a low
qualified-lead or sale rate is not healthy traffic, and missing disposition data means traffic
quality is unestablished. Fix missing tags, events, joins, status definitions, or disposition capture
before setting a traffic-growth target. Preserve consent and privacy requirements; measurement
readiness does not authorize collecting personal data or changing an account.

## Search Console

**The API** covers search analytics, sitemaps, and URL inspection. Use it for scheduled checks and
regression alerts.

**The bulk data export** is the serious option: a daily dump into BigQuery containing all performance
data except anonymized queries, in two tables — `searchdata_site_impression` (aggregated by
property) and `searchdata_url_impression` (by URL, with query and rich-result detail). They remove the
UI's row limits and 16-month window, which is what makes cannibalization and long-tail analysis
possible at all.

Set it up before it is needed. It is not retroactive; the export starts collecting from the day it is
configured.

Things worth querying on a schedule:

- URLs whose impressions dropped week-over-week beyond a threshold.
- Queries where two or more URLs from the property alternate — the cannibalization signature.
- Pages indexed but receiving zero impressions for 90 days.
- The gap between sitemap URL count and indexed URL count.

## Core Web Vitals

- **CrUX API** — field data, page and origin granularity, 150 queries per minute per Google Cloud
  project at no charge. This is the number that matters.
- **CrUX History API** — the trailing trend, which is how you tell a fix from noise.
- **PageSpeed Insights API** — returns both field and lab data, but Google plans to discontinue the
  field portion and recommends the CrUX APIs instead. Do not build new tooling on PSI field data.
- **Lighthouse / Lighthouse CI** — lab only. Genuinely useful as a **regression gate in CI** on a
  fixed environment, where the point is "did this PR make it worse" and the absolute score is
  irrelevant. It is not a Core Web Vitals measurement and must not be reported as one.

A workable split: Lighthouse CI blocks regressions per-PR; CrUX confirms the real-user effect after
deploy.

## Rendered HTML and structured data

- **URL Inspection** (UI or API) for what Google fetched, rendered, and chose as canonical.
- **Rich Results Test** for rendered HTML and rich-result eligibility.
- **Schema Markup Validator** for schema.org syntax independent of Google's features.
- Search Console enhancement reports for the population-level view a few days later.

In CI, the cheap version of this is a crawl of the sitemap asserting invariants: unique titles, one
canonical per page, canonical is self-referential or intentional, `200` status, no unintended
`noindex`, parseable JSON-LD.

## AI surfaces

- **Google:** the Search Generative AI performance report in Search Console (announced 3 June 2026)
  gives **impressions** in AI Overviews and AI Mode plus pages, countries, devices and dates. There
  is **no click data**, which Google indicated may come later. Rolling out incrementally, so it may
  be absent from a given property.

  **It is not in the API.** `searchanalytics.query` still accepts only `web`, `image`, `video`,
  `news`, `discover`, and `googleNews` for its type, there is no generative-AI value and no separate
  endpoint, so the report is reachable through the Search Console UI and its export only. Anything
  automated against the API cannot see it. Say that plainly rather than describing a number the
  reader cannot pull. The `searchAppearance` dimension is passed through verbatim, so a future
  Google-side value would arrive without a client change — but no such value is documented today,
  and guessing at one is not a measurement.
- **Microsoft:** Bing Webmaster Tools AI Performance (public preview, February 2026) reports total
  citations, average cited pages, grounding queries, and page-level citation activity across Copilot
  and Bing AI summaries. It reports citations, which is closer to the question than impressions.
  There is no documented API; it is a dashboard.
- **Everything else** is sampling. Prompt-based trackers run a prompt set and record what appeared;
  useful for trend, not a measurement of the system.

  If a prompt sample is run anyway — in-house or bought — it is reportable only with all four of:
  the **prompt set fixed and written down** before the run, the **denominator** (how many prompts,
  how many runs each), the **date and platform version observed**, and the statement that generative
  answers are **non-deterministic**, so a re-run differs without anything having changed. Without
  those it is an anecdote with a percent sign. With them it is a trend line about a sample of
  prompts, and still never a measurement of the system. Do not average it with Search Console
  impressions or call the result share of voice; published tools each define that term differently
  and none of the definitions is the platform's.

## AI and assistant referral traffic

GA4 added a native **"AI Assistant" channel** to the default channel group on 13 May 2026 — the first
time AI traffic is split from ordinary referral without configuration. It does not cover every
platform, so add a custom channel group:

- Match `Source` against a regex covering `chatgpt.com`, `openai.com`, `perplexity.ai`, `claude.ai`,
  `gemini.google.com`, `copilot.microsoft.com`, and the current crop.
- **Order it above `Referral`**, or GA4 classifies the session as a referral before reaching the rule.
- Re-check the referral source list monthly; the platform list changes.

That configuration is a change to the property, which is a different permission from reading it. The
**read-only** route needs no configuration at all: a session breakdown by default channel group
returns the native `AI Assistant` row wherever GA4 has assigned it, and a breakdown by session source
returns the raw `chatgpt.com` and `perplexity.ai` rows to classify afterwards. Prefer that when the
task is to measure rather than to instrument, and say which of the two produced the number — a
custom channel group and a source breakdown will not agree, because they classify different things.

**State the limitation whenever reporting these numbers:** a large share of AI referrals arrive with
no referrer header and land in Direct, so measured AI referral traffic is a floor, not a total.
Published estimates of the undercount vary widely and none is authoritative — report the shape of the
error, not a fabricated correction factor. Note also what this measures: a session that arrived from
an assistant. It says nothing about answers where the brand was named and nobody clicked, which the
citation studies suggest is the larger population.

## Server logs

The only ground truth for crawler behaviour, and the check nobody runs. Aggregate by user agent to
answer:

- Is Googlebot spending its fetches on products or on faceted noise?
- Which AI crawlers actually fetch this site, and what status do they get?
- Did a robots.txt change take effect?
- Are crawlers being served errors or slow responses that no human sees?

Verify claimed identities against the published IP lists — Google publishes crawler ranges, and
OpenAI publishes `openai.com/searchbot.json` and siblings. User-agent strings are trivially forged.

## Baselines and honest reporting

- **Record the baseline before the change**, with the date. Post-hoc SEO attribution is otherwise
  unfalsifiable.
- Respect the lag: indexing changes take days, CrUX moves over a 28-day window, ranking effects take
  weeks, and a core update inside the window contaminates everything.
- Annotate deployments and known algorithm updates on any traffic chart.
- Segment before concluding. Sitewide traffic moves for reasons unrelated to the fix; the affected
  URL set is the population to measure.
- When an effect cannot be isolated, say that. "Implemented, not yet attributable" is a legitimate
  and frequently correct status.

## Sources

- [Search Console API](https://developers.google.com/webmaster-tools)
- [Bulk data export](https://developers.google.com/search/blog/2023/02/bulk-data-export)
- [BigQuery efficiency tips for Search Console bulk data exports](https://developers.google.com/search/blog/2023/06/bigquery-efficiency-tips)
- [Using Search Console and Google Analytics data for SEO](https://developers.google.com/search/docs/monitor-debug/google-analytics-search-console)
- [CrUX API](https://developer.chrome.com/docs/crux/api) and [how to use it](https://developer.chrome.com/docs/crux/guides/crux-api)
- [CrUX tools](https://developer.chrome.com/docs/crux/methodology/tools)
- [PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started)
- [Core Web Vitals workflows with Google tools](https://web.dev/articles/vitals-tools)
- [Introducing Search Generative AI performance reports](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)
- [Generative AI performance report — Search Console Help](https://support.google.com/webmasters/answer/16984139)
- [Introducing AI Performance in Bing Webmaster Tools](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview)
- [Verifying Googlebot and other Google crawlers](https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot)
- [OpenAI bots](https://developers.openai.com/api/docs/bots) — published IP ranges per agent
- [Search Console Performance report](https://support.google.com/webmasters/answer/7576553)
- [GA4 recommended lead-generation events](https://support.google.com/analytics/answer/9267735)
- [GA4 Lead acquisition report](https://support.google.com/analytics/answer/16376749)
- [GA4 key events](https://support.google.com/analytics/answer/9267568)
- [GA4 ecommerce events](https://support.google.com/analytics/answer/14434488)
