# How exports damage data, and how to catch it

Every mechanism here is silent. The file opens, the columns line up, the totals look plausible, and
the data is wrong. Assume damage and check for it; do not wait for the file to look suspicious.

## CSV is not a format

There is no formal specification for comma-separated values. RFC 4180 is *Informational* — it
"does not specify an Internet standard of any kind" — and it says so directly: "there is no formal
specification in existence, which allows for a wide variety of interpretations of CSV files." It
documents the convention that seemed to be most common in 2005 and registers the `text/csv` MIME
type. Nothing obliges a producer to follow it.

So every one of these is a decision the exporting tool made and did not record:

- the delimiter — comma, semicolon in locales that use a decimal comma, tab, or pipe;
- the quote character, and whether a quote inside a field is doubled or backslash-escaped;
- the line ending, and whether a field may contain one;
- whether a header row exists;
- the character encoding;
- how `null` is distinguished from an empty string, if at all.

**Check columns per row, not just the header, and check them with a quote-aware reader.** A single
unescaped quote or an embedded newline shifts every subsequent field left or right, and a shifted
row is still a valid row. Rows whose column count differs from the header's are the fastest way to
find it.

**Splitting the line on the delimiter is not that check.** A correctly quoted field containing the
delimiter — `"7,473.44"`, an address, a name with a comma — becomes an extra field under a naive
split, and every column after it appears shifted. The output is indistinguishable from a genuine
quoting failure: a currency code sitting in a status column, a date in an amount column. A run that
reports that as a defect has reported its own parser, and has done it in the confident register of a
finding. Use the language's CSV reader, and when you name a shifted row, quote the raw line so the
reader can see the quoting for themselves.

## Spreadsheets convert data on open, and this is not a solved problem

Excel with default settings converts values that look like dates or numbers into dates or numbers.
It does this on open, without asking, and writes the converted value back on save.

The scale is documented. Ziemann, Eren, and El-Osta scanned supplementary files in leading genomics
journals in 2016 and found gene-name conversion errors in about one fifth of papers with
supplementary Excel gene lists. Abeysooriya and colleagues repeated the scan across PubMed Central
for 2014–2020 and found the errors "continued to accumulate unabated" after the 2016 report, at
**30.9% (3,436/11,117)** of articles with supplementary Excel gene lists — higher than the earlier
estimate, partly because values were also being converted to Excel's internal five-digit date
serials, not only to displayed dates and floats.

The standards body gave up on the tool rather than on the data: the HUGO Gene Nomenclature Committee
revised its guidelines in 2020 and renamed symbols to stop spreadsheets rewriting them, citing the
"Excel auto-changing date symbols" problem in its own announcement.

**The lesson for a supplied file is the second study, not the first.** Publicity about the defect
did not reduce it. You cannot assume the person who exported the file knew, or cared, or checked.

What gets converted:

| Value shape | What it becomes |
|---|---|
| `MAR1`, `SEP2`, `DEC1` | A date, then a serial number |
| `1-5`, `3/4`, `2024-3` | A date |
| Leading zeros — `00123`, a zip code, an account number | An integer, zeros gone |
| `1E5`, a hex-looking ID, a long numeric ID | Scientific notation, or rounded |
| `+1 555 0100`, `=SUM(...)` | A formula, or an error |
| `TRUE`, `NA`, `NULL` | A boolean or a special value |

**Check by sampling.** Take ten identifiers from the file and look them up in the source system. If
any is missing, the column was converted. This costs a minute and is the only reliable test.

## Fifteen significant digits, and no more

Microsoft documents that Excel was designed around IEEE 754 and "can only do so within 15 digits of
precision," a limit it states "is a direct result of strictly following the IEEE 754 specification
and isn't a limitation of Excel." Digits past the fifteenth become zeros.

Two consequences:

- **Long identifiers are silently mutilated.** A 16-digit order number, transaction ID, or card
  reference ends in a zero that is not in the source. Two distinct IDs can collapse into one, which
  turns a unique key into a duplicate and multiplies rows in any join.
- **Money computed in binary floating point is approximate.** Microsoft's own example: `0.1` has no
  finite binary representation and is stored rounded by about `-2.8E-17`. Sum enough rows and the
  total disagrees with the source system by cents. Compute money in a decimal type or in integer
  minor units; reserve floating point for things that are genuinely continuous.

Read identifier columns as text at import. Every serious reader supports declaring the type; the
default of "guess per column" is what produces the damage.

## Encoding, and the mark you cannot see

The WHATWG Encoding Standard defines UTF-8, UTF-16LE, and UTF-16BE, and is explicit that byte-order
mark handling is **not part of the encodings themselves** but of wrapper algorithms around them.
Whether a leading BOM is stripped therefore depends on the reader, not the file.

The practical effect is a first column whose name is not what it appears to be — `date` carrying an
invisible `U+FEFF` prefix, so a lookup by that name fails while the column is plainly visible on
screen. If a column exists but cannot be addressed, check the header bytes.

Mojibake — `Ã©` where `é` belongs, `â€™` where an apostrophe belongs — means the file was written in
one encoding and read as another, usually UTF-8 read as a legacy single-byte encoding. It matters
beyond appearance: it changes the string, so grouping and joining on that column will split what
should be one value.

## Truncation, sampling, and withheld rows

Three different things remove rows, and only one of them is usually reported:

- **Truncation.** An export or API stops at a bound. Suspect any round row count.
- **Sampling.** Some tools return an estimate from a subset above a volume threshold. An estimate
  has sampling error and must not be reported as a count.
- **Thresholding.** A tool may withhold rows to prevent identifying individuals. Google documents
  this for Analytics: data "may be withheld" from a report, exploration, or API call involving
  demographics or audiences built on them, and a search-query row "may be withheld if there aren't
  enough total users." The thresholds are system-defined and cannot be adjusted; narrowing the date
  range makes withholding more likely.

Thresholding is the one that corrupts analysis quietly, because the total is still right while the
breakdown is short. **If the segments do not sum to the total, suspect withheld rows before
suspecting arithmetic.**

## Dates, and the two that are not ambiguous by accident

`03/04/2026` is March 4th or April 3rd depending on the locale of whoever exported it. There is no
way to tell from the value. There is a way to tell from the column: find any row whose first
position exceeds 12, and the ambiguity is resolved for the whole column. If no such row exists, the
column is genuinely ambiguous and must be treated as unestablished rather than guessed.

Two related traps:

- **A date column can be parsed two different ways within one file** when a tool guesses per chunk.
  Check the minimum and maximum; an impossible spread is the symptom.
- **Excel's date serials begin at 1900 and include a February 29th, 1900** — a date that did not
  exist. Serial-to-date conversion done by hand will be off by one for early dates.

## The checks, as a list

Run these on any supplied file before analysis. Record which ones you ran; they belong in the return.

1. Row count against expectation; flag round numbers as suspected truncation.
2. Column count per row against the header, read with a quote-aware CSV reader rather than a split.
3. Header bytes — leading BOM, trailing whitespace, duplicate names.
4. Encoding — scan for mojibake sequences in text columns.
5. Key uniqueness on the intended grain.
6. Ten identifiers sampled against the source system.
7. Type per column, including one text value hiding in a numeric column.
8. Null vocabulary — how many distinct spellings of "missing" the file uses.
9. Distinct values per categorical column, looking for case and spelling variants.
10. Minimum, maximum, and tails per numeric and date column.
11. Non-data rows — totals, repeated headers, footnotes, blank separators.
12. Currency present and consistent for every money column.
13. Segments summed against the reported total.
