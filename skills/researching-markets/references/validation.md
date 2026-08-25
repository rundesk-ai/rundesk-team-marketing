# Researching Markets Validation

This is the current validation plan for `researching-markets`. No live provider matrix has been run
for this skill yet, so none of the cases below is marked passed. Record a case only from a run
someone watched.

## Boundary under test

The skill should activate when a question asks how large a market or category is, what a segment is
worth, what share is available, or whether demand is growing. It supplies a bottom-up method on
counted public data, range-and-assumption discipline, and the provenance traps in published market
figures. It should not activate for first-party analytics, a company's own revenue forecast, website
auditing, or a research question with no size or demand component.

Two boundaries carry the risk. The first is **provenance**: a published figure whose method is
paywalled must not be reported as a measurement, and repetition across outlets must not be counted as
corroboration. The second is **precision**: an estimate built on judged inputs must be returned as a
range with its assumptions, never as a point.

## Trigger and exclusion cases

| ID | Request shape | Expected behavior |
|---|---|---|
| MKT-T01 | "How big is the market for X?" | Load |
| MKT-T02 | "Is demand for X growing?" | Load |
| MKT-T03 | "What's our TAM?" | Load |
| MKT-T04 | "What share of this category could we realistically win?" | Load |
| MKT-T05 | "What was our revenue last quarter?" | Do not load; first-party analytics |
| MKT-T06 | "Forecast our own bookings for next year" | Do not load; first-party forecasting |
| MKT-T07 | "Why is this page not indexed?" | Do not load; site retrieval |
| MKT-T08 | "Verify whether this regulation applies to us" | Do not load; general research with no size component |

## Method and provenance cases

| ID | Request shape | Expected behavior |
|---|---|---|
| MKT-W01 | A press release states a market will reach a precise figure by a future year | Report it as an assertion of unknown provenance; do not present it as measured |
| MKT-W02 | Several outlets carry the same figure | Trace to origin and count it once; do not describe repetition as corroboration |
| MKT-W03 | Two published figures for one market differ by more than a factor of two | Compare boundaries before numbers, and name undisclosed scope divergence as the likely cause |
| MKT-W04 | Only judged inputs are available for a share assumption | Return a range with the assumption labelled, never a point estimate |
| MKT-W05 | A bottom-up and a top-down build disagree | Reconcile and report the reason; do not average them into a midpoint |
| MKT-W06 | Asked to size a narrow product category in one country this year | Say what is unestablished, give the bound from the nearest counted total, and name what would close it |
| MKT-W07 | A stated market boundary is missing from the request | Define who buys, what, where, when, and at what price level before producing a number |
| MKT-W08 | A multi-year series crosses an industry-classification revision | Name the time series break rather than presenting one continuous line |
| MKT-W09 | A search-interest line is offered as evidence of demand growth | Treat it as relative attention, name the instrument's instability, and pair it with a counted series |
| MKT-W10 | A company's own stated addressable market is available | Record it as the company's claim and name the interest |
| MKT-W11 | Asked for one number for a board deck | Give the range and the sensitivity; do not collapse to a point because a point was requested |

## Next validation

Run every case in fresh supported provider sessions, with and without the skill installed, using
ordinary requests that never name the boundary under test. Establish the counted data independently
first, so a fabricated or laundered figure can be distinguished from a sourced one. Record activation,
whether the boundary was defined before the number, whether assumptions were labelled counted or
judged, and whether the answer was reviewable by someone who wanted to change one input.
