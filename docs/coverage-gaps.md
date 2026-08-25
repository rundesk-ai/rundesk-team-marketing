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
| Query demand and volume | Search Console reports only queries the property already ranks for, so it cannot show an absent one | A demand source. Until one exists, demand is characterizable from published evidence by Scout and is not measurable by anyone here |
| A guarded retrieval package | [`seo`](../skills/seo/references/retrieval.md) now fixes the check set, the guardrails for a host the property does not own, and the redirect and tag-matching traps, so two audits of one site agree. It remains guidance a member may follow rather than a boundary anything enforces, and `inspect-url` still works only on a verified property | A bounded package that can only `GET` and `HEAD`, refuses private and loopback addresses, sends no credentials, and returns the check set as structured output. Guidance closes the consistency gap; only a package closes the enforcement one |

## Evidence Signal's role implies but cannot query

Signal owns the metric contract for every number this team reports, and holds two vendor report
APIs to do it with.

| Missing | Consequence |
|---|---|
| Warehouse or SQL access | Any question outside the shapes GA4 and PostHog expose cannot be asked. Custom denominators, joins across systems, and backfills have no home |
| Search Console bulk export to BigQuery | The only source that removes the API's row limits and 16-month window, and the only path to long-tail and cannibalization analysis at scale. It is not retroactive, so it must be configured before it is needed |
| Order, payment, CRM, or lead-outcome data | Certifying value means reconciling analytics to the system that accepted the money or the lead. No integration reaches one |
| An experiment platform | Assignment, sample-ratio checks, and exposure logging are method Signal owns with no tool behind them |

## Capabilities no member owns

| Missing | Consequence |
|---|---|
| Paid, email, lifecycle, social, affiliate, and marketplace acquisition methods | Beacon's routing covers organic search, landing paths, and product feeds. No member can reason about any other channel, and [`seo`](../skills/seo/SKILL.md) excludes paid search by contract |
| Brand, positioning, and pricing method | Scout can research what others published about them; no skill turns that into a position or a price |
| Landing-path build and rendered verification | [`conversion-landing-pages`](../skills/conversion-landing-pages/SKILL.md) ends in an implementation package and a rendered verification report. Beacon and Signal now share the skill and split its diagnosis and measurement halves, but no member may change or render a site, so its build half still has no owner |

## Boundaries no instruction draws

Each row was observed in the Beacon runs recorded in [team validation](team-validation.md).

| Missing | What exists today | What would close it |
|---|---|---|
| Evidence that the working-tree boundary holds | [Beacon's `Scope`](../agents/beacon/AGENTS.md) now says to return a proposed change as text and not to place the file, and its first step no longer sends it to find a repository unconditionally. Both rules were written after a run created a file in a repository it was never pointed at | Runs of `BEACON-B10` and `BEACON-R10`. Both rules are untested, and the defect that prompted them showed that available guidance is not applied guidance |
| The same first step for the other three members | Scout, Signal, and Quill each still open by reading the worked-on repository's `AGENTS.md`. For Beacon it was demoted: its stated purpose — bounding inspection, data, claims, and external effects — is already covered by Beacon's own `Scope`, and leading with it sent runs looking for a codebase. It now sits inside the step that establishes reachable evidence, so it still applies while Beacon is working in a repository. Scout is an external researcher with the same shape | An owner decision on whether the convention should change for the other members. Beacon was changed alone because Beacon is the member whose runs exposed the behavior. Signal and Quill may have a stronger claim to keeping it than Scout, since a repository can genuinely own metric definitions and publication voice |
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

`acquisition` is not a canonical term and carries two senses. Beacon reads an acquisition path as a
structural journey it can retrieve; Signal reads acquisition as a first-party channel report. The
caller's routing table sends the bare word to growth planning alone. Qualify the word or make it
canonical before either member's scope is widened.

## Status

Every row above was read from this repository. None has been observed in a provider session, and no
gap here is proved closed by a code change alone. Record behavior in
[team validation](team-validation.md) when a case is actually run.
