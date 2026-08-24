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

Third-party rank trackers and "AI visibility" tools sample; they do not observe. Google states
plainly that "no third-party tool has access to our internal ranking or AI systems." Use them for
direction, never as evidence.

## Search Console

**The API** covers search analytics, sitemaps, and URL inspection. Use it for scheduled checks and
regression alerts.

**The bulk data export** is the serious option: a daily dump into BigQuery containing all performance
data except anonymized queries, in three tables — `searchdata_site_impression` (aggregated by
property) and `searchdata_url_impression` (by URL, with query and rich-result detail). It removes the
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
- **Microsoft:** Bing Webmaster Tools AI Performance (public preview, February 2026) reports total
  citations, average cited pages, grounding queries, and page-level citation activity across Copilot
  and Bing AI summaries. It reports citations, which is closer to the question than impressions.
- **Everything else** is sampling. Prompt-based trackers run a prompt set and record what appeared;
  useful for trend, not a measurement of the system.

## AI and assistant referral traffic

GA4 added a native **"AI Assistant" channel** to the default channel group on 13 May 2026 — the first
time AI traffic is split from ordinary referral without configuration. It does not cover every
platform, so add a custom channel group:

- Match `Source` against a regex covering `chatgpt.com`, `openai.com`, `perplexity.ai`, `claude.ai`,
  `gemini.google.com`, `copilot.microsoft.com`, and the current crop.
- **Order it above `Referral`**, or GA4 classifies the session as a referral before reaching the rule.
- Re-check the referral source list monthly; the platform list changes.

**State the limitation whenever reporting these numbers:** a large share of AI referrals arrive with
no referrer header and land in Direct, so measured AI referral traffic is a floor, not a total.
Published estimates of the undercount vary widely and none is authoritative — report the shape of the
error, not a fabricated correction factor.

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
