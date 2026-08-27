# Reproducible local processing

Use a local script or query when the evidence cannot be checked reliably by eye. The code is part of
the calculation trail, not a substitute for source provenance. Keep the supplied input immutable,
work in a disposable location outside a repository and the source directory, and do not install a
new dependency merely to complete the run.

## Fix the input and parser contract

Record the input filename, byte size, cryptographic checksum, and modification time before reading
it. A checksum identifies the exact bytes processed; it does not establish who exported them, which
filters were applied, or whether the export was complete.

Make every parsing choice explicit:

- CSV or delimited text: encoding, byte-order-mark handling, delimiter, quote and escape rules,
  header rule, newline handling, null vocabulary, and declared column types. Use a quote-aware
  reader and treat delimiter or header detection as a heuristic to verify, not a fact.
- Workbook: file format, sheet names, selected sheet and range, hidden sheets, rows, and columns,
  merged cells, active filters, date system, formulas, cached results, displayed rounding, and error
  cells. If the available reader cannot evaluate formulas, distinguish the formula from its cached
  value and mark freshness unestablished.
- Identifiers: read them as text and preserve leading zeros and all digits. Never convert an
  identifier merely because every observed value looks numeric.
- Money: retain the currency per row and calculate with decimal arithmetic or integer minor units.
  Never sum mixed currencies or silently assume two decimal places.
- Dates and times: declare the date order, timezone, event-time field, and treatment of ambiguous or
  invalid values before grouping by day, week, or month.

Python's `csv` reader returns strings unless numeric conversion is explicitly requested, supports
declared dialect parameters, and requires `newline=''` for correct embedded-newline handling. Those
are useful defaults, not a requirement to use Python. A different reader is acceptable when its
equivalent choices can be fixed and returned.

## Make large transformations auditable

Prefer one deterministic pass, chunked processing, or a local query engine to loading an unknown-size
file blindly into memory. A task-scoped script may parse, validate, filter, join, group, and
aggregate supplied data, but it must not modify the inputs, call an unrelated service, inspect
adjacent files, or emit row-level personal data.

For every transformation, return:

```text
Input: checksum, bytes, rows, columns, and declared grain
Runtime: tool and version
Parser: format, encoding, dialect or workbook choices, schema, nulls, dates, and timezone
Execution: exact script or query, command, parameters, and exit status
Filters: rule, rows before, rows removed, rows after
Joins: key, uniqueness on both sides, expected cardinality, matched, unmatched, and multiplied rows
Groups: grouping keys, group count, aggregate units, and whether parts sum to the whole
Output: rows, columns, checksum when written, and location or disposal status
Proof: a hand-checkable sample or independently computed control total
```

An exit status is not arithmetic proof. Re-run the same code against the same checksum and require
the same result. Then compare a small slice or control total through an independent path. If a join
multiplies rows, a filter count cannot be reconciled, or grouped parts do not sum to the eligible
whole, stop and return that discrepancy before interpreting the output.

Keep temporary scripts and derived files only as long as the task requires. Return the exact code
in the report or provide it at the authorized destination when requested; do not place it in a
project, scheduled job, shared folder, or production path without separate authority.

## Bound public-page extraction

A table acquired from a public page needs both web provenance and file-style integrity. Record the
URL, retrieval time and timezone, response status, pagination or result bounds, selected fields,
extraction rule or selector, and the raw and accepted record counts. Identify it as acquired public
data rather than a first-party system-of-record export.

Use only the pages required for the assigned growth-evidence question and follow the bounded public
surface retrieval rules already loaded for the task. Honor the site's crawler rules. Never bypass a
login, paywall, bot control, rate limit, or other access control; never submit a form or mutate the
site as part of extraction. Broad collection of published facts belongs to external research, and
an authenticated analytics surface belongs to its supported read-only integration.

Read [sources](sources.md) when changing these parser or crawler claims.
