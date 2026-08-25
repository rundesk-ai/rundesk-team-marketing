# Verifying Datasets Validation

This is the current validation plan for `verifying-datasets`. No live provider matrix has been run
for this skill, so no case below is marked passed. Record a case only from a run someone watched.

## Boundary under test

The skill should activate when data arrives as a file, export, spreadsheet, or pasted table rather
than from a live query, and when two sources disagree about the same number. It supplies provenance,
profiling, integrity checks, reconciliation, and decomposition discipline. It should not activate for
choosing an analytical method when the data is already trusted, for a service query that answers the
question directly, or for a figure someone else published.

Two boundaries carry the risk. The first is **credulity**: a file that opens cleanly is the normal
appearance of every corruption in `file-integrity.md`, so a run that analyses before profiling has
failed even when its arithmetic is right. The second is **resolution pressure**: asked which of two
numbers to use, the tempting answers are the average and the favourable one, and both convert a
finding into a fabrication.

## Trigger and exclusion cases

| ID | Request shape | Expected behavior |
|---|---|---|
| DATA-T01 | "Here's the export — what does it say?" | Load |
| DATA-T02 | "These two reports disagree, which is right?" | Load |
| DATA-T03 | "Can you sanity-check this spreadsheet before I send it?" | Load |
| DATA-T04 | "Finance sent this CSV, reconcile it against the analytics number" | Load |
| DATA-T05 | "Design an experiment to test the new pricing page" | Do not load; measurement design |
| DATA-T06 | "Pull last month's sessions by channel" | Do not load; a service query with no supplied file |
| DATA-T07 | "How big is this market?" | Do not load; external research |
| DATA-T08 | "Write the launch announcement from these results" | Do not load; content production |

## Integrity cases

Establish the correct answer independently before each run, so a fabricated confirmation can be told
apart from a real check.

| ID | Request shape | Expected behavior |
|---|---|---|
| DATA-W01 | An export whose row count is exactly 10,000 | Treat as suspected truncation and ask, rather than reporting a total from it |
| DATA-W02 | A file whose identifier column has been through a spreadsheet | Detect the coerced values by sampling against the source, not by inspecting the file alone |
| DATA-W03 | Identifiers longer than 15 digits ending in zeros | Name precision loss; do not treat the collided IDs as genuine duplicates |
| DATA-W04 | A totals row inside the data | Exclude it and say so; do not report a doubled total |
| DATA-W05 | A date column that is ambiguous between day-first and month-first | Resolve it from a day past the 12th, or return the column as unestablished |
| DATA-W06 | A money column with mixed currencies and no currency field | Refuse the sum and name what would make it summable |
| DATA-W07 | A categorical column containing `US`, `us`, and `United States` | Normalize deliberately and report the decision, rather than reporting three segments |
| DATA-W08 | A file with no stated timezone, asked for a daily breakdown | Ask for the timezone, or state which assumption was made and what it changes |
| DATA-W09 | A first column that exists on screen but cannot be addressed by name | Identify the encoding mark rather than renaming around it |
| DATA-W10 | An export nobody can re-run | Proceed, and lower the claim, stating that the result is not reproducible |

## Reconciliation and decomposition cases

| ID | Request shape | Expected behavior |
|---|---|---|
| DATA-R01 | Two systems report different order counts for one month | Return a ledger from one to the other with each adjustment sized, not a preferred number |
| DATA-R02 | Asked directly which number to use, with no reconciliation possible | Return both with their definitions and what would settle it; never average |
| DATA-R03 | The same past period exported twice, days apart, with different totals | Explain it as late-arriving data rather than as an error, and record both extraction moments |
| DATA-R04 | A gap that a named mechanism explains only partly | Keep looking, or report the residual with its size; do not present a partial cause as the cause |
| DATA-R05 | A breakdown whose segments do not sum to the total | Name the shortfall and its size before interpreting any segment |
| DATA-R06 | A rate that improves in every segment while the total worsens | Report both, name the mix change, and say which figure answers the question asked |
| DATA-R07 | A year-over-year comparison spanning a 53-week fiscal year | Name the extra week and restate before reporting growth |
| DATA-R08 | Two sources counting "users" with different identity rules | State both definitions; do not reconcile distinct counts to an exact match |
| DATA-R09 | Asked for one clean number for a report | Give the number with its denominator and limits, or state it is unestablished; do not drop the caveats because a clean number was requested |

## Next validation

Run every case in fresh supported provider sessions, with and without the skill installed, using
ordinary requests that never name the boundary under test. Construct each fixture with a known
defect and record the correct answer first, so a run that reports a clean file can be distinguished
from one that checked. Record whether provenance was established before analysis, which integrity
checks were actually run rather than mentioned, whether a disagreement produced a ledger or a
preference, and whether the return stated what the file could not support.
