---
name: analyzing-growth-data
description: Use when first-party product or marketing data must answer a growth question through funnels, cohorts, retention, attribution, experiments, segmentation, forecasting, or the value a conversion turned out to be worth. It supplies metric contracts, comparable populations, causal boundaries, uncertainty, reconciliation to the system that accepted the money or the lead, and reproducible proof. Do not use for retrieving data from a specific analytics service without an analysis question, external market research, or implementing instrumentation.
---

# Analyze growth data

Turn the question and its supplied decision context into a metric contract before opening a
dashboard or writing a query. The analysis informs the requester; it does not choose for them.

## Define the question and population

Write these fields first:

```text
Question: what the data must establish
Decision context: the action the requester says this may inform
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
5. Record the exact query, saved report, export, or local script and transformation, its runtime,
   parameters, audit counts, and the extraction time.
6. Use only sources named by or required for the question. Do not inspect or reconcile an adjacent
   dataset merely because it shares a directory or date.

Disagreement between tools is a finding to explain, not a reason to choose the preferred number.

## Expose every calculation

Make each derived value independently recomputable from the return. Substitute the physical values
into every displayed equation; a generic formula followed by an unsupported result is not a trail.

- A count names its unit, population, source row or query field, and window.
- A rate shows `numerator / denominator × 100 = rate`, with the physical numerator and denominator.
- A period comparison shows both values and windows, the absolute change, and
  `(current - previous) / previous × 100 = relative change`.
- When comparing rates, also show `current rate - previous rate = percentage-point change`; never
  call that difference a percent change.
- A zero prior value makes relative change undefined. Report the absolute change and `n/a` rather
  than dividing by zero or calling the result infinite growth.
- Keep units and currency attached, calculate before rounding, and state the rounding applied.
- When auditing a displayed headline, compare it with the unrounded calculated value first, then
  show the displayed values under the stated rounding rule; do not let rounding replace the exact
  discrepancy.
- Do not calculate an interval, p-value, or significance claim from aggregates unless the sampling,
  assignment, unit of analysis, independence assumptions, and error model are established.

Name the property or project, exact command, saved report, query, export, or transformation behind
the inputs. When that identifier was not supplied, label the source trail incomplete; a local file-
inspection command is not the analytics source. A dashboard name, screenshot, or tool name alone is
not a reproducible source. Do not return an unlabeled percentage or a comparison such as “up 20%”
without both physical values and their comparable windows.

## Use the method that matches the question

| Question | Method | Required guard |
|---|---|---|
| Where do eligible observations stop? | Ordered funnel | One entry rule, step order, conversion window, and repeated-event rule |
| Does behavior persist after a shared start? | Cohort retention | Compare cohorts at the same age and account for censoring |
| Which observed touchpoints receive reporting credit? | Attribution | State model, scope, lookback window, and missing-channel bias |
| Did an intervention cause incremental change? | Randomized experiment | Assignment unit, exposure, primary metric, guardrails, and uncertainty |
| How do meaningful groups differ? | Segmentation | Predefine segments, keep overlap explicit, and report small samples |
| What range is plausible later? | Forecast | Backtest, show interval and horizon, and separate forecast from target |
| What was it actually worth? | Reconciliation to the system of record | Name which value figure, its settlement maturity, and its currency |

Read [measurement design](references/measurement-design.md) for funnel, cohort, retention,
attribution, experiment, and segment decisions. Read [forecasting and uncertainty](references/forecasting-and-uncertainty.md)
for forecasts, interval estimates, repeated looks, and model comparison. Read [value and revenue](references/value-and-revenue.md)
before releasing any figure in money or any lead-outcome rate. Read [sources](references/sources.md)
when auditing or changing this guidance.

An analytics property reports the value its instrumentation sent. It does not establish what was
earned, and a value claim is unestablished until it is reconciled to the system that accepted the
money or the lead. When data arrives as a file or export rather than from a query, or when two
sources disagree, `verifying-datasets` owns the integrity and reconciliation method that must run
before this one.

## Classify claims without deciding

Attribution distributes credit under a reporting rule. It does not estimate what would have
happened without the channel. A cohort comparison describes groups that may differ for many reasons.
A randomized experiment estimates an effect only for its assignment, exposure, population, period,
and measured outcome.

Use causal language only when the design supports it. Otherwise write that a metric changed, a
segment differs, or an association was observed.

## Return reproducible evidence

Return:

1. the question, supplied decision context, and metric contract;
2. source-trail status complete or incomplete; source, query or report, extraction time, and timezone;
3. population, exclusions, identity, window, and comparison;
4. raw inputs, units, formula, result, denominator, uncertainty, and material segments;
5. absolute, relative, and percentage-point changes where applicable;
6. data-quality checks, reconciliation notes, and claim class: descriptive, causal, or forecast;
7. limitations, unused adjacent sources, and unresolved data questions.

Do not hide an unstable result behind an aggregate, a forecast behind one accuracy score, or an
experiment behind a statistically significant secondary metric. Stop before ranking options,
recommending an action, issuing a verdict, or making the requester's decision. State what the data
establishes and lacks; do not tell the requester what they should conclude.
