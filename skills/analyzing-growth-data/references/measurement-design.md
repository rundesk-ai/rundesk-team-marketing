# Measurement design

## Funnels

Define eligibility before the first step. Decide whether a person may enter once, once per session,
or repeatedly; whether steps must be ordered; whether intermediate steps may be skipped; and which
event timestamp establishes the conversion window. Report eligible starts, completions, and losses
at each step. A funnel built from event counts can overstate conversion when one person repeats a
step.

## Cohorts and retention

Anchor a cohort to one explicit start event and group by that event's period. Compare cohorts at the
same age so recent cohorts are not penalized for time they have not had. Define retention as an
observable return or active state, then distinguish classic, rolling, and bounded retention rather
than mixing them.

Show the eligible cohort size beside every retained rate. Mark incomplete cells and account for
right censoring. Changes in acquisition mix, onboarding, pricing, or product access can explain a
cohort difference without retention behavior causing it.

## Attribution

Record the touchpoint population, channel taxonomy, first-user, session, or event scope, lookback
window, attribution model, direct-traffic handling, cross-device limitations, consent loss, and
offline gaps. Reconcile identifiers and windows before comparing analytics and advertising tools.

Use attribution for descriptive reporting. Estimate incrementality with a randomized holdout,
geo-experiment, or another defensible counterfactual design.

## Experiments

Predefine the hypothesis, assignment unit, eligibility, exposure, primary outcome, guardrail metrics,
minimum detectable effect, analysis window, and stopping rule. Analyze by assigned group unless a
documented design requires otherwise. Check sample-ratio mismatch, assignment collisions, novelty,
interference, missing outcomes, and instrumentation changes.

Report effect size and interval, not only a thresholded p-value. Secondary and segmented results are
exploratory unless their multiplicity was planned.

## Segments

Choose segments because the decision can act differently on them, not because a dashboard offers
many dimensions. Define membership before viewing the result, preserve overlapping membership when
the concepts overlap, and report each segment's eligible count. Avoid a segment whose definition
uses information observed after the outcome.
