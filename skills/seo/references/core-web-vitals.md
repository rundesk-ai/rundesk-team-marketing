# Core Web Vitals

Read this when a task involves page speed, responsiveness, layout stability, or a performance score
someone wants improved for search reasons.

## The three metrics and their thresholds

| Metric | Measures | Good | Poor above |
|---|---|---|---|
| Largest Contentful Paint (LCP) | Loading | ≤ 2.5s | 4.0s |
| Interaction to Next Paint (INP) | Responsiveness | ≤ 200ms | 500ms |
| Cumulative Layout Shift (CLS) | Visual stability | ≤ 0.1 | 0.25 |

**All three are assessed at the 75th percentile of page loads, split by mobile and desktop.** A page
passes only when all three are Good at that percentile
([Web Vitals](https://web.dev/articles/vitals)). Optimizing the median is optimizing the wrong number:
the threshold is set so that a quarter of real visits may still be worse than the reported figure.

First Input Delay (FID) is retired and replaced by INP. Any advice or tooling still reporting FID is
out of date.

## Field data is the measurement; lab data is a debugging aid

Google's ranking systems and Search Console use **field data** from the Chrome UX Report — real
Chrome users, aggregated over a trailing 28 days. Lighthouse and PageSpeed Insights' lab section
simulate a single load on one machine with a synthetic network.

The consequences that matter in practice:

- A green Lighthouse score does not mean the page passes Core Web Vitals, and a red one does not mean
  it fails. Report field data when the question is about search.
- **INP cannot be measured in the lab at all** — no synthetic run produces real interactions. Total
  Blocking Time is the lab proxy web.dev names, and it is a proxy, not the metric.
- CrUX needs enough traffic to report. A low-traffic URL falls back to origin-level data or has none;
  say so rather than inventing a number.
- Field data lags. A fix deployed today moves the 28-day window gradually; do not judge it in a day.

## What actually changes each metric

### LCP — almost always the hero image or the font

1. Find the LCP element first. It is reported per-page in CrUX and in Lighthouse; guessing wastes the
   whole exercise.
2. Never lazy-load it. `loading="lazy"` on an above-the-fold image is the single most common
   self-inflicted LCP regression.
3. Preload it, and preload the *responsive* candidate — `<link rel="preload" as="image" imagesrcset=…>`
   so the preload matches what `srcset` will pick.
4. Cut render-blocking work in `<head>`: inline critical CSS, defer the rest, and load fonts with
   `font-display: swap` plus a preload of the font file itself.
5. Reduce Time to First Byte. TTFB is a diagnostic metric, not a Core Web Vital, but it is a floor
   under LCP that no front-end change can get below.

### INP — long tasks on the main thread

1. Break up long tasks. Anything over 50ms blocks the next interaction.
2. Move work out of event handlers: yield to the main thread before non-urgent work, and defer
   analytics and third-party scripts.
3. Audit third parties honestly. Embeds, tag managers, chat widgets, and consent banners are the
   usual cause, and they are usually somebody else's code running in the critical path.
4. Avoid large re-renders synchronous with input in component frameworks.

### CLS — space that was not reserved

1. Set `width` and `height` (or `aspect-ratio`) on every image, video, iframe and ad slot.
2. Reserve space for anything injected late: banners, cookie notices, lazily hydrated components.
3. Load fonts so the fallback and the web font have compatible metrics, or the swap shifts the text.
4. Never insert content above existing content after paint unless it is in response to an
   interaction.

## Where performance sits in an SEO priority list

Page experience is a genuine but modest ranking input, and it is a tiebreaker rather than a
substitute for relevance. Google's own framing is that it helps when other signals are comparable.
Treat it accordingly:

- Fix indexability and canonicalization first. A fast page that is not indexed ranks nowhere.
- Fix a *failing* Core Web Vitals assessment; do not chase 100/100 on a page already passing. Beyond
  the threshold there is no additional search benefit to claim, and the effort is better spent on
  content and internal links.
- Performance has direct commercial value independent of ranking. Say that plainly rather than
  overstating the SEO case for it.

## Verification

```sh
# Field data for one URL, from the Chrome UX Report (free, 150 queries/minute)
curl -sS "https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=$CRUX_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/page","formFactor":"PHONE"}'
```

Read `p75` for each metric from the response, and the histogram for the good/needs-improvement/poor
split. `references/measurement.md` covers wiring this into a repeatable check.

## Sources

- [Web Vitals](https://web.dev/articles/vitals) — the metric set, thresholds, and the 75th percentile rule
- [How the Core Web Vitals metrics thresholds were defined](https://web.dev/articles/defining-core-web-vitals-thresholds)
- [Largest Contentful Paint (LCP)](https://web.dev/articles/lcp)
- [The performance effects of too much lazy loading](https://web.dev/articles/lcp-lazy-loading)
- [Preload responsive images](https://web.dev/articles/preload-responsive-images)
- [Debug performance in the field](https://web.dev/articles/debug-performance-in-the-field)
- [Understanding Core Web Vitals and Google search results](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [CrUX API](https://developer.chrome.com/docs/crux/api)
