---
name: analyzing-growth-data
description: Use when first-party product or marketing data must answer a growth question through funnels, cohorts, retention, attribution, experiments, segmentation, or forecasting. It supplies metric contracts, comparable populations, causal boundaries, uncertainty, and reproducible proof. Do not use for retrieving data from a specific analytics service without an analysis question, external market research, or implementing instrumentation.
---

# Analyze growth data

Turn a decision into a metric contract before opening a dashboard or writing a query.

## Define the question and population

Write these fields first:

```text
Decision: the action this analysis informs
Population: eligible people, accounts, sessions, or events
Start event: how an observation enters the analysis
Outcome: the event or state that counts as success
Window: event time, reporting timezone, cohort age, and late-arrival cutoff
Identity: anonymous, user, account, or another stable key
Exclusions: tests, bots, duplicates, reversals, consent limits, and missing data
Comparison: baseline, prior cohort, control, target, or forecast holdout
```

Name numerator and denominator separately. A rate without both is not reproducible. Keep event time,
ingestion time, reporting time, and experiment assignment time distinct.

## Check the data before interpreting it

1. Confirm the source owns the event and identity definition you need.
2. Inspect missingness, duplicates, impossible order, schema changes, late events, bots, and internal traffic.
3. Reconcile timezones, filters, attribution windows, and identity rules before comparing tools.
4. Compare a small hand-checkable sample with the aggregate query.
5. Record the exact query, saved report, export, or transformation and the extraction time.

Disagreement between tools is a finding to explain, not a reason to choose the preferred number.

## Use the method that matches the question

| Question | Method | Required guard |
|---|---|---|
| Where do eligible observations stop? | Ordered funnel | One entry rule, step order, conversion window, and repeated-event rule |
| Does behavior persist after a shared start? | Cohort retention | Compare cohorts at the same age and account for censoring |
| Which observed touchpoints receive reporting credit? | Attribution | State model, scope, lookback window, and missing-channel bias |
| Did an intervention cause incremental change? | Randomized experiment | Assignment unit, exposure, primary metric, guardrails, and uncertainty |
| How do meaningful groups differ? | Segmentation | Predefine segments, keep overlap explicit, and report small samples |
| What range is plausible later? | Forecast | Backtest, show interval and horizon, and separate forecast from target |

Read [measurement design](references/measurement-design.md) for funnel, cohort, retention,
attribution, experiment, and segment decisions. Read [forecasting and uncertainty](references/forecasting-and-uncertainty.md)
for forecasts, interval estimates, repeated looks, and model comparison. Read [sources](references/sources.md)
when auditing or changing this guidance.

## Keep descriptive and causal claims separate

Attribution distributes credit under a reporting rule. It does not estimate what would have
happened without the channel. A cohort comparison describes groups that may differ for many reasons.
A randomized experiment estimates an effect only for its assignment, exposure, population, period,
and measured outcome.

Use causal language only when the design supports it. Otherwise write that a metric changed, a
segment differs, or an association was observed.

## Return reproducible evidence

Return:

1. the decision and metric contract;
2. source, query or report, extraction time, and timezone;
3. population, exclusions, identity, window, and comparison;
4. result with counts, denominator, uncertainty, and material segments;
5. data-quality checks and reconciliation notes;
6. interpretation labeled descriptive, causal, or forecast;
7. limitations and the next decision the evidence supports.

Do not hide an unstable result behind an aggregate, a forecast behind one accuracy score, or an
experiment behind a statistically significant secondary metric.
