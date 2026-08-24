# Forecasting and uncertainty

## Establish the forecast contract

Name the outcome, aggregation interval, horizon, update cadence, decision threshold, information
available at prediction time, and the cost of over- and under-prediction. Keep a forecast distinct
from a target, quota, scenario, or commitment.

Use a simple seasonal or naive baseline first. Split evaluation by time, never by randomly mixing
future observations into training. Backtest over several historical origins so the score does not
depend on one unusually easy period.

## Compare useful error measures

Choose measures that fit the decision and data. Absolute error preserves the outcome's unit;
percentage error becomes unstable near zero; squared error gives large misses extra weight. Report
the baseline, central estimate, interval coverage, and error by relevant period or segment. One
average can hide failure exactly where capacity or budget decisions are tight.

## Represent uncertainty honestly

Provide prediction intervals for future observations and state their intended coverage. Widen them
for longer horizons and material unresolved events. Historical backtest coverage is evidence about
calibration under past conditions, not a guarantee under a structural break.

For experiments and estimates, report confidence or credible intervals with the model and unit of
analysis. Repeatedly checking a fixed-horizon test inflates false positives unless the method and
stopping rule account for it.

## Detect conditions that invalidate the model

Check for product, pricing, channel, tracking, policy, and seasonality changes that alter the data-
generating process. Compare residuals and error over time. Refuse a precise forecast when history
does not contain a relevant analogue; provide bounded scenarios and the assumptions that separate
them instead.
