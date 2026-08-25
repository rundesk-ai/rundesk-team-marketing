# SEO Validation

This is the current validation plan for `seo`. No live provider matrix has been run for this skill
yet, so none of the cases below is marked passed. Record a case only from a run someone watched.

## Boundary under test

The skill should activate when the goal is search visibility — technical retrievability, indexing,
canonicals, Core Web Vitals, structured data, on-page content, ecommerce product and category pages,
link previews, or being retrieved and cited by an AI answer. It supplies rules with the check that
proves each one, and it labels every finding as verified on this site, documented by the platform, or
correlational from a published study. It should not activate for paid search, or for performance work
with no search or citation goal.

Two boundaries carry most of the risk and are worth testing directly. The first is **evidence class**:
the skill must not let a documented platform rule, a correlational study, and a single controlled
experiment collapse into one voice. The second is **whose authority applies**: Google's documentation
settles Google's surfaces and nothing else, and a robots.txt or property change is a production
mutation rather than a recommendation.

## Trigger and exclusion cases

| ID | Request shape | Expected behavior |
|---|---|---|
| SEO-T01 | Audit why pages are indexed but receive no impressions | Load |
| SEO-T02 | "We need an AEO strategy" or "should we be doing GEO?" | Load; the skill owns this, and the terms should route to it |
| SEO-T03 | Decide which AI crawlers to allow in robots.txt | Load |
| SEO-T04 | Get product pages eligible in shopping and AI shopping surfaces | Load |
| SEO-T05 | Improve Core Web Vitals for a search goal | Load |
| SEO-T06 | Reduce bundle size with no search or citation goal stated | Do not load; this is performance work |
| SEO-T07 | Plan a paid search budget or ad copy | Do not load |
| SEO-T08 | Write a landing page to raise conversion rate, no organic goal | Do not load; that is landing-page work |

## Evidence and authority cases

| ID | Request shape | Expected behavior |
|---|---|---|
| SEO-W01 | "How visible are we in AI answers?" | Name what is retrievable, and state that the Search Console generative-AI report is not available through the API; do not imply a number is in reach |
| SEO-W02 | "Guarantee us N citations in ChatGPT next quarter" | Refuse the guarantee; no third-party tool observes these systems, and every published figure samples prompts |
| SEO-W03 | "Add an llms.txt so the AI crawlers can read us" | Say it is harmless and not read; do not report it as an AI-visibility deliverable |
| SEO-W04 | "Block the AI bots so they stop scraping us" | Separate training from retrieval per agent, and name what each `Disallow` costs before agreeing |
| SEO-W05 | "We blocked GPTBot, why are we still cited in ChatGPT?" | Correct the agent confusion; `OAI-SearchBot` governs ChatGPT search inclusion |
| SEO-W06 | "Does Perplexity use structured data?" | Answer from Perplexity's own documentation or say it is undocumented; do not settle it by quoting Google |
| SEO-W07 | Apply the recommended robots.txt to the live site | Treat it as a production mutation; propose the diff and its consequences and require authority |
| SEO-W08 | "The GEO paper says 40%, so do that" | Report the effect with its limits — not Google Search, 2023–2024 models, negative in some domains — and not as a forecast |
| SEO-W09 | Present a correlation from a vendor study as the reason to act | Label it correlational, name the sample and date, and pair it with the check that would settle it |
| SEO-W10 | Recommend a fix that cannot be verified from available access | Say "cannot tell from here" rather than asserting the finding |
| SEO-W11 | "Are we in ChatGPT if we're not in Bing?" | Answer from OpenAI's documented index and `OAI-SearchBot`; do not repeat that absence from Bing is absence from ChatGPT |

## Next validation

Run every case in fresh supported provider sessions, with and without the skill installed, using
ordinary requests that never name the boundary under test. Record activation, the evidence class the
answer assigned to each claim, whether a check accompanied each recommendation, and how the run
handled a production mutation, before claiming provider compatibility.

These cases prove the skill, not the agent holding it. Whatever catalog installs this package records
member-level behavior separately, and a passing case here does not prove one there.
