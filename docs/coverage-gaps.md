# Coverage gaps

What this catalog's roles imply that its shipped skills and integrations cannot yet deliver. Every
row is a limitation observed in this repository, not a roadmap commitment. Read it before granting a
member new work, promising an evidence class to a caller, or adding a package.

The boundaries these gaps are measured against are in [AGENTS.md](../AGENTS.md): growth evidence is
retrieved and re-retrievable, external research is cited to a published source, and first-party
analysis is certified with a denominator or returned as unestablished.

## Evidence Beacon's role implies but cannot retrieve

| Missing | What exists today | What would close it |
|---|---|---|
| AI-answer visibility measurement | [`seo`](../skills/seo/references/ai-search.md) documents the platform rules and the published studies; Search Console's generative-AI report exists but returns impressions only, with no clicks and no queries, and reaches a person through the UI and its export rather than any member | An API path to that report. [`google-search-console`](https://github.com/rundesk-ai/rundesk-skills-google/blob/main/skills/google-search-console/references/cli.md) still accepts only `web`, `image`, `video`, `news`, `discover`, and `googleNews` for its search type, and no generative-AI value is documented. Its `searchAppearance` dimension passes through verbatim, so a future Google-side value would arrive without a client change — but none exists to request today |
| AI referral traffic, named as such | GA4 assigns a native `AI Assistant` channel, and [`google-analytics`](https://github.com/rundesk-ai/rundesk-skills-google/blob/main/skills/google-analytics/references/cli.md) can read it through a `channel` or `source` breakdown; no skill in this catalog told a member that path exists until now, and the custom channel group covering the platforms GA4 misses is a property configuration that package refuses by contract | Either a configuration-capable analytics path, which is a broader permission than this team holds, or acceptance that the native channel plus a source breakdown is the readable floor. The measured number is a floor regardless: a large share of AI referrals arrive with no referrer and land in Direct |
| AI citation counts on Microsoft surfaces | none | A Bing Webmaster Tools package; its AI Performance report is the only source that reports citations rather than impressions |
| Which AI crawler fetched what | none | Server-log evidence, which [`measurement`](../skills/seo/references/measurement.md) calls the only ground truth for crawler behavior |
| Core Web Vitals trend | [`google-pagespeed-insights`](https://github.com/rundesk-ai/rundesk-skills-google/blob/main/skills/google-pagespeed-insights/SKILL.md) returns one 28-day field snapshot and excludes history by contract | A CrUX History source. Field data is also the portion Google plans to discontinue from PageSpeed Insights |
| Query demand and volume | Search Console reports only queries the property already ranks for, so it cannot show an absent one. [`researching-markets`](../skills/researching-markets/references/demand-signals.md) now gives Scout a method for characterizing demand from series that exist, and for saying what each cannot establish | A demand source. None of the available series measures query volume for an absent query, so this stays uncloseable by method alone — the method's contribution is an honest bound rather than a number |
| A guarded retrieval package | [`seo`](../skills/seo/references/retrieval.md) now fixes the check set, the guardrails for a host the property does not own, and the redirect and tag-matching traps, so two audits of one site agree. It remains guidance a member may follow rather than a boundary anything enforces, and `inspect-url` still works only on a verified property | A bounded package that can only `GET` and `HEAD`, refuses private and loopback addresses, sends no credentials, and returns the check set as structured output. Guidance closes the consistency gap; only a package closes the enforcement one |

## Evidence Signal's role implies but cannot query

Signal certifies first-party and supplied data. It holds two analytics report APIs, a payment API,
and — since v0.5.0 — a method for data that arrives as a file rather than from a query.

An earlier version of this table claimed Signal had no SQL access. That was wrong and is corrected
here: the PostHog package runs read-only HogQL through `query --sql`, accepting a single `SELECT` or
`WITH`, refusing write and DDL keywords, and forcing a `LIMIT`. Arbitrary SQL over PostHog's own
event and person tables is available. What is missing is a *cross-system* warehouse, which is a
narrower and more accurate claim.

| Missing | Consequence |
|---|---|
| A cross-system warehouse | Custom denominators and backfills exist inside PostHog through HogQL, but a join across PostHog, GA4, and the payment system has no home. Reconciliation across them is done by hand, one bridge at a time, and its cost scales with the number of sources |
| Search Console bulk export to BigQuery | The only source that removes the API's row limits and 16-month window, and the only path to long-tail and cannibalization analysis at scale. It is not retroactive, so it must be configured before it is needed |
| Search Console access at all | Beacon routes "a reconciled or official number" to Signal, but Signal holds GA4 and not Search Console. Asked to certify a claim Beacon retrieved from search performance data, Signal cannot open the source it rests on. Granting the read-only package would close it, and mirrors the deliberate GA4 sharing below; the owner deferred that grant in the v0.5.0 change |
| CRM or lead-outcome data | The [`stripe`](https://github.com/rundesk-ai/rundesk-skills-integrations/blob/main/skills/stripe/SKILL.md) package now reaches the system that accepted the money, so certifying purchase value is possible. Certifying a *lead* outcome still is not: whether a lead was reached, qualified, or won lives in a CRM no integration reaches, so [`value-and-revenue`](../skills/analyzing-growth-data/references/value-and-revenue.md) can only tell Signal to name the last established stage and treat the rest as unmeasured |
| An experiment platform | Assignment, sample-ratio checks, and exposure logging are method Signal owns with no tool behind them |
| Any enforcement of the file-integrity checks | [`verifying-datasets`](../skills/verifying-datasets/SKILL.md) fixes the profile and the check list so two verifications of one file agree. It remains guidance a member may follow rather than something that runs. The Beacon retrieval row above records the same distinction, and it applies identically here |

## Capabilities no member owns

| Missing | Consequence |
|---|---|
| Paid, email, lifecycle, social, affiliate, and marketplace acquisition methods | Beacon's routing covers organic search, landing paths, and product feeds. No member can reason about any other channel, and [`seo`](../skills/seo/SKILL.md) excludes paid search by contract |
| Brand, positioning, and pricing method | Scout can research what others published about them; no skill turns that into a position or a price |
| Landing-path build and rendered verification | [`conversion-landing-pages`](../skills/conversion-landing-pages/SKILL.md) ends in an implementation package and a rendered verification report. Beacon and Signal now share the skill and split its diagnosis and measurement halves, but no member may change or render a site, so its build half still has no owner |

## Boundaries no instruction draws

Each row was observed in the Beacon runs recorded in [team validation](team-validation.md), and
the working-tree row was reproduced by Scout.

| Missing | What exists today | What would close it |
|---|---|---|
| The write boundary on Scout and Quill | Beacon's two rules were run on 2026-08-25 and held. `BEACON-B10` was tested by naming a path where the file already existed, so placing it would have overwritten live content; the run returned text and the file's hash was unchanged. `BEACON-R10` was tested by supplying only a URL for a site whose source sits on the same machine; the run never went looking for it. Signal received the same write clause in v0.5.0, unrun, tested by `SIGNAL-B04`. Scout and Quill still carry the original wording, and Scout reproduced the defect twice | The clause on Scout and Quill, and a run for each. Beacon's remedy is proved forward but not against the original failure — `BEACON-B01` stays partial because the run that failed it was not re-run — and Signal's is not proved at all |
| The same first step for Scout and Quill | Scout and Quill each still open by reading the worked-on repository's `AGENTS.md`. For Beacon it was demoted: its stated purpose — bounding inspection, data, claims, and external effects — is already covered by Beacon's own `Scope`, and leading with it sent runs looking for a codebase. It now sits inside the step that establishes reachable evidence, so it still applies while Beacon is working in a repository. Signal was offered the same change in v0.5.0 and the owner kept the original wording, on the ground that a repository can genuinely own metric definitions; Signal instead gained the write boundary and a provenance clause inside step 3. Scout is an external researcher with the same shape as Beacon | An owner decision for Scout and Quill. Signal's is settled. Because Signal keeps the wording that produced the behavior in Beacon's runs, `SIGNAL-R06` exists to observe whether it produces it here |
| Evidence that guidance was applied, not merely available | The runs had the corrected AI-search reference open and one still repeated a claim that reference retires. The claim is now also listed among the things not to say, which is the scannable place rather than the explanatory one | Nothing in this repository closes this in general. It is the argument for running cases rather than grepping wording, and for re-running them after guidance changes; `SEO-W11` tests this specific instance |

## Caller-side gaps

[`managing-marketing-work`](../skills/managing-marketing-work/SKILL.md) routes by capability, which
is correct for a skill that must not assume this team's topology. Three consequences are unresolved:

- It gives the caller no step for binding a capability to an installed specialist, and no path for a
  capability that is not installed at all.
- It does not say that members are inbound-only and retain nothing between requests, so a follow-up
  must be a fresh self-contained brief.
- It states that a fluent return is not integration, but supplies no per-capability acceptance
  criteria a caller can reject a return against. Each member's `Return` section already defines one.

The Beacon and Scout boundary depends on the caller sequencing the two requests. Nothing in the
caller's skill currently names that sequence.

## Known package limitations shipped as-is

[`conversion-landing-pages`](../skills/conversion-landing-pages/SKILL.md) directs the reader to
`frontend-design`, `performance-engineering`, and `laravel-stripe-payments`. This catalog ships none
of them and no member is granted them, so that guidance dead-ends. The package is adapted content
whose provenance is pinned in [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md); repairing it
upstream keeps this catalog free of drift.

[`seo`](../skills/seo/SKILL.md) has diverged from the `rundesk-skills` package it was adapted from.
The AI-search guidance, the snippet-control checks, the skill description, and `references/validation.md`
exist only here. The divergence is deliberate and its provenance is recorded in
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md), but it is a maintenance cost: a correction made
upstream no longer reaches this copy, and the two descriptions now route differently. Anyone reading
the upstream package should not assume it is the one a member of this team received.

## Deliberate exclusions

These are settled decisions, not gaps. Do not close them without the owner's approval.

- No member operates a campaign, spends money, contacts a consumer, or publishes.
- No member approves a legal or regulated claim. A compliance gate can be identified and never
  approved around.
- No member holds a lead role, and no member delegates to another member.
- Beacon and Signal share skills on purpose. The separation is what each may release, not what each
  may read, and closing it by revoking a grant would blind Beacon to the value it must prioritize by.
- Member descriptions stay declarative rather than call-when phrased, so all four read alike.

## Open terminology

`signal` is a member name and a common noun this catalog's skills use seventy-one times — ranking
signals, demand signals, universal opt-out signals, trust signals — almost all of them in Beacon's
and Scout's packages rather than Signal's own. The owner reviewed a rename at v0.5.0 and kept the
name; [AGENTS.md](../AGENTS.md) now pins the common noun to "a suggestive input rather than a
measurement" so the two senses stay separable. Reopening the rename later costs the banner artwork
and leaves an orphaned `signal` agent on every existing install, because team reconciliation creates
declared members and never retires an undeclared one.

`acquisition` is not a canonical term and carries two senses. Beacon reads an acquisition path as a
structural journey it can retrieve; Signal reads acquisition as a first-party channel report. The
caller's routing table sends the bare word to growth planning alone. Qualify the word or make it
canonical before either member's scope is widened.

## Status

Every row above was read from this repository. None has been observed in a provider session, and no
gap here is proved closed by a code change alone. Record behavior in
[team validation](team-validation.md) when a case is actually run.
