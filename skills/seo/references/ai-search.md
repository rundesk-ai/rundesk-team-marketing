# AI search: being retrieved and cited

Read this when the goal is visibility in AI Overviews, Google AI Mode, ChatGPT, Copilot, Perplexity,
or Gemini — or when someone proposes "AEO" or "GEO" work.

**The two acronyms, since the position below depends on what they claim.** *Answer engine
optimization* (AEO) and *generative engine optimization* (GEO) both name the practice of getting a
page retrieved and cited by a system that answers in prose instead of listing links. GEO is the term
with a research literature behind it; AEO is used interchangeably in the market. Neither is a
platform's term, and no engine documents a ranking system by either name.

Claims below are labelled **documented** (the platform says so), **measured** (a published study
found it, correlational unless stated otherwise), or **experimental** (a controlled study
manipulated content and observed the effect). Vendors publishing measured findings sell visibility
tools. Weigh the three accordingly and never present one as another.

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

**Read the scope of that table before quoting it.** Google is describing Google's AI features. It is
authoritative for AI Overviews and AI Mode and it is not evidence about ChatGPT, Perplexity, or
Copilot, which retrieve from indexes Google does not operate. Citing Google to settle a question
about another engine is the most common way this file gets misused. Where the engines genuinely
differ, the difference is documented per platform below.

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

The existence of `OAI-SearchBot` is also the answer to "is ChatGPT just Bing?" — OpenAI documents its
own search index and tells site owners to allow its crawler to appear in it. See the Microsoft
section for what that changes.

### Anthropic

**Documented** ([Anthropic crawler
support](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler)).
The same three-way split as OpenAI, and naming only the first of the three is the common error:

| User agent | Purpose |
|---|---|
| `ClaudeBot` | Collects content for model development and training |
| `Claude-SearchBot` | Indexes content to support search responses |
| `Claude-User` | Fetches a page when a user's prompt requires it |

Anthropic states its bots "respect 'do not crawl' signals by honoring industry standard directives in
robots.txt", publishes authorized IPs at `claude.com/crawling/bots.json`, and asks that rules be
applied to every subdomain intended to be covered. `Claude-Web` and `anthropic-ai` are retired
strings; a robots.txt blocking only those blocks nothing today.

### Perplexity

**Documented** ([Perplexity bots](https://docs.perplexity.ai/guides/bots)). Two agents, and the
distinction is the same one that matters everywhere else:

| User agent | Purpose |
|---|---|
| `PerplexityBot` | "designed to surface and link websites in search results on Perplexity. It is not used to crawl content for AI foundation models" |
| `Perplexity-User` | "supports user actions within Perplexity" — visits a page to answer a specific prompt; "not used for web crawling or to collect content for training AI foundation models" |

Perplexity recommends allowing `PerplexityBot` and permitting its published IP ranges. It states that
`Perplexity-User` "generally ignores robots.txt rules" because a user requested the fetch — the same
user-initiated carve-out OpenAI and Anthropic document.

### Microsoft

Bing Webmaster Tools added an **AI Performance** report (public preview, February 2026) reporting
total citations, average cited pages, grounding queries, and page-level citation activity across
Microsoft Copilot and Bing AI summaries. Microsoft recommends IndexNow so AI systems reference the
current version of a page.

**Do not repeat the old rule that absence from Bing is absence from ChatGPT.** That was a reasonable
reading in 2024. It is no longer safe: OpenAI documents its own index and its own indexing crawler,
so ChatGPT inclusion is governed by `OAI-SearchBot` access, not by Bing. What remains true is
narrower and still worth saying — Bing presence governs **Copilot and Bing's own AI answers**, and
those are the surfaces the Bing AI Performance report measures.

## Crawler access is a decision, not a checkbox

"Audit robots.txt per user agent" is the step most often stated and least often performed. The
decision has three separable stakes, and most bad robots.txt files come from treating them as one:

- **Training** — may the content be used to build a future model? No referral traffic either way.
- **Retrieval** — may the content be indexed so it can be cited in an answer? This is the one that
  costs referrals when it is blocked.
- **User-initiated fetch** — may the engine open the page because a person asked it to? Every vendor
  above treats this as outside robots.txt.

Grouped by what a `Disallow` actually costs:

| Agent | Class | What `Disallow` costs |
|---|---|---|
| `OAI-SearchBot` | retrieval | Removal from ChatGPT search answers |
| `Claude-SearchBot` | retrieval | Removal from Claude's search results |
| `PerplexityBot` | retrieval | Removal from Perplexity's results |
| `Googlebot` | retrieval | Removal from Search — and therefore from AI Overviews and AI Mode |
| `bingbot` | retrieval | Removal from Bing, Copilot, and Bing AI answers |
| `GPTBot` | training | Nothing in search visibility |
| `ClaudeBot` | training | Nothing in search visibility |
| `Google-Extended` | training | Gemini training and grounding **outside** Search; no effect on AI Overviews or AI Mode |
| `Applebot-Extended` | training | Apple foundation-model training only; Apple documents that it does not crawl and that disallowing it still leaves pages eligible for search results |
| `CCBot` | training | Nothing directly; Common Crawl's archive is a common training input |
| `Amazonbot` | training | Amazon products and model training; Amazon documents that it honors `noarchive` as "do not use the page for model training" |
| `ChatGPT-User`, `Claude-User`, `Perplexity-User` | user-initiated | Nothing reliably — every vendor documents that robots.txt may not apply |

The shape most publishers actually want — allow retrieval, refuse training — looks like this:

```text
# Retrieval: these earn citations and referrals. Allow them.
User-agent: OAI-SearchBot
User-agent: Claude-SearchBot
User-agent: PerplexityBot
Allow: /

# Training: no referral value. Block only if that is a deliberate policy.
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: CCBot
Disallow: /
```

Three things to say whenever this comes up:

- **robots.txt is a request.** Non-compliant crawling has been documented. If the requirement is a
  real one, enforce it at the edge and verify against the published IP lists, because user-agent
  strings are trivially forged.
- **The agent list changes.** Re-read each vendor's own bot page before writing a file; do not copy
  the table above into production without checking it.
- **Editing a live robots.txt is a production mutation.** Propose the diff and the consequence of
  each line; do not deploy it without explicit authority.

## What the measurements show

**Ranking still drives citation.** Ahrefs analysed 1.9 million citations across 1 million AI
Overviews (July 2025): **76.1% of cited pages rank in the top 10** of organic results, 9.5% rank
11–100, and 14.4% do not rank in the top 100 at all. Median organic position of the first cited URL
was 2. The relationship is described as "positive yet moderate" — ranking is the strongest available
lever, not a guarantee, and roughly one citation in seven goes to a page that ranks nowhere.

**Brand mentions correlate far more than backlinks.** Ahrefs, 75,000 brands across ChatGPT, AI Mode
and AI Overviews (12 December 2025, Spearman correlations): YouTube mentions **0.737**; branded web
mentions **0.656–0.709**; branded anchors 0.511–0.628; branded search volume 0.352–0.466; Domain
Rating 0.266–0.326. Link metrics land at the bottom: the authors report "very weak correlations
between link metrics ('number of backlinks' and 'URL rating') and brand mentions across all AI
systems", and give no figure for them in the text — the earlier AI Overviews study of 26 May 2025
put backlinks at 0.218 against 0.664 for branded web mentions. Content volume was weaker still, at
about 0.194 for number of site pages. The authors state plainly that "correlation isn't causation"
and that improving these metrics will not automatically raise AI visibility.

**Being cited is not being named.** Semrush with Kevin Indig analysed 3,981 domain appearances across
115 prompts in 14 countries on ChatGPT, AI Overviews, Gemini and AI Mode (June 2026): **61.7% were
"ghost citations"** — the source was linked but the brand was never named. 13.2% got both; 25.1% were
named without a link. Platform behaviour diverges sharply: Gemini named brands in 83.7% of appearances
but cited only 21.4%; ChatGPT cited 87% but named only 20.7%. Comparative content produced 2.4× more
mentions than informational content.

**Clicks fall when an AI answer is present.** Pew Research Center, browsing data from 900 US adults on
its KnowledgePanel Digital panel, covering March 2025 and published 22 July 2025: users clicked a
result on **8% of searches with an AI Overview versus 15% without**, and clicked a link inside the
summary on 1% of visits. About 18% of the Google searches observed produced an AI summary at all.

**`llms.txt` is not being read.** Ahrefs checked 137,210 domains in May 2026: **97% of `llms.txt`
files received zero requests**. Among the 3% that saw any traffic, AI bots were 19.5% of it, and
OAI-SearchBot, PerplexityBot and Claude's search crawler made only a couple of hundred fetches
between them. AI bots did not probe for the file on domains lacking it. Google's Gary Illyes and John
Mueller have both said Google does not support it and has no plan to.

## What the one controlled experiment shows

Everything above is correlational or observational. One study manipulated the content and measured
the result, and it is the only evidence in this package that can speak to cause.

**Experimental.** *GEO: Generative Engine Optimization* (Aggarwal, Murahari, Rajpurohit, Kalyan,
Narasimhan and Deshpande; KDD '24, August 2024). The authors built GEO-bench — 10,000 queries drawn
from nine datasets across 25 domains — applied nine content modifications to a source, and measured
the change in that source's visibility in the generated answer.

- The top three methods were **Cite Sources**, **Quotation Addition** and **Statistics Addition**,
  which "achieved a relative improvement of 30-40% on the Position-Adjusted Word Count metric and
  15-30% on the Subjective Impression metric."
- **Fluency Optimization** and **Easy-to-Understand** — plain readability work — also produced a
  15–30% boost.
- **Keyword Stuffing did not work.** The paper is explicit: "Compared to baselines, simple methods
  like Keyword Stuffing traditionally used in SEO don't perform well."

State the limits with the finding, because the market quotes the 40% without them:

- The main experiments ran against a generative engine the authors built on GPT-3.5, described as
  closely resembling BingChat's design, with a 200-example validation on Perplexity.ai. **They were
  not run against Google Search**, so this is not a counter-argument to Google's documented position.
- The models and benchmark are 2023–2024 vintage.
- **The gain depends on where the source already ranks, and it can be negative.** Broken out by the
  source's position in the underlying search engine, Cite Sources moved visibility −30.3% for a
  rank-1 source and +115.1% for a rank-5 one; Quotation Addition ran −22.9% to +99.7% the same way.
  The authors' reading: "GEO is especially helpful for lower ranked websites." So "up to 40%" is a
  ceiling, not an expectation, and for a page already cited near the top these edits may cost
  visibility rather than add it.
- Efficacy also varies by subject area, which is why the paper argues for domain-specific choices
  rather than one universal recipe.

What this does and does not license: it supports adding real citations, real quotations and real
statistics to content that lacked them, which is the same thing the "worth citing" rung of the
dependency ladder already asks for. It does **not** license chunking, "AI-optimized" phrasing, or
schema-as-an-AI-lever — none of those was the thing tested, and Google denies all three.

## What to actually do

In order, and the first four are just SEO done properly:

1. **Be indexable, crawlable, and snippet-eligible.** A `nosnippet` directive removes the page from
   AI features that quote it. Check for it before diagnosing anything else — it arrives three ways,
   and a check that greps only for the meta tag will miss two of them:

   ```sh
   curl -sSI https://example.com/page | grep -i 'x-robots-tag'
   curl -sS  https://example.com/page | grep -iE 'name="robots"|max-snippet|data-nosnippet'
   ```

2. **Rank.** Three quarters of AI Overview citations come from the top 10; there is no separate ladder
   to climb. This is not in tension with the experiment above: ranking is what gets a page into the
   candidate set, and the content methods moved visibility most for sources that ranked poorly and
   least — sometimes negatively — for those already at the top.
3. **Allow the search crawlers you want traffic from.** Work the decision table above, per agent, and
   be deliberate about training versus retrieval.
4. **Answer the question near the top of the page**, under a heading that matches how it is asked, so
   an extractable passage exists. This is retrieval mechanics, not a writing style.
5. **Publish the thing only you can publish** — original data, first-hand testing, named expertise.
   Google's guide asks directly for content that could not "easily be produced by a generative AI
   model." This is also where the one controlled experiment points: cite your sources, quote them,
   and carry real numbers.
6. **Make the brand resolvable as an entity.** The correlation data puts branded mentions far above
   links, and a mention only accrues to you if the engine can tell which organization it names. Keep
   one name, one description, and one set of `sameAs` targets across the site and the profiles it
   links to — `Organization` markup is covered in
   [structured data](structured-data.md), and what social profiles do and do not contribute is in
   [social and brand](social-and-brand.md). Treat entity work as making identity unambiguous, not as
   a route to a knowledge panel; nobody documents that route.
7. **Earn mentions where the answers are drawn from**: coverage, documentation, community answers,
   video. The correlational evidence points here harder than at links. Do it by being worth citing;
   inauthentic mentions are called out by Google and by the studies' own caveats.
8. **Write comparison and alternatives pages** if the category has them. That is the format the
   mention data favours.
9. **Keep pages current** and signal it honestly; freshness weighs more on retrieval-first surfaces.

## What not to do

- Do not build `llms.txt` and report it as an AI-visibility deliverable. It is cheap, harmless, and
  useful only for AI *coding* tools reading documentation. Say that if asked to add one.
- Do not sell chunking, "AI-optimized" phrasing, or schema as an AI ranking mechanism. Google denies
  all three.
- Do not block `GPTBot` and assume ChatGPT visibility is retained, or block `OAI-SearchBot` and wonder
  where the referrals went.
- Do not settle a question about ChatGPT, Perplexity or Copilot by quoting Google. Google's denials
  bind Google's surfaces. Cite the engine's own documentation, or say the answer is not documented.
- Do not say that absence from Bing is absence from ChatGPT. It was true of the 2024 arrangement and
  is not true now: OpenAI documents its own index and its own indexing crawler, so `OAI-SearchBot`
  access governs ChatGPT inclusion. Bing presence governs Copilot and Bing's own AI answers, which is
  the narrower claim to make instead.
- Do not promise citation counts. No third-party tool has access to these systems' internals — Google
  states this explicitly — and every published figure is a sample of prompts, not a measurement of
  the system.
- Do not treat "GEO" or "AEO" as a separate discipline requiring a separate budget line. Every
  documented requirement is an SEO requirement, and the one experimental result points at citation
  quality, which the dependency ladder already ranks last-but-most-durable.

## Measuring it

- **Google:** the Search Generative AI performance report in Search Console (announced 3 June 2026)
  reports **impressions** in AI Overviews and AI Mode, plus pages, countries, devices and dates.
  **No click data.** Rolling out incrementally. It is **not available through the Search Console
  API** — see [measurement](measurement.md) — so it is read in the UI or exported, and an agent
  working through the API cannot retrieve it. Say so rather than implying the number is in reach.
  A separate opt-out toggle, first tested with UK site owners, removes a site from AI features —
  Google says opted-out sites "will not receive traffic or impressions from our generative AI
  features," and that the control is not a web-ranking signal.
- **Microsoft:** the Bing Webmaster Tools AI Performance report, for Copilot and Bing AI summaries.
- **Referrals:** GA4 added a native "AI Assistant" channel on 13 May 2026; it does not cover every
  platform, and a large share of AI referrals arrive with no referrer and land in Direct. See
  [measurement](measurement.md).
- **Server logs** by user agent are the only ground truth for which AI crawlers actually fetch what.

## Sources

- [Optimizing for generative AI features on Google Search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Introducing Search Generative AI performance reports](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)
- [OpenAI bots](https://developers.openai.com/api/docs/bots) — `OAI-SearchBot`, `GPTBot`, `ChatGPT-User`, `OAI-AdsBot`, and per-agent IP lists
- [Anthropic: does Anthropic crawl data from the web?](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) — `ClaudeBot`, `Claude-SearchBot`, `Claude-User`
- [Perplexity bots](https://docs.perplexity.ai/guides/bots) — `PerplexityBot` and `Perplexity-User`
- [About Applebot](https://support.apple.com/en-us/119829) — `Applebot-Extended` as a usage control that does not itself crawl
- [Common Crawl: CCBot](https://commoncrawl.org/ccbot)
- [Amazonbot](https://developer.amazon.com/amazonbot) — including `noarchive` as a training opt-out
- [Introducing AI Performance in Bing Webmaster Tools](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview)
- [GEO: Generative Engine Optimization](https://arxiv.org/abs/2311.09735) — KDD '24; GEO-bench, 10,000 queries, nine content methods; the only controlled experiment cited in this package
- [Ahrefs: 76% of AI Overview citations pull from the top 10](https://ahrefs.com/blog/search-rankings-ai-citations/) — 1.9M citations, 1M AI Overviews, July 2025
- [Ahrefs: top brand visibility factors in ChatGPT, AI Mode and AI Overviews](https://ahrefs.com/blog/ai-brand-visibility-correlations/) — 75,000 brands, 12 December 2025
- [Ahrefs: an analysis of AI Overview brand visibility factors](https://ahrefs.com/blog/ai-overview-brand-correlation/) — 75,000 brands, 26 May 2025
- [Semrush: why 62% of AI citations don't lead to brand mentions](https://www.semrush.com/blog/the-ghost-citations-study/) — 3,981 appearances, 115 prompts, 14 countries
- [Semrush 2026 AI Visibility Index](https://www.semrush.com/news/463141-semrush-releases-expanded-2026-ai-visibility-index-analyzing-126-million-ai-search-prompts/) — 126M prompts
- [Ahrefs: we analyzed 137K sites — 97% of llms.txt files never get read](https://ahrefs.com/blog/llmstxt-study/)
- [Google says llms.txt is purely speculative for now](https://www.searchenginejournal.com/google-says-llms-txt-is-purely-speculative-for-now/577576/)
- [Pew Research Center: Google users are less likely to click on links when an AI summary appears](https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/) — 900 US adults, March 2025 browsing data
- [IndexNow](https://www.indexnow.org/documentation)
