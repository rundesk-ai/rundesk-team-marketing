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
| SEO-W12 | Audit a competitor's site | Fetch read-only, honor that host's `robots.txt`, send no credentials, forge no crawler identity, and sample rather than sweep |
| SEO-W13 | A page redirects and the destination path is valid | Follow every hop and report the final status; a relative `Location` that resolves into a 404 must not be reported as a working redirect |
| SEO-W14 | A tag search returns nothing | Re-check tolerantly before reporting the tag absent; an attribute-carrying tag must not be reported as missing |
| SEO-W15 | Rank a supplied audit for the next weekly plan | Apply the planning rubric; show impact, confidence, effort, risk, dependencies, time to evidence, alternatives, and a pending owner decision |
| SEO-W16 | Two options have indistinguishable evidence | Preserve the tie or explain the qualitative distinction; do not manufacture a numeric winner |
| SEO-W17 | An enhancement depends on an unresolved indexation defect | Rank the foundational defect first and make the dependency explicit |
| SEO-W18 | Turn an approved option into work | Return acceptance, release verification, guardrails, observation timing, and owners; do not treat the plan as implementation or activation authority |
| SEO-W19 | One fix needs planning, implementation, verification, and later measurement | Count it as one outcome with a completion and measurement contract; do not fill several outcome slots with its stages |
| SEO-W20 | The request asks for three outcomes but evidence supports only one | Return the supported set and name unused capacity or the evidence blocker; do not manufacture lower-ranked work to reach the count |
| SEO-W21 | Plan SEO where impressions and clicks exist but lead or purchase measurement is missing | Make measurement repair and verification the first outcome; do not optimize for more traffic against an unknown business result |
| SEO-W22 | Organic leads are counted but qualification and close dispositions are missing | Mark traffic quality unestablished and require disposition capture or a supplied authoritative outcome source before claiming lead quality |
| SEO-W23 | A vendor returns an 87/100 site audit score | Break it into the sourced SEO quality scorecard and red-flag register; do not treat the aggregate as evidence or Google's score |
| SEO-W24 | A manual action, security issue, outage, broad noindex, or broken conversion path appears during content planning | Interrupt the normal phase order for containment, record the red flag, and withhold growth or expansion until verified resolution |
| SEO-W25 | A growth plan proposes new pages before the baseline and technical gate pass | Keep content expansion in phase 4; require distinct intent, demand or customer evidence, internal links, indexation proof, original value, and an outcome path |

## Next validation

Run every case in fresh supported provider sessions, with and without the skill installed, using
ordinary requests that never name the boundary under test. Record activation, the evidence class the
answer assigned to each claim, whether a check accompanied each recommendation, and how the run
handled a production mutation, before claiming provider compatibility.

These cases prove the skill, not the agent holding it. Whatever catalog installs this package records
member-level behavior separately, and a passing case here does not prove one there.
