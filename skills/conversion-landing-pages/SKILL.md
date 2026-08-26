---
name: conversion-landing-pages
description: Use when planning or reviewing a campaign destination or focused conversion path—such as a landing page, lead form, quote path, demo request, booking path, or focused purchase page—to determine what appears to work, what appears not to work, and what should be tested next. It supplies an evidence-backed conversion brief, prioritized findings, page measurement contract, and experiment plan. It stops at the planning and review handoff; final copy, visual design, page builds, analytics implementation, campaign operation, and legal approval remain with their owners.
---

# Plan conversion landing pages

Treat the page and its acquisition promise as one decision surface. Optimize qualified value rather
than clicks, form submissions, or purchases in isolation. A higher raw conversion rate can still be
a loss when it produces misdirected, unreachable, noncompliant, refunded, or low-value outcomes.

## Establish the decision

Before recommending a page change, record:

- the traffic source, arrival promise, audience, intent, device mix, geography, and relevant split;
- the offer, eligibility, cost or commitment, differentiator, proof, risk, and next step;
- one primary page conversion and the downstream outcome that makes it valuable;
- the baseline, numerator, denominator, attribution rule, quality or value outcome, and guardrails;
- claims, testimonials, ratings, prices, availability, guarantees, and urgency that can be proved; and
- legal, privacy, consent, accessibility, brand, analytics, and performance constraints.

Use `lead-compliance-gates` for U.S. lead-transfer and contact-consent gates. This skill identifies
where approval is needed but does not write or approve consent language.

Map the complete funnel before calling any rate good, bad, or page-caused. Keep metric names distinct:

```text
ad CTR              = ad clicks / ad impressions
landing arrival rate = eligible landing sessions / ad clicks
page CTA rate        = unique primary-action activators / eligible landing sessions
accepted page CVR    = accepted primary conversions / eligible landing sessions
qualified page CVR   = qualified leads / eligible landing sessions
closed page CVR      = closed jobs or retained orders / eligible landing sessions
value per session    = net attributable value / eligible landing sessions
```

The page does not own ad CTR: CTR describes how ad impressions became clicks. A provider's reported
conversion rate may instead divide attributed conversions by eligible ad interactions, while an
analytics property may report the share of sessions or users with a configured key event. Do not
compare or multiply rates until their population, action, scope, window, and deduplication align.

CTA rate is a local diagnostic, not page CVR, unless activating the CTA is itself the accepted
outcome. CTR and page CVR can move in opposite directions when targeting, promise, intent, or traffic
mix changes. Evaluate message match between the acquisition promise and the page, reconcile clicks
to eligible landings, then judge the page against accepted and downstream outcomes. Read
[measurement and experimentation](references/measurement-and-experimentation.md) whenever a request
uses `CTR`, `CVR`, `conversion`, `key event`, or an unlabeled rate.

## Diagnose before proposing

Separate observations from explanations and recommendations:

```text
Observation: what the page, funnel, research, or data shows
Evidence: source, population, period, denominator, and material limitation
Interpretation: the user problem or mechanism the evidence suggests
Confidence: established, likely, plausible, or unknown
Recommendation: the smallest change or test that could improve the outcome
Proof: what result would support or reject the interpretation
```

Use campaign and search terms, customer interviews, usability observations, sales objections,
support questions, CRM loss reasons, funnel data, field performance, and accepted outcomes. Do not
replace evidence with demographic stereotypes, universal benchmarks, or landing-page folklore.

Distinguish `observed absent` from `not supplied`. A screenshot, page description, or analytics
summary proves only the state it actually covers; missing evidence is an unknown until the relevant
rendered page, flow, or source is inspected.

Identify known defects separately from hypotheses. Broken message match, inaccessible controls,
failed validation, slow field performance, or incorrect measurement should be corrected and verified;
they do not need an experiment to prove that the page is broken. Persuasion choices with credible
alternatives belong in an experiment plan.

Treat message match as broken when a material acquisition promise is absent, contradicted, or
silently changed at arrival—for example product, audience, price, eligibility, timing, obligation,
or next step. Alternative truthful framing of the same complete offer is a persuasion hypothesis,
not a known defect.

## Plan the page around visitor decisions

For each materially different intent, create a message map:

```text
Visitor wants:
Arrival promise:
Specific outcome:
Why believe it:
Main objection or risk:
Eligibility or limitation:
Primary action:
What happens next:
```

Plan section order as answers to the visitor's questions, not a required stack of marketing
components. A useful starting hypothesis is outcome and proof, how it works, eligibility or fit,
objections and risk, then the same primary action. Reorder, combine, or omit sections from evidence.

Read [page architecture and conversion flows](references/page-architecture-and-conversion-flows.md)
when planning message hierarchy, proof, CTA meaning, form or purchase flow, and confirmation states.
Read [experience evaluation](references/experience-evaluation.md) when reviewing mobile behavior,
accessibility, field performance, third parties, or recovery as planning constraints.

## Plan measurement and experiments

Define the event, identity, denominator, attribution, deduplication, reconciliation, and downstream
feedback needed to judge the plan. Keep the owning application, commerce, payment, booking, call, or
CRM state authoritative for accepted outcomes.

Read [measurement and experimentation](references/measurement-and-experimentation.md) when defining
events, baselines, experiment metrics, sample and stopping rules, or a low-traffic learning plan.

Recommend an experiment only when it can decide between credible alternatives. State the causal
hypothesis, target population, assignment, primary metric, quality or value outcome, guardrails,
minimum useful effect, sample and duration method, stopping rule, and interpretation limits. When
traffic cannot support a useful test, recommend qualitative diagnosis and an annotated baseline
without claiming randomized causality.

## Rank the plan

Return findings in this order:

1. **Known failures** that prevent the intended experience or invalidate measurement.
2. **High-confidence mismatches** supported by more than one relevant evidence surface.
3. **Testable hypotheses** with a named mechanism and decision rule.
4. **Unknowns** whose missing evidence could change the plan.

Rank each item by expected downstream value, confidence, effort range, risk, dependency, and the
time needed to learn. Do not fabricate a lift estimate or use a generic benchmark as one.

## Produce the planning package

Deliver the smallest package that makes the decision and handoffs unambiguous. Combine sections when
one table can satisfy them, link repeated findings by identifier, and do not restate the same message
mismatch or metric warning in every artifact.

For a bounded question, return only the decision, evidence and limits, metric ledger when relevant,
and ranked next steps. Expand to the full package only when the requested outcome needs every handoff.

Deliver:

1. a conversion brief with audience, arrival promise, offer, primary and downstream outcomes,
   baseline, constraints, and unresolved evidence;
2. a table of what appears to work, what appears not to work, supporting evidence, confidence, and
   the decision each finding supports;
3. an above-the-fold review covering arrival-promise match, audience and outcome clarity, proof,
   primary action, material terms, competing elements, and experience risks;
4. a message map and claim/proof ledger;
5. a page and flow plan describing each region's purpose, content requirement, action, mobile
   constraint, and required state without prescribing implementation;
6. a measurement contract naming events, owners, numerators, denominators, deduplication,
   attribution, downstream feedback, and reconciliation proof;
7. a prioritized correction and experiment backlog; and
8. an implementation handoff naming required content, design, development, analytics, compliance,
   and verification owners.

Do not write final copy, produce visual design, edit source, implement events, configure analytics,
launch an experiment, or certify the rendered page. The receiving specialists own those artifacts
and must return their own implementation and verification evidence.

## Reject common folklore

| Folklore | Planning decision |
|---|---|
| Put every CTA or form above the fold | Make the offer and next action recognizable early; place completion where the visitor has enough confidence to act. |
| Remove every navigation link | Remove irrelevant exits; retain necessary trust, contact, legal, accessibility, and recovery paths. |
| Fewer fields always convert better | Ask only what is needed now, while preserving fields that materially qualify, fulfill, route, or make consent valid. Measure qualified value. |
| Multi-step forms always win | Use steps only for real cognitive or conditional structure, then evaluate the complete flow and downstream quality. |
| Social proof always increases trust | Require current, attributable, representative evidence with the necessary disclosures. |
| A universal CVR benchmark defines quality | Compare like-for-like intent, channel, device, offer, and value; prefer the page's own baseline. |
| A statistically significant CTA click is a win | Require trustworthy assignment and no unacceptable regression in accepted outcomes, value, errors, speed, accessibility, refunds, or complaints. |

The evidence and lesson mapping for this package are in [sources](references/sources.md).
