# AI search: being retrieved and cited

Read this when the goal is visibility in AI Overviews, Google AI Mode, ChatGPT, Copilot, Perplexity,
or Gemini — or when someone proposes "GEO"/"AEO" work.

Claims below are labelled **documented** (the platform says so) or **measured** (a published study
found it). Measured findings are correlational unless stated otherwise, and vendors publishing them
sell visibility tools.

## Start from what the platforms document

### Google

**Documented.** Google's own guide states the position bluntly: "From Google Search's perspective,
optimizing for generative AI search is optimizing for the search experience, and thus still SEO," and
"the best practices for SEO continue to be relevant because our generative AI features on Google
Search are rooted in our core Search ranking and quality systems."

Eligibility requirements, all of them ordinary SEO:

- The page must be **indexed**, **crawlable**, and **eligible to be shown with a snippet**.
- The site must meet the standard Search technical requirements.

Two retrieval mechanisms Google names:

- **Retrieval-augmented generation** — answers grounded in indexed content, with clickable links to
  supporting pages.
- **Query fan-out** — the model generates related queries beyond the one typed, so a page can be
  retrieved for a question the user never asked in those words.

**What Google says is not needed** — quoted, because each of these is actively sold as a service:

| Proposed tactic | Google's position |
|---|---|
| `llms.txt` and other "special" markup | "Google Search itself doesn't use them"; doing so "will neither harm nor help your site's visibility" |
| Chunking content into small pieces | "No requirement to break your content into tiny pieces" |
| A distinct writing style for AI | "You don't need to write in a specific way just for generative AI search" |
| Structured data for AI | "Structured data isn't required for generative AI search" |
| Pages for every query variation | The systems "can understand synonyms and general meanings" |
| Buying or arranging mentions | "Seeking inauthentic 'mentions' isn't as helpful as it might seem" |

Google also warns that generating pages around harvested question queries "primarily to manipulate
rankings" violates the scaled content abuse policy.

### OpenAI

**Documented** ([OpenAI bots](https://developers.openai.com/api/docs/bots)). Four separate agents, and
conflating them is the most expensive mistake available here:

| User agent | Purpose | Effect of blocking |
|---|---|---|
| `OAI-SearchBot` | Surfaces sites in ChatGPT search | "Sites that are opted out of OAI-SearchBot will not be shown in ChatGPT search answers" |
| `GPTBot` | Training data for foundation models | "Disallowing GPTBot indicates a site's content should not be used in training" — no effect on search visibility |
| `ChatGPT-User` | Fetches a page when a user's prompt requires it | User-initiated, so "robots.txt rules may not apply" |
| `OAI-AdsBot` | Validates ad landing pages | Only visits submitted ad pages |

Each publishes an IP list for verification (`openai.com/searchbot.json` and siblings). **Blocking
`GPTBot` does not remove a site from ChatGPT's answers, and blocking `OAI-SearchBot` does.** A site
that blocked "OpenAI" by copying a 2023 robots.txt snippet may have made exactly the wrong trade.

### Anthropic, Perplexity, Google training

- Anthropic runs separate robots for training, search, and user-directed retrieval, and states
  `ClaudeBot` "adheres to industry-standard practices with respect to the robots.txt instructions"
  ([Anthropic help centre](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)).
- `Google-Extended` controls Gemini training and grounding **outside** Search. It does not affect AI
  Overviews or AI Mode, which are governed by Googlebot access.
- `Claude-Web` and `anthropic-ai` are retired strings. A robots.txt blocking only those blocks
  nothing today.
- robots.txt is a request. Non-compliant crawling has been documented; enforce at the edge if the
  requirement is real.

### Microsoft

ChatGPT and other assistants have historically drawn on the Bing index, so absence from Bing is
absence from those answers. Bing Webmaster Tools added an **AI Performance** report (public preview,
February 2026) reporting total citations, average cited pages, grounding queries, and page-level
citation activity across Microsoft Copilot and Bing AI summaries. Microsoft recommends IndexNow so AI
systems reference the current version of a page.

## What the measurements show

**Ranking still drives citation.** Ahrefs analysed 1.9 million citations across 1 million AI
Overviews (July 2025): **76.1% of cited pages rank in the top 10** of organic results, 9.5% rank
11–100, and 14.4% do not rank in the top 100 at all. Median organic position of the first cited URL
was 2. The relationship is described as "positive yet moderate" — ranking is the strongest available
lever, not a guarantee, and roughly one citation in seven goes to a page that ranks nowhere.

**Brand mentions correlate far more than backlinks.** Ahrefs, 75,000 brands across ChatGPT, AI Mode
and AI Overviews (Spearman correlations): YouTube mentions **0.737**; branded web mentions
**0.656–0.709**; branded anchors 0.511–0.628; branded search volume 0.352–0.466; Domain Rating
0.266–0.326; raw backlink counts "very weak" (~0.218 in the AI Overviews study). The authors state
plainly that correlation is not causation and that improving these metrics is not proven to raise AI
visibility.

**Being cited is not being named.** Semrush with Kevin Indig analysed 3,981 domain appearances across
115 prompts in 14 countries on ChatGPT, AI Overviews, Gemini and AI Mode (June 2026): **61.7% were
"ghost citations"** — the source was linked but the brand was never named. 13.2% got both; 25.1% were
named without a link. Platform behaviour diverges sharply: Gemini named brands in 83.7% of appearances
but cited only 21.4%; ChatGPT cited 87% but named only 20.7%. Comparative content produced 2.4× more
mentions than informational content.

**Clicks fall when an AI answer is present.** Pew Research, browsing data from 900 US adults: users
clicked a result on **8% of searches with an AI Overview versus 15% without**, and clicked a link
inside the summary on 1% of visits. Median zero-click rate was 80% with an AI Overview against 60%
without.

**`llms.txt` is not being read.** Ahrefs checked 137,210 domains in May 2026: **97% of `llms.txt`
files received zero requests**. Among the 3% that saw any traffic, AI bots were 19.5% of it, and
OAI-SearchBot, PerplexityBot and Claude's search crawler made only a couple of hundred fetches
between them. AI bots did not probe for the file on domains lacking it. Google's Gary Illyes and John
Mueller have both said Google does not support it and has no plan to.

## What to actually do

In order, and the first four are just SEO done properly:

1. **Be indexable, crawlable, and snippet-eligible.** A `nosnippet` directive removes the page from
   AI features that quote it. Check for it before diagnosing anything else.
2. **Rank.** Three quarters of AI Overview citations come from the top 10; there is no separate ladder
   to climb.
3. **Allow the search crawlers you want traffic from.** Audit robots.txt per user agent and be
   deliberate about training versus search.
4. **Answer the question near the top of the page**, under a heading that matches how it is asked, so
   an extractable passage exists. This is retrieval mechanics, not a writing style.
5. **Publish the thing only you can publish** — original data, first-hand testing, named expertise.
   Google's guide asks directly for content that could not "easily be produced by a generative AI
   model."
6. **Earn mentions where the answers are drawn from**: coverage, documentation, community answers,
   video. The correlational evidence points here harder than at links. Do it by being worth citing;
   inauthentic mentions are called out by Google and by the studies' own caveats.
7. **Write comparison and alternatives pages** if the category has them. That is the format the
   mention data favours.
8. **Keep pages current** and signal it honestly; freshness weighs more on retrieval-first surfaces.

## What not to do

- Do not build `llms.txt` and report it as an AI-visibility deliverable. It is cheap, harmless, and
  useful only for AI *coding* tools reading documentation. Say that if asked to add one.
- Do not sell chunking, "AI-optimized" phrasing, or schema as an AI ranking mechanism. Google denies
  all three.
- Do not block `GPTBot` and assume ChatGPT visibility is retained, or block `OAI-SearchBot` and wonder
  where the referrals went.
- Do not promise citation counts. No third-party tool has access to these systems' internals — Google
  states this explicitly — and every published figure is a sample of prompts, not a measurement of
  the system.
- Do not treat "GEO" as a separate discipline requiring a separate budget line. Every documented
  requirement is an SEO requirement.

## Measuring it

- **Google:** the Search Generative AI performance report in Search Console (announced 3 June 2026)
  reports **impressions** in AI Overviews and AI Mode, plus pages, countries, devices and dates.
  **No click data.** Rolling out incrementally. A separate opt-out toggle, first tested with UK site
  owners, removes a site from AI features — Google says opted-out sites "will not receive traffic or
  impressions from our generative AI features," and that the control is not a web-ranking signal.
- **Microsoft:** the Bing Webmaster Tools AI Performance report, for Copilot and Bing AI summaries.
- **Referrals:** GA4 added a native "AI Assistant" channel on 13 May 2026; it does not cover every
  platform, and a large share of AI referrals arrive with no referrer and land in Direct. See
  `references/measurement.md`.
- **Server logs** by user agent are the only ground truth for which AI crawlers actually fetch what.

## Sources

- [Optimizing for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Introducing Search Generative AI performance reports](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)
- [OpenAI bots](https://developers.openai.com/api/docs/bots)
- [Anthropic: does Anthropic crawl data from the web?](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)
- [Introducing AI Performance in Bing Webmaster Tools](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview)
- [Ahrefs: 76% of AI Overview citations pull from the top 10](https://ahrefs.com/blog/search-rankings-ai-citations/) — 1.9M citations, 1M AI Overviews
- [Ahrefs: top brand visibility factors in ChatGPT, AI Mode and AI Overviews](https://ahrefs.com/blog/ai-brand-visibility-correlations/) — 75,000 brands
- [Ahrefs: an analysis of AI Overview brand visibility factors](https://ahrefs.com/blog/ai-overview-brand-correlation/)
- [Semrush: why 62% of AI citations don't lead to brand mentions](https://www.semrush.com/blog/the-ghost-citations-study/) — 3,981 appearances, 115 prompts, 14 countries
- [Semrush 2026 AI Visibility Index](https://www.semrush.com/news/463141-semrush-releases-expanded-2026-ai-visibility-index-analyzing-126-million-ai-search-prompts/) — 126M prompts
- [Ahrefs: we analyzed 137K sites — 97% of llms.txt files never get read](https://ahrefs.com/blog/llmstxt-study/)
- [Google says llms.txt is purely speculative for now](https://www.searchenginejournal.com/google-says-llms-txt-is-purely-speculative-for-now/577576/)
- [Pew Research on AI Overviews and clicks, via Search Engine Land](https://searchengineland.com/google-ai-overviews-hurting-clicks-study-459434)
- [ChatGPT Search makes Microsoft Bing an SEO priority](https://searchengineland.com/chatgpt-search-microsoft-bing-seo-448019)
- [IndexNow](https://www.indexnow.org/documentation)
