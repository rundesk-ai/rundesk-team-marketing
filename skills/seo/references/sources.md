# SEO source basis

This package is a Rundesk synthesis of search-engine documentation and published measurement. The
operational guidance is in the other references; use this file to audit or update the basis of any
claim, and to check whether a source has moved since it was read.

**Read in this order of authority.** Platform documentation states rules; published studies measure
outcomes and are correlational; commentary reports announcements. Never present the second or third
as the first.

Verified against the sources listed here in **August 2026**. Google withdrew several rich result
types during 2026 and AI reporting surfaces are rolling out incrementally, so anything dated should
be re-checked before being quoted to a client.

## Tier 1 — platform documentation

### Google Search fundamentals

- [Search Essentials — technical requirements](https://developers.google.com/search/docs/essentials/technical):
  the three conditions for eligibility — Googlebot not blocked, HTTP `200`, indexable content.
- [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide):
  site organization, directory structure, sitemaps as a crawl priority signal.
- [In-depth guide to how Google Search works](https://developers.google.com/search/docs/fundamentals/how-search-works):
  crawling, indexing, and serving as three separate stages.
- [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content):
  the self-assessment questions, E-E-A-T with trust as the primary aspect, and the two AI-content
  rules (disclosure, and the spam line on rank manipulation).
- [Spam policies for Google web search](https://developers.google.com/search/docs/essentials/spam-policies):
  all sixteen named policies, including scaled content abuse and site reputation abuse.

### Crawling, indexing, and rendering

- [Consolidate duplicate URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls):
  the canonicalization signal hierarchy — redirects strongest, `rel="canonical"` strong, sitemaps
  weak — plus the explicitly prohibited practices.
- [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap):
  50MB / 50,000 URL limits; `<priority>` and `<changefreq>` ignored; `<lastmod>` honoured only when
  "consistently and verifiably accurate".
- [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics):
  the three-phase pipeline, the `<a href>` requirement, soft-404 handling, and the warning that
  blocked JS is not rendered.
- [Fix lazy-loaded content](https://developers.google.com/search/docs/crawling-indexing/javascript/lazy-loading).
- [Crawl management for faceted navigation](https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation):
  the overcrawling mechanism and the five mitigations in strength order.
- [Localized versions of your pages](https://developers.google.com/search/docs/specialty/international/localized-versions):
  hreflang delivery methods, the mandatory return links, ISO code format, `x-default`, and the
  invalid `UK`/`EU`/`UN` codes.
- [Mobile-first indexing best practices](https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing).
- [Verifying Googlebot and other Google crawlers](https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot).
- [Qualify your outbound links](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links):
  `sponsored`, `ugc`, `nofollow`.

### Appearance and structured data

- [Influencing your title links](https://developers.google.com/search/docs/appearance/title-link):
  every documented rewrite trigger, the sources Google draws titles from including `og:title`, and
  the statement that there is no length limit on `<title>`.
- [Control your snippets](https://developers.google.com/search/docs/appearance/snippet):
  `nosnippet`, `max-snippet`, `data-nosnippet`.
- [Structured data general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies):
  JSON-LD preference, the visible-content rule, and the manual-action consequence.
- [Structured data markup that Google Search supports](https://developers.google.com/search/docs/appearance/structured-data/search-gallery):
  the current supported feature list. **Check this before recommending any type.**
- [Changes to HowTo and FAQ rich results](https://developers.google.com/search/blog/2023/08/howto-faq-changes)
  and [Simplifying the search results page](https://developers.google.com/search/blog/2025/06/simplifying-search-results):
  the withdrawal programme.
- [Understanding Core Web Vitals and Google search results](https://developers.google.com/search/docs/appearance/core-web-vitals).
- [Image SEO](https://developers.google.com/search/docs/appearance/google-images) ·
  [Video SEO](https://developers.google.com/search/docs/appearance/video).

### Ecommerce

- [Ecommerce SEO](https://developers.google.com/search/docs/specialty/ecommerce) — the section index.
- [Share your product data with Google](https://developers.google.com/search/docs/specialty/ecommerce/share-your-product-data-with-google):
  structured data, Merchant Center feeds, and the Content/Merchant API, and why they are combined.
- [Designing a URL structure for ecommerce sites](https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites):
  parameter format, variant URLs, and the warning on session IDs and tracking parameters.
- [Pagination and incremental page loading](https://developers.google.com/search/docs/specialty/ecommerce/pagination-and-incremental-page-loading):
  `rel=next/prev` retired; per-page self-canonical; crawlers do not trigger user-action JavaScript.
- [Intro to product structured data](https://developers.google.com/search/docs/appearance/structured-data/product) ·
  [Merchant listing](https://developers.google.com/search/docs/appearance/structured-data/merchant-listing) ·
  [Product variants](https://developers.google.com/search/docs/appearance/structured-data/product-variants) ·
  [Merchant return policy](https://developers.google.com/search/docs/appearance/structured-data/return-policy).
- [Product data specification](https://support.google.com/merchants/answer/7052112) and the
  [2026 specification update](https://support.google.com/merchants/answer/16989427).

### AI features

- [Optimizing for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide):
  **the single most useful source in this package.** Eligibility requirements, RAG and query fan-out,
  and Google's explicit debunking of `llms.txt`, chunking, AI-specific writing, and structured data
  as AI requirements.
- [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features):
  snippet controls, `Google-Extended`, and the statement that no new machine-readable files are
  needed.
- [Introducing Search Generative AI performance reports](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)
  and the [Search Console help page](https://support.google.com/webmasters/answer/16984139).

### Non-Google platforms

- [OpenAI bots](https://developers.openai.com/api/docs/bots): `OAI-SearchBot`, `GPTBot`,
  `ChatGPT-User`, `OAI-AdsBot`; per-agent IP lists; and the consequence of blocking each.
- [Anthropic: does Anthropic crawl data from the web?](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
- [Bing Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a) ·
  [AI Performance in Bing Webmaster Tools](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview)
- [IndexNow documentation](https://www.indexnow.org/documentation)
- [The Open Graph protocol](https://ogp.me/): the specification behind `og:` tags. X's own card
  documentation was folded into a generic developer overview and is no longer citable at a stable
  URL; `twitter:` tags fall back to Open Graph, so this is the source that still holds.

## Tier 1 — web platform performance

- [Web Vitals](https://web.dev/articles/vitals): the metric set, thresholds, the 75th-percentile rule,
  FID's retirement, and TBT as the lab proxy for INP.
- [How the Core Web Vitals thresholds were defined](https://web.dev/articles/defining-core-web-vitals-thresholds).
- [Largest Contentful Paint](https://web.dev/articles/lcp) ·
  [The performance effects of too much lazy loading](https://web.dev/articles/lcp-lazy-loading) ·
  [Preload responsive images](https://web.dev/articles/preload-responsive-images).
- [Debug performance in the field](https://web.dev/articles/debug-performance-in-the-field) ·
  [Core Web Vitals workflows with Google tools](https://web.dev/articles/vitals-tools).

## Tier 1 — measurement APIs

- [Search Console API](https://developers.google.com/webmaster-tools) ·
  [Bulk data export](https://developers.google.com/search/blog/2023/02/bulk-data-export) ·
  [BigQuery efficiency tips](https://developers.google.com/search/blog/2023/06/bigquery-efficiency-tips)
- [CrUX API](https://developer.chrome.com/docs/crux/api) ·
  [How to use the CrUX API](https://developer.chrome.com/docs/crux/guides/crux-api) ·
  [CrUX tools](https://developer.chrome.com/docs/crux/methodology/tools)
- [PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started) —
  note Google's stated plan to drop field data from it.
- [Using Search Console and Google Analytics data for SEO](https://developers.google.com/search/docs/monitor-debug/google-analytics-search-console)

## Tier 2 — published measurement

Correlational or sampled. Always quote the sample, the date, and the caveat; never present as
causal. Every one of these is published by a vendor selling visibility tooling.

| Study | Sample | Finding used here |
|---|---|---|
| [Ahrefs — 76% of AI Overview citations pull from the top 10](https://ahrefs.com/blog/search-rankings-ai-citations/) | 1.9M citations across 1M AI Overviews, July 2025 | 76.1% of cited pages rank top 10; 14.4% rank nowhere in the top 100; median position of first citation is 2 |
| [Ahrefs — top brand visibility factors](https://ahrefs.com/blog/ai-brand-visibility-correlations/) | 75,000 brands, ChatGPT / AI Mode / AI Overviews, Spearman | YouTube mentions 0.737; branded web mentions 0.656–0.709; DR 0.266–0.326; backlinks very weak. Authors state correlation is not causation |
| [Ahrefs — AI Overview brand visibility factors](https://ahrefs.com/blog/ai-overview-brand-correlation/) | 75,000 brands | Brand web mentions 0.664 versus backlinks 0.218 |
| [Semrush / Kevin Indig — ghost citations](https://www.semrush.com/blog/the-ghost-citations-study/) | 3,981 domain appearances, 115 prompts, 14 countries, June 2026 | 61.7% cited without a brand mention; Gemini names 83.7% / cites 21.4%; ChatGPT cites 87% / names 20.7%; comparative content 2.4× more mentions |
| [Semrush 2026 AI Visibility Index](https://www.semrush.com/news/463141-semrush-releases-expanded-2026-ai-visibility-index-analyzing-126-million-ai-search-prompts/) | 126M US AI prompts, Jan–Apr 2026 | Scale and platform mix of AI answer sourcing |
| [Ahrefs — 137K sites, llms.txt](https://ahrefs.com/blog/llmstxt-study/) | 137,210 domains, May 2026 | 97% of `llms.txt` files received zero requests; AI search bots made only hundreds of fetches |
| [Pew Research, via Search Engine Land](https://searchengineland.com/google-ai-overviews-hurting-clicks-study-459434) | Browsing data from 900 US adults | 8% click-through with an AI Overview versus 15% without; 1% clicked a link inside the summary; median zero-click 80% versus 60% |

## Tier 3 — reported announcements and commentary

Useful for dates and enforcement history; confirm against Tier 1 before quoting as policy.

- [Google to no longer support FAQ rich results](https://searchengineland.com/google-to-no-longer-support-faq-rich-results-476957) —
  the 7 May / June / August 2026 timeline.
- [Google to remove more search features](https://searchengineland.com/google-to-remove-more-search-features-including-practice-problems-nutrition-facts-nearby-offers-and-more-464255).
- [Search Console AI performance reports and controls to block content in AI responses](https://searchengineland.com/google-search-console-ai-performance-reports-and-controls-to-block-your-content-in-ai-responses-479298) —
  the opt-out toggle, announced 3 June 2026, initially for a subset of UK site owners.
- [Google Search Console AI performance reports rolling out to more users](https://searchengineland.com/google-search-console-ai-performance-reports-rolling-out-to-more-users-480867).
- [Google says llms.txt is purely speculative for now](https://www.searchenginejournal.com/google-says-llms-txt-is-purely-speculative-for-now/577576/).
- [Google explains why they need to control ranking signals](https://www.searchenginejournal.com/google-explains-why-they-need-to-control-their-ranking-signals/553657/) —
  Illyes on social signals.
- [Google again says: we don't use social media for ranking](https://www.seroundtable.com/again-google-doesnt-use-social-media-for-ranking-22200.html).
- [John Mueller rebuts the idea that Google uses a domain authority signal](https://www.searchenginejournal.com/domain-authority/246515/).
- [Site reputation abuse: first-party involvement](https://searchengineland.com/google-site-reputation-abuse-policy-now-includes-first-party-involvement-or-oversight-of-content-448432)
  and [manual actions in Europe](https://searchengineland.com/google-manual-actions-site-reputation-abuse-europe-451046).
- [ChatGPT Search makes Microsoft Bing an SEO priority](https://searchengineland.com/chatgpt-search-microsoft-bing-seo-448019).

## What this package deliberately does not cite

- Ranking-factor lists and vendor authority scores. Google does not publish a factor list and does
  not use a third-party authority metric.
- Prompt-sampling "AI visibility" trackers as measurement. Google states no third-party tool has
  access to its ranking or AI systems.
- Market-size forecasts for AI or agentic commerce. Projections are not evidence for a technical
  decision.
- Undated blog posts restating other blog posts. Where a claim here comes from commentary, the
  primary announcement is cited beside it.
