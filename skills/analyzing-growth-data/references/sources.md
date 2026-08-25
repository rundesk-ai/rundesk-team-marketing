# Source basis

Verified in August 2026. These sources establish the measurement and forecasting boundaries; the
portable workflow in this package is a Rundesk synthesis.

## Product analytics and experiments

- [PostHog funnels](https://posthog.com/docs/product-analytics/funnels) documents ordered and
  unordered funnels, conversion windows, exclusions, and breakdowns.
- [PostHog retention](https://posthog.com/docs/product-analytics/retention) documents cohort start
  and return events, retention periods, and retention calculation choices.
- [Google Analytics attribution](https://support.google.com/analytics/answer/10597962) documents
  reporting attribution models and lookback settings. It establishes reporting credit rules, not
  causal incrementality.
- [Google Analytics traffic-source scopes](https://support.google.com/analytics/answer/11080067)
  distinguishes first-user, session, and event-scoped acquisition dimensions.
- [Microsoft's experimentation platform paper](https://exp-platform.com/Documents/2015%20Online%20Controlled%20Experiments_EncyclopediaOfMLDM.pdf)
  covers randomization, assignment units, guardrails, sample-ratio mismatch, and practical threats
  to online controlled experiments.
- [American Statistical Association statement on p-values](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)
  establishes that a p-value alone does not measure effect size, practical importance, or the
  probability that a hypothesis is true.

## Cohorts, survival, and forecasts

- [NIST Engineering Statistics Handbook: survival analysis](https://www.itl.nist.gov/div898/handbook/apr/section1/apr15.htm)
  establishes censoring and time-to-event analysis concepts that motivate marking incomplete
  retention observations rather than treating them as failures.
- Hyndman and Athanasopoulos, [Forecasting: Principles and Practice](https://otexts.com/fpp3/),
  covers time-series cross-validation, naive baselines, accuracy measures, prediction intervals,
  residual diagnostics, and forecast horizons.
- [NIST Engineering Statistics Handbook: confidence intervals](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm)
  defines interval estimates and their interpretation.

## Value, revenue, and reversals

Retrieved and read directly rather than summarized.

- [How Stripe Revenue Recognition works](https://docs.stripe.com/revenue-recognition/methodology)
  states the accrual principle: GAAP requires revenue to be recognized "when you realize and earn it,
  which might be earlier or later than when you actually receive payments." This establishes that
  cash movement, invoiced amount, and recognized revenue are distinct figures.
- [How disputes work](https://docs.stripe.com/disputes/how-disputes-work) documents that a disputed
  charge causes Stripe to debit "the disputed amount, plus a dispute fee," from the account, that the
  outcome "is at the sole discretion of the account owner's bank," and that filing patterns vary
  across card networks. It also describes issuer fraud warnings as a signal preceding a dispute
  rather than a reversal in itself. This establishes that a booked conversion is provisional after
  its period closes.

The four-figure ordering, the settlement-maturity rule, the prohibition on comparing a fresh period
against a matured one, and the lead-outcome chain are catalog conclusions supported by these
sources rather than statements made in them.

## Attribution

The guidance and examples are adapted in part from `conversion-landing-pages` and
`ecommerce-storefronts` at `https://github.com/rundesk-ai/rundesk-skills`, commit
`826953197c01c7816fdd480e1eb91ee4fe708a8b`, under the MIT License. Attribution reports observed
credit under a model; the causal boundary and counterfactual replacement are catalog conclusions
supported by the experiment sources above.
