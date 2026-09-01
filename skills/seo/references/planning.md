# Search-growth planning

Read this when choosing what organic or AI-search work to do, sequencing an approved program, or
turning established evidence into an implementation brief. The domain owner applies this method and
retains the decision; the evidence specialist remains independent.

## Establish planning inputs

Start with:

- the decision and business outcome being served;
- the property, audience, approved direction, scope, and authority;
- traceable site, search, analytics, and business-outcome evidence;
- cited market, customer, or competitor-strategy evidence when it affects the ranking;
- the current approved phase, active experiments, dependencies, constraints, and known risks; and
- the baseline, guardrails, observation window, and evidence latency.

Do not retrieve missing specialist evidence while ranking. Ask the first-party and supplied-data
evidence specialist for property, analytics, and supplied-file evidence, and the external-research
specialist for published claims. Continue with unaffected options and mark every dependent
conclusion provisional.

## Operate four gates in order

Do not call a vendor audit number, Lighthouse score, ranking estimate, or invented weighted total a
"quality score." For organic search, use an **SEO quality scorecard**: a dated set of named measures,
statuses, denominators, sources, and red flags. Keep its parts separate so an aggregate cannot hide a
missing outcome metric or a critical technical failure.

### 1. Measurement readiness and baseline

Establish the current state before proposing growth:

- **Search visibility:** Search Console impressions, clicks, CTR, and average position, segmented by
  query, landing page, device, country, and comparable date window where the population supports it.
- **Onsite outcomes:** organic sessions by landing page, the defined key events, generated leads,
  purchases or sales, and recognized value where the authoritative systems establish them.
- **Traffic quality:** total leads and each available disposition, including working, qualified,
  disqualified, converted, and unconverted; keep loss or disqualification reasons when the source
  records them. Report qualified-lead rate, lead-to-sale rate, disposition completeness, and value
  only with physical numerators, denominators, windows, and the attribution rule.
- **Reconciliation:** compare Search Console clicks with analytics organic sessions as trends, not as
  equal counts. Record canonical handling, consent, time-zone, attribution, tag coverage, and other
  known reasons the sources differ.

Label every required measure `available`, `missing`, `unreconciled`, or `not applicable`, with its
source and definition. If impressions, clicks, organic landing behavior, the named lead or purchase
event, or required disposition outcomes are missing or cannot be joined back to organic acquisition,
the first planned outcome is to repair that measurement path and verify it with a synthetic event or
reconciled sample. Do not infer traffic quality from clicks, engagement, or form submissions alone.

Preserve the pre-change values and population as the baseline. Never backfill an unavailable metric
with zero, estimate a disposition that the CRM did not record, or delay the baseline until after a
change ships.

### 2. Technical quality and red-flag resolution

Build the technical section of the scorecard from observable checks, not a single score:

- Search Console manual actions, security issues, Page indexing, Crawl stats, sitemaps, URL
  Inspection, canonical selection, and material performance anomalies;
- live status, redirect chain, `robots.txt`, robots directives, rendered content, crawlable links,
  canonical and hreflang behavior, structured-data validity, and server-log failures where available;
- page-level insights from Search Console plus field Core Web Vitals from CrUX. PageSpeed Insights or
  Lighthouse lab results diagnose a page and guard regressions; they do not replace field data; and
- conversion-path failures, broken forms or checkout, missing tags, duplicate events, irreconcilable
  attribution, and disposition leakage that makes traffic quality unknowable.

Search Console recommendations may surface indexing, crawling, serving, sitemap, structured-data,
or trending-query opportunities. Record them as dated inputs, not commands: Google describes the
feature as experimental and says recommendations can expire or change. Verify the underlying report,
business-outcome path, dependency, and red-flag state before promoting one into the plan.

Keep a red-flag register with location or affected population, evidence, severity, owner, required
fix, verification, and state. Security issues, manual actions, an unavailable site, broad accidental
blocking or `noindex`, broken conversion paths, and material tracking loss interrupt the normal
order for containment. All other missing measurement is resolved in phase 1, then unresolved
technical red flags are resolved here before growth work. A new red flag found in any later phase
returns the program to this gate.

### 3. Growth plan

Only after the baseline is usable and blocking red flags are resolved, rank improvements to existing
coverage: canonical consolidation, snippets and titles, internal links, structured-data eligibility,
field performance, conversion-path improvements, and other evidence-supported opportunities. Each
option needs a search-to-business outcome path, a release check, a guardrail, and a readout window.

### 4. Content expansion

Expand coverage only after the first three gates. Require distinct user intent, cited demand or
customer evidence, a canonical target, an internal-link path, indexation proof, useful original
value, an owner, and a measurable path to qualified outcomes or sales. Do not create pages merely to
fill keyword variants, satisfy a volume estimate, or increase page count. Check cannibalization and
scaled-content-abuse risk before approval.

The fixed order is a catalog operating method, not a claim that a search engine publishes one
universal SEO process. It follows the dependency in the documented evidence: Search Console covers
pre-arrival search behavior, analytics and lead outcomes cover what traffic did after arrival, and
technical eligibility precedes serving and growth. Do not advance a phase merely because its report
exists; require its observable gate to pass.

## Separate work within the gates

Use three groups:

1. **Foundational defects:** missing or unreliable measurement, crawl, index, canonical, rendering,
   usability, conversion, or disposition defects that materially block later outcomes.
2. **Evidence-supported enhancements:** structured data, content, internal links, performance,
   answer modules, or AI-search improvements with an established serving role and measurement path.
3. **Coverage expansion:** new commercial or educational coverage with distinct intent, an internal
   link path, indexation proof, and a search-to-business outcome path.

Do not rank a dependent enhancement or expansion ahead of the foundational defect that prevents its
outcome. Recurring maintenance continues after the foundation is verified; it does not compete with
the three outcome slots as a growth outcome by itself.

Do not split one change into separate planning, implementation, verification, and readout outcomes.
Those are one outcome's completion and measurement contract. If the evidence supports fewer outcomes
than the requested count, return the supported set and name the unused capacity or evidence blocker;
do not promote maintenance, reporting, or an unsupported idea merely to fill a slot.

## Rank without false precision

For each viable option, show:

- expected impact and the outcome path that supports it;
- confidence, tied to verified, documented, correlational, or unestablished evidence;
- effort and the actual implementation owners involved;
- material risks and guardrails;
- dependencies and approval boundaries;
- time to release, time to observable evidence, and source latency; and
- the smallest test or change that can resolve the important uncertainty.

Use relative tiers or an explained ordering. Do not multiply invented numeric scores into a precise
total. Preserve ties when the evidence cannot distinguish two options. A tool score, traffic
estimate, keyword volume, citation count, or competitor feature is not business impact without a
traceable path to the named outcome.

## Return a decision-ready recommendation

Return:

```text
Decision served: <owner choice this ranking informs>
Evidence: <supplied sources, dates, definitions, and material limits>
Ranked options: <impact, confidence, effort, risk, dependencies, and time to evidence>
Recommendation: <top option, why it leads, alternatives, and what could change the order>
Decision state: Pending owner decision
Test: <smallest useful change or evidence collection>
Measurement: <baseline, primary and downstream outcomes, guardrails, window, latency, readout date>
Authority: <approved preparation and separately controlled implementation or activation>
Unknowns: <missing evidence or decisions and which conclusions depend on them>
```

Only after the owner selects an option, turn it into an implementation brief with acceptance checks,
release verification, stop conditions, observation timing, and the named artifact owners. The plan
does not authorize code changes, publication, deployment, account configuration, tracking changes,
experiments, spend, or contact.

## Preserve independent verification

An implementation reviewer judges the finished artifact type and must not be its producer. After an
authorized release, the evidence specialist — not the domain owner and not the implementer —
independently verifies the affected production surface, measurement behavior, and source trail. The
domain owner compares that observed return with the approved measurement contract and recommends
keep, iterate, stop, or gather more evidence; the named owner makes the resulting decision.
