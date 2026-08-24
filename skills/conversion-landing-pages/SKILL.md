---
name: conversion-landing-pages
description: Use when planning, writing, designing, building, reviewing, or optimizing a conversion landing page that sells a product or captures a lead, quote, consultation, demo, application, booking, or call; or when improving landing-page CVR, CTR, CTA clicks, form or purchase completion, mobile performance, campaign message match, analytics, or A/B tests. It supplies an evidence-backed workflow for page setup, layout, copy, offers, forms, trust, responsive UX, measurable outcomes, and trustworthy experiments. Do not use it for a full storefront or checkout, general product UI, SEO-only content, ad creative alone, or legal approval of lead consent.
---

# Conversion landing pages

Optimize the page and its acquisition path as one system. Maximize qualified value, not clicks or
transactions in isolation. A higher raw conversion rate can be a loss when it produces misdirected,
unreachable, noncompliant, or low-value leads, refunded purchases, or unprofitable orders.

## Establish the conversion contract

Before drawing a section or writing a headline:

1. Identify the traffic source, campaign, query or promise, audience, awareness level, device mix,
   geography, and returning-versus-new split. Do not design one generic page for materially
   different intents.
2. Define the offer in the visitor's terms: outcome, audience, eligibility, cost or commitment,
   differentiator, evidence, risk, and what happens after the action.
3. Choose one primary conversion for the page: accepted order, call, form, booking, quote start, or
   another durable outcome. Give secondary actions lower emphasis and a reason to exist.
4. Define the downstream success event and owner: paid and retained order, margin, accepted or
   qualified lead, reached lead, appointment, sale, or value. Record rejection, disqualification,
   cancellation, refund, and fraud reasons that can reverse apparent success.
5. List the claims, logos, ratings, testimonials, certifications, pricing, availability, and
   guarantees that can actually be substantiated. Remove invented proof and unsupported urgency.
6. Record the legal, privacy, consent, accessibility, brand, analytics, and performance constraints.
   Use `lead-compliance-gates` for U.S. lead transfer and contact consent; this skill does not approve
   disclosures or create permission to call or text.

Keep the metric names distinct:

```text
ad CTR       = ad clicks / ad impressions
page CTA rate = unique primary-action activators / eligible landing sessions
page CVR      = accepted primary conversions / eligible landing sessions
qualified CVR = qualified leads / eligible landing sessions
purchase CVR  = accepted purchases / eligible landing sessions
value/session = net attributable value / eligible landing sessions
```

The landing page does not directly own ad CTR. Improve CTR through the ad and targeting, then keep
the page promise consistent with them. A clickbait promise can raise CTR while lowering page CVR,
lead quality, purchase value, and trust.

## Build a message map before a layout

Use campaign/search terms, customer interviews, sales-call objections, support questions, CRM loss
reasons, and usability observations. Do not replace audience evidence with demographic stereotypes.

For each materially different intent, write:

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

As a starting hypothesis, make the page's identity, relevance, offer, and next step recognizable
early. Let intent, risk, content, accessibility, and the real viewport determine how much belongs in
the first view. Do not cram in every argument or force a complete form above the fold when the
visitor needs context to decide.

Treat the rest of the page as an ordered answer to visitor questions, not a mandatory stack of
marketing sections. A useful default sequence is outcome and proof, how it works, eligibility or
fit, objections and risk, then the same primary action. Reorder, combine, or omit sections from
evidence. Repeating the same action after relevant answers is coherent; introducing unrelated
actions is not.

Read [page-architecture-and-conversion-flows.md](references/page-architecture-and-conversion-flows.md)
when creating the message map, section order, value proposition, offer, proof, CTA copy, product
purchase path, lead form, or confirmation state.

## Make one action easy to understand

Use one visually dominant action in each decision region and label its truthful next step, such as
`See my quote options` or `Book a 20-minute demo`, not `Submit` or a result the next screen cannot
deliver. Keep its meaning consistent through activation, pending, acceptance, and confirmation.
Retain necessary trust, legal, contact, and recovery paths without making unrelated exits compete.

## Design the shortest truthful conversion flow

For a product page, preserve the advertised product, variant, price, terms, availability, and actual
purchase path. For a lead page, justify every field by the current fulfillment, qualification,
routing, contact, or compliance decision it serves. In both cases, make loading, errors, duplicate
protection, backend acceptance, and confirmation part of the flow rather than treating a click or
thank-you URL as conversion truth.

Use `laravel-stripe-payments` for Stripe payments and lifecycle handling. Use
`lead-compliance-gates` for regulated lead consent, transfer, contact, suppression, and evidence.
The page skill may measure those boundaries but does not redefine them.

## Build the mobile page as the primary task, not a smaller desktop page

Preserve the promise, proof, action, disclosures, recovery, and accepted outcome across sizes. Build
the narrow flow first, then recompose from content pressure. Treat accessibility, field performance,
third-party cost, keyboard coverage, and error recovery as conversion behavior, not polish.

Read [mobile-performance-and-accessibility.md](references/mobile-performance-and-accessibility.md)
when implementing responsive layout, sticky actions, mobile forms, media, analytics tags, Core Web
Vitals, or accessibility proof. Use `frontend-design` alongside this skill for complete interaction
states and rendered UI verification. Use `performance-engineering` for performance investigation,
budgeting, optimization, or proof. Use `seo` when organic visibility, crawling/indexing, metadata,
structured data, or field Core Web Vitals as a search concern are also in scope.

## Instrument the whole conversion outcome

Write the event, identity, denominator, attribution, deduplication, and reconciliation contract
before launch. Separate page diagnostics from backend-accepted conversion, downstream quality or
value, and harm guardrails. Keep ordinary analytics free of PII and payment data, and make the owning
application, commerce, payment, booking, call, or CRM state authoritative.

Read [measurement-and-experimentation.md](references/measurement-and-experimentation.md) when
defining CTR/CVR, events, attribution, commerce or CRM feedback, experiment metrics, measurable
results, sample size, stopping rules, or a low-traffic optimization plan.

## Improve through evidence, then experiments

Fix known message, function, accessibility, performance, and measurement defects before testing
persuasion. Then test one causal hypothesis with stable assignment, a prespecified primary outcome,
quality/value result, harm guardrails, sample and stopping method, and equivalent end-to-end paths.
Validate sample ratio and telemetry before interpreting lift. Report absolute results and uncertainty,
not a winner label alone. If traffic cannot power a useful decision, use qualitative diagnosis and
an annotated baseline without claiming randomized causality.

## Produce an implementation-ready package

For a build or redesign, deliver:

1. a conversion brief with traffic segments, offer, primary and downstream outcomes, baseline,
   constraints, and unresolved evidence;
2. a message map and claim/proof ledger;
3. a section and responsive layout specification naming the purpose, content, action, and mobile
   behavior of each region;
4. a conversion-flow specification covering fields or product/variant selection, loading, errors,
   duplicate protection, acceptance, and confirmation;
5. an analytics contract with event owners, numerators, denominators, deduplication, attribution,
   quality/value feedback, and reconciliation proof;
6. an A/B test brief with hypothesis, primary metric, guardrails, baseline, minimum detectable
   effect, power/sample plan, duration, stopping method, and result-report template; and
7. a rendered verification report for mobile, desktop, accessibility, performance, source-to-page
   message match, and end-to-end conversion truth.

If the baseline, traffic volume, proof, product terms, qualified outcome, or legal-approved content
is missing, mark it explicitly. Do not invent a target lift, claim, review, price, or consent copy to
make the package appear complete.

## Reject common conversion folklore

| Folklore | Better decision |
|---|---|
| Put every CTA, form, or buy control above the fold | Make the offer and next action clear early; place the conversion control where the visitor has enough confidence to complete it. |
| Remove every navigation link | Remove irrelevant exits; retain necessary trust, contact, legal, accessibility, and recovery paths. |
| Fewer fields always convert better | Ask only what is needed now, but keep fields that materially qualify, fulfill, route, or make consent valid. Measure qualified value. |
| Multi-step forms always win | Use steps for real cognitive or conditional structure, then test the complete flow and downstream quality. |
| Social proof always increases trust | Use current, attributable, representative evidence with required disclosures; fake or context-free proof destroys trust and can be unlawful. |
| A universal CVR benchmark defines quality | Compare like-for-like intent, industry, channel, device, offer, and conversion value; use your own baseline and downstream outcomes. |
| A statistically significant CTA click is a win | Require trustworthy assignment and data plus no unacceptable regression in accepted outcomes, quality, net value, refunds, speed, errors, or complaints. |

## Prove the delivered page

Before calling the page ready:

1. Compare the rendered first viewport with every acquisition promise and intended segment.
2. Complete the flow on representative mobile and desktop browsers using touch, keyboard, zoom,
   autofill, slow network, long content, validation errors, duplicate activation, and back/restore.
3. Verify semantic headings, labels, focus order, visible focus, contrast, reflow, touch targets,
   error announcements, reduced motion, and a representative screen-reader path.
4. Measure field Core Web Vitals and inspect layout shifts and third-party main-thread/network cost.
5. Trace each event from browser to analytics to the owning order, payment, booking, call, or CRM
   system; prove deduplication, attribution, accepted-versus-rejected status, and absence of
   prohibited PII or payment data.
6. Verify all claims, proof, pricing, availability, privacy, consent, and next-step statements against
   their owners and effective versions.
7. Record the page/campaign version, test conditions, known limits, baseline metrics, and next
   hypothesis. Do not report a generic `conversion optimized` verdict without this evidence.

The research and good/bad lesson mapping for this package are in
[sources.md](references/sources.md).
