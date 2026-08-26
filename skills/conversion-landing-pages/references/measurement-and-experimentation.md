# Measurement and experimentation

Read this reference when defining landing-page CTR or CVR, analytics events, attribution, commerce
or CRM feedback, experiment metrics, sample size, stopping rules, or optimization under low traffic.

## Choose the outcome hierarchy before instrumentation

Separate the acquisition, page, accepted-conversion, quality, and business layers:

| Layer | Examples | Use |
|---|---|---|
| acquisition | impressions, ad clicks, ad CTR, spend | targeting and creative relevance |
| landing behavior | eligible views, CTA activations, form starts, errors | diagnose task friction |
| accepted conversion | stored lead, connected call, confirmed booking, accepted order | page CVR source of truth |
| outcome quality | qualified/disqualified lead, duplicate, paid order, refund, cancellation, fraud | prevent proxy optimization |
| business outcome | appointment, retained order, converted lead, net value, margin | choose winners and bidding signals |
| guardrail | speed, accessibility, error, abandonment, privacy or compliance incident | prevent harmful lift |

Pick one primary decision metric and a small set of guardrails. CTA rate and form-start rate are
diagnostics unless the click itself is the business outcome. Optimize the earliest reliable signal
that predicts value, then continue monitoring the later outcome.

Define every ratio with a named numerator, denominator, unit, time window, identity/deduplication
rule, eligibility rule, and late-arrival policy. `CVR` without those fields is not comparable across
tools or teams.

## Write a durable event contract

A provider-neutral contract should share a common acquisition spine, then branch by conversion type:

```text
landing_eligible
primary_action_activated

# Lead or booking branch
lead_form_started
lead_step_completed
lead_validation_failed
lead_submit_attempted
lead_accepted
lead_duplicate
lead_rejected
lead_qualified
lead_disqualified
lead_contacted
lead_converted

# Product purchase branch
offer_selected
cart_or_purchase_started
checkout_started
order_accepted
payment_confirmed
order_cancelled
order_refunded
order_disputed
```

For each event define trigger, owner, event ID, business operation ID, page/campaign/variant version,
allowed non-PII properties, retry and deduplication behavior, and source of truth. Record reason codes
for validation, rejection, duplication, and disqualification without sending entered values to
ordinary analytics.

Instrument a form or purchase start from meaningful entry, not focus caused by page autofocus.
Instrument an accepted lead from the backend after durable acceptance and an accepted purchase from
the owning order/payment transition, not from a click handler or thank-you page. Send the same
durable business identifier through approved systems so analytics, commerce, payment, and CRM counts
can be reconciled without exposing raw PII or payment data.

If using a provider's recommended schema, map rather than replace domain meaning. For example, GA4
defines lead lifecycle events and ecommerce events such as product view, add-to-cart, checkout,
purchase, and refund. Your backend lifecycle still owns when those states occur.

## Define the measurement handoff

Keep the plan provider and database neutral. Name the existing analytics, commerce, CRM, tenancy,
and persistence contracts the implementation must preserve, then hand the contract to the owning
analytics and development specialists.

The handoff defines:

- the grain before any event, session, lead, or order joins;
- authorized account or tenant scope;
- event time, reporting timezone, attribution window, late-arrival cutoff, and exposure window;
- durable event and business-operation identifiers for deduplication;
- permitted properties and the personal, payment, or consent data excluded from general analytics;
- the authoritative state for accepted, rejected, qualified, refunded, or disputed outcomes; and
- the source totals and segment sums the implementation must reconcile against.

Do not prescribe tables, queries, indexes, framework calls, or provider configuration. Require the
implementation owner to return the executed reconciliation and representative performance evidence.

## Preserve attribution without pretending it is causal

Keep approved campaign and click identifiers through the flow, including redirects and multi-step
forms. Document first-user, session, and event-scoped dimensions and the reporting attribution
model; the same conversion can receive different credit under different scopes or models.

Reconcile the applicable path:

```text
ad clicks -> eligible landing sessions -> accepted leads -> qualified leads -> converted leads
ad clicks -> eligible landing sessions -> accepted orders -> paid/retained orders -> net value
```

Investigate gaps instead of silently dividing mismatched counts. Clicks can exceed landings because
the page never loads, consent or blockers suppress telemetry, redirects lose parameters, bots or
invalid traffic differ, sessions split, or tools use different time zones and attribution windows.

Return qualified, converted, purchase, refund, and value outcomes to acquisition platforms only
through an approved privacy and data-sharing design. Hashing a contact value does not by itself make
every use lawful or remove the need for consent, notice, minimization, retention, and vendor controls.

## Diagnose before experimenting

Use segmented funnels, field-performance data, session evidence, support and sales calls, CRM loss
reasons, and representative usability tests to identify a plausible cause. Fix correctness,
accessibility, mobile, performance, routing, and tracking defects directly; do not randomize users
into a known broken experience merely to prove the bug matters.

Turn an observation into a causal hypothesis:

```text
Observation: mobile visitors start the form but abandon at the phone field.
Evidence: keyboard mismatch and format errors dominate that step.
Hypothesis: a truthful telephone input, autocomplete, tolerant parsing, and nearby format guidance
will reduce valid-user errors and increase accepted leads without reducing qualification.
```

Avoid hypotheses that restate the treatment: `Changing the button to green will increase clicks`
does not explain a user problem or mechanism.

## Pre-register the decision

Before exposure, record:

- target population, eligibility, randomization unit, persistent assignment, allocation, and traffic
  exclusions;
- control and treatment versions and the one coherent experience difference being tested;
- primary metric, quality/value outcome, guardrails, diagnostic metrics, and harm limits;
- baseline, minimum detectable effect worth shipping, significance/error policy, power, required
  sample, and planned duration;
- seasonality or business cycles the duration must cover;
- fixed-horizon or valid sequential analysis and its stopping rule;
- handling of duplicates, late conversions, missing telemetry, bots, outliers, and multiple metrics;
  and
- rollout, rollback, and follow-up decision rules.

Choose the sample from the baseline, meaningful minimum effect, variance, power, and error rate—not a
generic “100 conversions” rule. If the required sample or downstream delay is impractical, test a
larger coherent change or use qualitative evidence; do not lower the bar after seeing the result.

## Protect experiment integrity

QA both variants end to end before and during exposure. Verify stable assignment, no cross-variant
cache or URL leakage, equivalent routing, forms, consent, performance and CRM handling, and exact
event versions.

Check sample-ratio mismatch before interpreting any outcome. An unexpected allocation can indicate
assignment, telemetry, filtering, or execution defects; finding significance elsewhere does not
cure it. Monitor telemetry loss and join rates by variant.

For a fixed-horizon test, do not stop because an ordinary p-value temporarily crosses a threshold.
Repeated peeking inflates false positives. Use a planned sequential method if continuous decisions
are required. Harm guardrails are different: stop or roll back immediately when users, compliance,
security, data, or operations are at unacceptable risk.

Do not change copy, routing, targeting, or tracking in one variant during the test unless the test is
invalidated and restarted. Record concurrent campaigns and product changes that could interact.

## Read the result at the right level

Report:

- absolute control and treatment rates and counts;
- effect size and uncertainty interval, not only relative lift and a threshold label;
- exposure dates, traffic allocation, segment, randomization unit, and exclusions;
- sample-ratio and telemetry-quality results;
- accepted, qualified, purchased, refunded, retained, converted, or value outcomes plus guardrails;
- device and campaign results only for prespecified or adequately powered segments; and
- limitations, late outcomes, novelty or learning effects, and next decision.

A positive CTA effect with flat accepted conversions is not a win. Higher raw lead CVR with lower
qualification, or higher purchase CVR with worse margin, refunds, disputes, or retention, may be a
loss. Slower performance, more complaints, or inaccessible completion can invalidate either result.

Treat an unplanned segment win as exploratory. Running many variants, metrics, and segments increases
the chance of a lucky result; apply the prespecified multiple-testing policy or confirm the finding
in a new experiment.

## Optimize responsibly under low traffic

When traffic cannot support the desired minimum effect in a useful time:

1. repair proven functional, mobile, accessibility, performance, and measurement defects;
2. run task-based usability sessions with representative visitors;
3. analyze search terms, calls, support questions, CRM rejection and loss reasons;
4. test message comprehension and offer fit before visual polish;
5. combine related fixes into a coherent treatment with a plausible larger effect; and
6. monitor an annotated before/after series while naming seasonality and campaign changes.

Do not call a before/after movement causal without randomised control. The honest result may be that
there is insufficient evidence to choose a winner.
