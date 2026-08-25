# Source basis

Verified in August 2026. Each source below was retrieved directly and read, rather than summarized,
because the load-bearing claims are standards text, vendor documentation, and published statistics —
the three kinds a summary is least safe on. Where a source could not be retrieved, that is stated.

The workflow itself — the provenance block, the profile order, the reconciliation ledger, and the
return contract — is a Rundesk synthesis. The sources establish the failure modes it guards against,
not the procedure.

## Tier 1 — standards and vendor documentation

- [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180.txt) is categorized *Informational* and states in
  its Status of This Memo that it "does not specify an Internet standard of any kind." Section 2
  states that "there is no formal specification in existence, which allows for a wide variety of
  interpretations of CSV files," and documents the format "that seems to be followed" by most
  implementations. This establishes that delimiter, quoting, line-ending, header, and encoding
  choices are producer decisions rather than format guarantees.

- [Floating-point arithmetic may give inaccurate results in Excel](https://learn.microsoft.com/en-us/troubleshoot/microsoft-365-apps/excel/floating-point-arithmetic-inaccurate-result)
  states that Excel was designed around IEEE 754, that it can store numbers only "within 15 digits of
  precision," and that this limit "is a direct result of strictly following the IEEE 754
  specification and isn't a limitation of Excel." It gives `0.1` as a value with no finite binary
  representation, rounded by approximately `-2.8E-17` on storage. This establishes both the
  identifier-truncation and the money-precision claims.

- [WHATWG Encoding Standard](https://encoding.spec.whatwg.org/) defines UTF-8, UTF-16LE, and
  UTF-16BE, and states that byte-order-mark handling is "not being part of the encodings themselves
  and instead being part of wrapper algorithms in this specification." This establishes that whether
  a leading BOM is stripped depends on the reading implementation, which is why a first column name
  can carry an invisible prefix.

- [GA4 data freshness](https://support.google.com/analytics/answer/11198161) states that "data
  processing can take 24-48 hours" and that "during that time, data in your reports may change."
  This establishes that a figure for a past period is a function of when it was extracted, and is
  the basis for recording the extraction moment alongside the period.

- [GA4 data thresholds](https://support.google.com/analytics/answer/9383630) states that data "may be
  withheld" from a report, exploration, or API call including demographic data or audiences defined
  using it, that a search-query row "may be withheld if there aren't enough total users," that
  thresholds are system-defined and cannot be adjusted, and that a narrow date range makes
  withholding more likely. This establishes suppression as a cause of a breakdown that does not sum
  to its total.

## Tier 2 — published studies of the failure itself

- Ziemann, Eren, and El-Osta, [Gene name errors are widespread in the scientific literature](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-016-1044-7),
  *Genome Biology* 17:177 (2016), found gene-name conversion errors in approximately one fifth of
  papers with supplementary Excel gene lists. The publisher page was not retrievable directly at the
  time of writing; the finding is quoted here as restated in the follow-up study below, which is
  cited for the figure rather than this paper.

- Abeysooriya, Soria, Kasu, and Ziemann, [Gene name errors: Lessons not learned](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1008984),
  *PLOS Computational Biology* 17(7) (2021). Retrieved and read directly. Scanning PubMed Central
  supplementary files from 2014 to 2020, it reports that gene name errors "continued to accumulate
  unabated in the period after 2016" and identifies errors in "30.9% (3,436/11,117) of articles with
  supplementary Excel gene lists; a figure significantly higher than previously estimated," partly
  because values were converted to internal five-digit date serials as well as to dates and floats.
  This is the source for the claim that publicity about spreadsheet coercion did not reduce it.

- [HGNC new guidelines, 2020](https://blog.genenames.org/hgnc/2020/09/28/New_Guidelines/). Retrieved
  and read directly. The HUGO Gene Nomenclature Committee describes its guideline revision and its
  "solution for the 'Excel auto-changing date symbols' problem," referring to its *Nature Genetics*
  comment article. This establishes that a standards body changed its identifiers rather than rely on
  exporters configuring the tool correctly.

- Bickel, Hammel, and O'Connell, [Sex Bias in Graduate Admissions: Data from Berkeley](https://www.science.org/doi/10.1126/science.187.4175.398),
  *Science* 187(4175):398–404 (1975). The publisher page is behind a bot wall and was not retrievable
  directly. The case is described here as summarized in the Stanford Encyclopedia of Philosophy entry
  below, which is the source actually read; no figure from the original paper is quoted.

- [Simpson's Paradox](https://plato.stanford.edu/entries/paradox-simpson/), *Stanford Encyclopedia of
  Philosophy*, first published 2021, substantive revision June 2026. Retrieved and read directly.
  Section 5.5 states that Bickel et al. found men more likely than women to be accepted to Berkeley's
  graduate programs while "the authors were unable to detect a bias towards men in any individual
  department," because "women were more likely to apply to departments with lower acceptance rates,"
  producing an association between the grouping variable and the outcome that can generate a
  reversal. This establishes the decomposition rule and that both figures can be correct.

- [NRF 4-5-4 calendar](https://nrf.com/resources/4-5-4-calendar). Retrieved and read directly.
  "Dividing the retail calendar into 52 weeks of seven days each, or 364 days, leaves an extra day
  each year to be accounted for. As a result, every five to six years a week is added to the fiscal
  calendar. This anomaly has most recently occurred in FY12, FY17 and FY23." NRF publishes restated
  and non-restated calendars for those years. This establishes the 53-week comparison trap.

## Catalog conclusions, not source facts

These are this catalog's positions. They are consistent with the sources above but are not stated by
any of them, and should be labelled as judgments where a reader might take them for findings.

- **A round row count is suspected truncation until the extractor says otherwise.** A local
  heuristic. No source establishes a threshold; the value is that it costs one question to rule out.
- **Sampling ten identifiers against the source system is the reliable test for coercion.** A local
  heuristic, chosen because the studies above show the corruption is undetectable within the file.
- **Never average two disagreeing numbers, and never adopt the favourable one.** A catalog rule about
  releasing results, derived from the certification standard in `analyzing-growth-data` rather than
  from any source here.
- **The reconciliation residual stays in the return.** A catalog rule.
- **Compute money in decimal or integer minor units, never in binary floating point.** The
  precision behavior is Microsoft's documented fact; the instruction that follows from it is this
  catalog's.

## Not established here

- **Excel's 1900 date-serial behavior**, mentioned in `file-integrity.md`, is long-standing
  documented behavior but was not retrieved from a Microsoft page for this package. Treat it as a
  check worth running rather than as a cited fact.
- **No source here establishes how often supplied marketing exports are corrupted.** The published
  measurements are from genomics. The mechanism transfers because it is the tool's behavior rather
  than the domain's; the rate does not.
