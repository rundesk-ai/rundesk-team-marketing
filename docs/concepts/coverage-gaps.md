# Coverage gaps

What this catalog's roles imply that its shipped skills and integrations cannot yet deliver. Every
row is a limitation observed in this repository, not a roadmap commitment. Read it before granting a
member new work, promising an evidence class to a caller, or adding a package.

The boundaries these gaps are measured against are in [AGENTS.md](../../AGENTS.md): growth evidence is
retrieved and re-retrievable, external research is cited to a published source, and first-party
analysis is certified with a denominator or returned as unestablished.

## Evidence Beacon's role implies but cannot retrieve

| Missing | What exists today | What would close it |
|---|---|---|
| AI-answer visibility measurement | [`seo`](../../skills/seo/references/ai-search.md) documents the platform rules and the published studies; Search Console's generative-AI report exists but returns impressions only, with no clicks and no queries, and reaches a person through the UI and its export rather than any member | An API path to that report. [`google-search-console`](https://github.com/rundesk-ai/rundesk-skills-google/blob/main/skills/google-search-console/references/cli.md) still accepts only `web`, `image`, `video`, `news`, `discover`, and `googleNews` for its search type, and no generative-AI value is documented. Its `searchAppearance` dimension passes through verbatim, so a future Google-side value would arrive without a client change — but none exists to request today |
| AI referral traffic, named as such | GA4 assigns a native `AI Assistant` channel, and [`google-analytics`](https://github.com/rundesk-ai/rundesk-skills-google/blob/main/skills/google-analytics/references/cli.md) can read it through a `channel` or `source` breakdown; no skill in this catalog told a member that path exists until now, and the custom channel group covering the platforms GA4 misses is a property configuration that package refuses by contract | Either a configuration-capable analytics path, which is a broader permission than this team holds, or acceptance that the native channel plus a source breakdown is the readable floor. The measured number is a floor regardless: a large share of AI referrals arrive with no referrer and land in Direct |
| AI citation counts on Microsoft surfaces | none | A Bing Webmaster Tools package; its AI Performance report is the only source that reports citations rather than impressions |
| Which AI crawler fetched what | none | Server-log evidence, which [`measurement`](../../skills/seo/references/measurement.md) calls the only ground truth for crawler behavior |
| Core Web Vitals trend | [`google-pagespeed-insights`](https://github.com/rundesk-ai/rundesk-skills-google/blob/main/skills/google-pagespeed-insights/SKILL.md) returns one 28-day field snapshot and excludes history by contract | A CrUX History source. Field data is also the portion Google plans to discontinue from PageSpeed Insights |
| Query demand and volume | Search Console reports only queries the property already ranks for, so it cannot show an absent one. [`researching-markets`](../../skills/researching-markets/references/demand-signals.md) now gives Scout a method for characterizing demand from series that exist, and for saying what each cannot establish | A demand source. None of the available series measures query volume for an absent query, so this stays uncloseable by method alone — the method's contribution is an honest bound rather than a number |
| A guarded retrieval package | [`seo`](../../skills/seo/references/retrieval.md) now fixes the check set, the guardrails for a host the property does not own, and the redirect and tag-matching traps, so two audits of one site agree. It remains guidance a member may follow rather than a boundary anything enforces, and `inspect-url` still works only on a verified property | A bounded package that can only `GET` and `HEAD`, refuses private and loopback addresses, sends no credentials, and returns the check set as structured output. Guidance closes the consistency gap; only a package closes the enforcement one |

## Measurement evidence Beacon's role implies but cannot query

Beacon certifies first-party and supplied data alongside growth evidence. It holds two analytics
report APIs, a payment API, Search Console, and a method for data that arrives as a file rather than
from a query.

An earlier version of this table claimed the team had no SQL access. That was wrong and is corrected
here: the PostHog package runs read-only HogQL through `query --sql`, accepting a single `SELECT` or
`WITH`, refusing write and DDL keywords, and forcing a `LIMIT`. Arbitrary SQL over PostHog's own
event and person tables is available. What is missing is a *cross-system* warehouse, which is a
narrower and more accurate claim.

| Missing | Consequence |
|---|---|
| A cross-system warehouse | Custom denominators and backfills exist inside PostHog through HogQL, but a join across PostHog, GA4, and the payment system has no home. Reconciliation across them is done by hand, one bridge at a time, and its cost scales with the number of sources |
| Search Console bulk export to BigQuery | The only source that removes the API's row limits and 16-month window, and the only path to long-tail and cannibalization analysis at scale. It is not retroactive, so it must be configured before it is needed |
| CRM or lead-outcome data | The [`stripe`](https://github.com/rundesk-ai/rundesk-skills-integrations/blob/main/skills/stripe/SKILL.md) package reaches the system that accepted the money, so certifying purchase value is possible. Certifying a *lead* outcome still is not: whether a lead was reached, qualified, or won lives in a CRM no integration reaches, so [`value-and-revenue`](../../skills/analyzing-growth-data/references/value-and-revenue.md) can only tell Beacon to name the last established stage and treat the rest as unmeasured |
| An experiment platform | Assignment, sample-ratio checks, and exposure logging are methods Beacon owns with no tool behind them |
| Any enforcement of the file-integrity checks | [`verifying-datasets`](../../skills/verifying-datasets/SKILL.md) fixes the profile and the check list so two verifications of one file agree. It remains guidance a member may follow rather than something that runs, and the 2026-08-25 runs showed the cost: one run counted columns with a naive split and reported its own parser as a defect in the data, and two runs read the same round row count without raising truncation. The guidance now names a quote-aware reader; nothing enforces that it is used | A package that profiles a file and returns the check set as structured output. Guidance closes the wording gap; only a package closes the enforcement one, which is the same distinction the Beacon retrieval row draws |

## Capabilities no member owns

| Missing | Consequence |
|---|---|
| Paid, email, lifecycle, organic-social acquisition strategy, affiliate, and marketplace methods | Quill can draft organic social copy from approved direction, but no member selects social opportunities, operates accounts, or measures social performance. Beacon's routing covers organic search, landing paths, and product feeds, and [`seo`](../../skills/seo/SKILL.md) excludes paid search by contract |
| Brand, positioning, and pricing method | Scout can research what others published about them; no skill turns that into a position or a price |

## Boundaries no instruction draws

Each row was observed in the Beacon runs recorded in [team validation](../guides/team-validation.md), and
the working-tree row was reproduced by Scout.

| Missing | What exists today | What would close it |
|---|---|---|
| Behavioral proof for Scout's write boundary | Beacon's rule held on 2026-08-25 and Quill's corresponding boundary held on 2026-08-26. Scout carries the same local-placement boundary after two runs reproduced the defect, but its revised instruction has not been forward-tested | Run a fresh placement case for Scout. Beacon's remedy is proved forward but not against the original failure, so `BEACON-B01` stays partial |
| Evidence that guidance was applied, not merely available | The runs had the corrected AI-search reference open and one still repeated a claim that reference retires. The claim is now also listed among the things not to say, which is the scannable place rather than the explanatory one | Nothing in this repository closes this in general. It is the argument for running cases rather than grepping wording, and for re-running them after guidance changes; `SEO-W11` tests this specific instance |

## Known package limitations shipped as-is

[`seo`](../../skills/seo/SKILL.md) has diverged from the `rundesk-skills` package it was adapted from.
The AI-search guidance, the snippet-control checks, the skill description, and `references/validation.md`
exist only here. The divergence is deliberate and its provenance is recorded in
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md), but it is a maintenance cost: a correction made
upstream no longer reaches this copy, and the two descriptions now route differently. Anyone reading
the upstream package should not assume it is the one a member of this team received.

## Deliberate exclusions

These are settled decisions, not gaps. Do not close them without the owner's approval.

- No member operates a campaign, spends money, contacts a consumer, or publishes.
- No member approves a legal or regulated claim. A compliance gate can be identified and never
  approved around.
- Landing-page work ends with a ranked plan, measurement contract, experiment backlog, and handoff.
  Content, design, development, analytics implementation, launch, and rendered verification remain
  with their owning teams.
- Technical documentation belongs to the development team, not Quill or this catalog.
- Quill may draft organic social content, but account access, posting, scheduling, community
  management, paid-ad strategy, and visual production remain outside its authority.
- No member holds a lead role, and no member delegates to another member.
- Member descriptions stay declarative rather than call-when phrased, so all three read alike.

## Open terminology

`acquisition` is not a canonical term and carries two senses. Beacon reads an acquisition path as a
structural journey it can retrieve and an acquisition report as first-party channel measurement.
Qualify the word by path, channel, report, or cohort before Beacon acts on it.

## Compatibility boundary

Team reconciliation creates and updates declared members but does not retire an undeclared member.
Existing installations therefore keep their old `signal` agent until the owner separately preserves
any durable context and performs the guarded agent-removal workflow. The catalog must not imply that
an ordinary team update deleted it.

## Status

Every row above was read from this repository. None has been observed in a provider session, and no
gap here is proved closed by a code change alone. Record behavior in
[team validation](../guides/team-validation.md) when a case is actually run.
