---
name: verifying-datasets
description: Use when data arrives as a file, export, spreadsheet, or pasted table rather than from a live query — a CSV someone hands over, a report export, a finance or CRM extract — or when two sources disagree about the same number. It supplies the provenance a file needs before it is trusted, the profile that comes before analysis, the corruptions exports introduce without reporting them, and the reconciliation that explains a disagreement instead of picking a side. Do not use it for choosing the analytical method for a growth question, for querying a service that answers the question directly, or for a figure someone else published.
---

# Verifying datasets

A file is not a system. It is one person's answer to a question you did not hear, taken at a moment
you cannot see, through filters nobody wrote down. Your first job is to establish what it is, and
your second is to say what it cannot support. The analysis comes third and is usually the easy part.

The metric contract in `analyzing-growth-data` still governs: population, denominator, window,
identity, exclusions. This skill adds what that method cannot know — that the material itself may
be wrong in ways nothing in it reports.

## Establish the file before you read a number from it

Settle these before any arithmetic. Ask for what is missing rather than inferring it.

```text
System:     the source of record it came out of, and its version or environment
Extractor:  who ran the export, and whether they can run it again
Extracted:  the moment it was taken, in a named timezone
Filters:    every filter, date range, segment, and permission scope applied at export
Population: what one row is — a person, a session, an order, an event, a day
Grain:      whether rows are unique on that key, or repeat
Currency:   for money, the currency per row and whether amounts are gross, net, or refund-adjusted
Completeness: whether the export was truncated, paginated, sampled, or thresholded
```

**A row limit is the most common silent defect.** Exports truncate at a bound the file does not
record. If the row count is exactly 1,000, 10,000, 50,000, or another round number, treat it as
truncated until the extractor says otherwise.

An export you cannot ask anyone about is still usable. Say so in the return, and lower what you
claim from it accordingly.

## Profile before you analyze

Run this before forming any view of what the data says. Every line is a fact you will need in the
return anyway.

1. **Row and column counts**, against what the extractor expected. A discrepancy is the finding.
2. **Uniqueness of the intended key.** Duplicated keys silently multiply rows in any later join.
3. **Nulls and blanks per column**, and whether blank, `null`, `0`, `N/A`, and `-` are being used
   for the same thing. They usually are, and they usually mean different things.
4. **Type consistency per column.** One text value in a numeric column changes how every tool reads
   the column, not just that row.
5. **Ranges and extremes.** Minimum, maximum, and the tails. Negative quantities, future dates, and
   a `1970-01-01` cluster are each a specific bug with a specific cause.
6. **Distinct values for every categorical column.** `US`, `us`, `USA`, and `United States` are four
   segments in every group-by until you decide otherwise.
7. **Rows that are not data** — totals, subtotals, headers repeated mid-file, footnotes, and a blank
   separator row. A totals row inside the data double-counts the file.

Compare a small hand-checkable slice against the aggregate before trusting the aggregate. If ten
rows you can read by eye do not produce the number the whole file produces, the file wins the
argument and you have found something.

## Process reproducibly

For a file too large or complex to verify by hand, use a deterministic local script or query rather
than hidden spreadsheet clicks or mental arithmetic. Read [local processing](references/local-processing.md)
before parsing a workbook, joining files, scraping a bounded public table, or aggregating enough
rows that a rerunnable transformation is needed.

Keep the supplied bytes read-only and work in a disposable location outside the source directory
and any repository. Do not install a dependency merely to make the run convenient. Use an available
quote-aware reader, workbook reader, streaming pass, or local query engine whose behavior you can
state. Preserve identifiers as text and money as decimal values or integer minor units.

Return the input name and checksum; parser, encoding, delimiter, schema, null, timezone, and sheet
choices; exact script or query and runtime; command and parameters; counts before and after every
filter, join, exclusion, and grouping; unmatched and multiplied rows; and an independent total or
hand-check. A local command proves how the supplied file was processed, not where its data
originated. If the source file, parsing choice, or transformation cannot be reproduced, lower the
claim instead of hiding the gap behind an aggregate.

## Assume the export damaged the data

`references/file-integrity.md` has the mechanisms and the checks. The short version, because these
are the ones that leave no trace in the file:

| Damage | How it looks afterwards | Check |
|---|---|---|
| Spreadsheet auto-conversion | Identifiers turned into dates or serial numbers | Compare a sample of IDs against the source system |
| Precision loss past 15 digits | Long IDs ending in zeros; totals off by cents | Read IDs as text; compare a known long value |
| Encoding mismatch | `Ã©` for `é`; an invisible mark on the first column name | Check the first header name and any non-ASCII column |
| Delimiter or quoting failure | A row with too many columns; a truncated address | Count columns per row with a quote-aware reader, never a naive split |
| Ambiguous dates | `03/04` parsed as March in one column and April in another | Find a day past the 12th and see which position moved |
| Thousands separators | A numeric column read as text | Check the column's type, not its appearance |

None of these announces itself. A file that opens cleanly and looks right is the normal appearance
of every one of them.

## Money and time are where precision dies

**Money.** Never compute money in binary floating point; that is where the missing cent comes from.
Keep the currency with the amount — a column of mixed-currency amounts summed into one total is
meaningless, and not every currency has two decimal places. Establish which of gross, net of
refunds, net of fees, and recognized revenue the column holds. Those are four different numbers,
and a source that reports money movement is not reporting recognized revenue.

**Time.** A timestamp with no timezone is not a time. Fix event time, ingestion time, and reporting
time separately and say which one the file is keyed on. Two exports taken from the same system on
different days will disagree about the same past period whenever late or backdated data lands
between them, and that disagreement is correct behavior rather than a defect.

**Weeks are not months and some years have 53 of them.** A week-grained series compared against a
month-grained one will drift, and a retail or fiscal calendar adds a 53rd week every five or six
years, which inflates that year's total against every neighbour. Comparing a 53-week year to a
52-week year without restating it is a double-digit error that looks like growth.

## When two sources disagree

The disagreement is the finding. Do not average, and do not pick the number that helps.

Work in this order, stopping at the first that explains the gap. `references/reconciling-sources.md`
covers each with its diagnostic.

1. **Population** — do the two count the same things? Different eligibility explains most gaps.
2. **Window** — same period, same timezone, same treatment of late data, taken at the same moment?
3. **Definition** — is a session, a user, a lead, or an order the same object in both?
4. **Identity** — are the two counting people, devices, cookies, or accounts?
5. **Filtering** — bot exclusion, internal traffic, consent, sampling, thresholding, and permission
   scope each remove rows silently and differently.
6. **Arithmetic** — deduplication, currency, and rounding, in that order.

Return a reconciliation that starts at one source's number, names each adjustment with its size, and
lands on the other's. An unexplained residual stays in the return as an unexplained residual, with
its size. **Reconciled means the bridge is complete, not that the two are close.**

## Break it down before you conclude

An aggregate is a claim about a population you have not looked at. Segment before you conclude, not
after someone challenges you.

A direction that holds in every subgroup can reverse in the total whenever subgroup sizes differ,
and the reversal is arithmetic rather than a mistake — so the aggregate and the breakdown can both
be correct and tell opposite stories. Decide which question is being asked before choosing which to
report, and say which one you chose.

Two decomposition habits earn their cost every time:

- **Split by the thing that changed**, not by the dimensions already on the dashboard. A total that
  moved is almost always one segment moving and the rest standing still.
- **Check that the parts sum to the whole.** When they do not, something is being withheld,
  deduplicated across rows, or double-counted. Suppressed small cells are the usual cause and are
  invisible by design.

## Return what the data can and cannot support

Return:

1. the question, and the decision it serves;
2. provenance — system, extractor, extraction moment and timezone, filters, and grain;
3. the profile, including row counts, key uniqueness, and every integrity check run;
4. the processing trail, including input checksum, exact script or query, runtime, parser choices,
   and filter and join counts when a local transformation was used;
5. the result with its numerator, denominator, and uncertainty;
6. the breakdown, and whether the parts sum to the whole;
7. for a disagreement, the reconciliation with each adjustment and any residual;
8. what this file cannot establish, and what would establish it.

A number without its denominator, a total that no breakdown reproduces, an export nobody can run
again, and a clean-looking file whose integrity was never checked are each unestablished. Say so
plainly rather than releasing a softened version of the claim.
