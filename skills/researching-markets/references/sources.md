# Market research source basis

This package is a Rundesk synthesis of statistical-agency documentation, accounting-standard review,
metrology and public-audit guidance, and two documented cases of published market figures failing.
Use this file to audit or update any claim in the other references.

**Read in this order of authority.** A statistical agency documents what it counted and what it
excluded. A standard-setter or auditor documents how estimates fail. A named analyst's published
build shows method. A press release states a number. Never present a later tier as an earlier one.

Verified against the sources listed here in **August 2026**. Statistical programs are reorganized and
industry classifications are revised, so re-check a program's current name and coverage before
building a series on it.

## Tier 1 — statistical agencies

- [Economic Census](https://www.census.gov/programs-surveys/economic-census/about.html): five-year
  cadence, establishment universe, industry and geography counts, and the paid-employee-only
  limitation.
- [County Business Patterns](https://www.census.gov/programs-surveys/cbp/about.html): annual
  establishment, employment, and payroll counts to ZIP code; the excluded industries and government
  establishments; noise infusion on small cells.
- [Annual Integrated Economic Survey](https://www.census.gov/programs-surveys/aies.html): the program
  that replaced and integrated seven annual business surveys.
- [Annual Retail Trade Survey](https://www.census.gov/programs-surveys/arts/about.html): retained
  here only to establish that the program **transitioned to the integrated survey**. Do not treat
  ARTS as current.
- [Quarterly e-commerce retail sales](https://www.census.gov/retail/ecommerce.html): e-commerce and
  total retail sales, and the practice of stating sampling error inline with each change.
- [BLS Quarterly Census of Employment and Wages](https://www.bls.gov/cew/overview.htm): coverage of
  more than 95% of US jobs, six-digit industry granularity, the six-month lag, the excluded worker
  categories, and the 2025 change publishing metropolitan data as totals only.
- [NAICS, via BLS](https://www.bls.gov/bls/naics.htm): the production-oriented conceptual framework,
  and that revisions create time series breaks.
- [Eurostat structural business statistics](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Structural_business_statistics_overview):
  sector coverage, the variables published, several-hundred-activity granularity, head-count
  employment.
- [UK Annual Business Survey](https://www.ons.gov.uk/businessindustryandtrade/business/businessservices/methodologies/annualbusinesssurveyabs):
  non-financial coverage, four-digit national and two-digit regional granularity, and the statement
  that more detailed breakdowns reduce statistical quality.

## Tier 1 — filings and segment reporting

- [EDGAR full-text search](https://www.sec.gov/edgar/search/): full text of electronic filings
  **since 2001** and no earlier.
- [IFRS 8 Operating Segments](https://www.ifrs.org/issued-standards/list-of-standards/ifrs-8-operating-segments/):
  the disclosure objective and the related product, geography, and major-customer requirements.
- [Post-implementation review of IFRS 8, feedback statement](https://www.ifrs.org/-/media/project/pir-ifrs-8/educational-material/pir-ifrs-8-operating-segments-feedback-statement.pdf):
  the standard-setter's own record that respondents found segments not comparable across entities in
  the same industry, and its response that comparability can rarely be achieved.

**Not verified, and therefore not quoted anywhere in this package:** the primary text of the US
segment standard or its recent amendment, and the verbatim operating-segment definition in IFRS 8.
Both are gated. The package therefore describes segment reporting from the review statement above and
from filings themselves, and makes no quotation from an unopened standard.

## Tier 1 — estimation and uncertainty guidance

- [Guide to the expression of uncertainty in measurement (JCGM 100:2008)](https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf):
  the Type A and Type B distinction, evaluation of a non-repeated input by scientific judgement from
  all available information, and the instruction not to double-count uncertainty components.
- [GAO Cost Estimating and Assessment Guide (GAO-20-195G)](https://www.gao.gov/products/gao-20-195g):
  that quality estimates fall within a range, that failing to address risk produces point estimates
  carrying no information about likelihood and sometimes meaningless confidence levels, and the
  requirement to cross-check with an alternative methodology and examine the difference.
- [The Aqua Book](https://www.gov.uk/government/publications/the-aqua-book-guidance-on-producing-quality-analysis-for-government):
  that uncertainty is inherent in any analysis, and the assumptions log — each assumption's effect,
  reliability, timing, rationale, and sign-off.

## Tier 2 — documented failures of published figures

Specific and verifiable. Each establishes something about a named figure, not a measured failure rate
for an industry.

| Source | Establishes |
|---|---|
| [GAO-10-423](https://www.gao.gov/products/gao-10-423) | Three widely cited government-attributed estimates could not be substantiated because the underlying studies did not exist; agencies could not locate source data or methodology for figures attributed to them; and a citation chain ran association to agency to international body and ended in nothing |
| [Grand View Research release, 3 July 2023](https://www.prnewswire.com/news-releases/artificial-intelligence-market-to-hit-1-811-75-billion-by-2030-grand-view-research-inc-301868806.html) | The figure $1,811.75 billion by 2030 at a 37.3% CAGR |
| [The Research Insights release, 22 May 2025](https://www.prnewswire.com/news-releases/artificial-intelligence-market-share-worth-1-811-75-billion-globally-by-2030---exclusive-report-by-the-research-insights-302463139.html) | The identical terminal figure at 36.6%, marketed as an exclusive report — the mismatch that shows the endpoint was taken rather than derived |
| [ABI Research](https://www.abiresearch.com/news-resources/chart-data/report-artificial-intelligence-market-size-global) | $467 billion for the same year on a narrower stated scope, and a gated underlying report |
| [IEEE Spectrum, 18 August 2016](https://spectrum.ieee.org/popular-internet-of-things-forecast-of-50-billion-devices-by-2020-is-outdated) | Provenance of the 50-billion-devices forecast to two vendor sources, both originators' later downward revisions, wide contemporaneous divergence, and the figure's persistence after retraction |

## Tier 2 — published builds and the disagreement between them

Both sides published their arithmetic, which is why they are cited: the value is the method and the
disclosure, not the answers.

- [Damodaran on Uber's market, June 2014](https://aswathdamodaran.blogspot.com/2014/06/a-disruptive-cab-ride-to-riches-uber.html):
  a stated build to a roughly $100 billion global taxi and limousine market, the explicit framing that
  it is the author's estimate rather than the true value, and self-flagging of an optimistic share
  assumption.
- [Gurley's rebuttal, July 2014](https://abovethecrowd.com/2014/07/11/how-to-miss-by-a-mile-an-alternative-look-at-ubers-potential-market-size/):
  that anchoring on a historical market assumes the entrant has no effect on market size, the
  precision-versus-accuracy warning, and disclosure of the author's own investment interest.

## Tier 2 — demand signal documentation and its limits

- [Google Trends methodology](https://support.google.com/trends/answer/4365533): division by total
  searches for the geography and period, 0-100 scaling, the documented exclusions including AI answer
  surfaces, statistical noise at low volume, and the statement that it is not a scientific poll.
- [The Parable of Google Flu (Science, 2014)](https://gking.harvard.edu/files/gking/files/0314policyforumff.pdf):
  the magnitude of the failure, and the named traps of big data hubris and algorithm dynamics.
- [Indeed Hiring Lab job postings tracker](https://github.com/hiring-lab/job_postings_tracker): the
  baseline date, per-series seasonal adjustment, trailing average, the caveat that the numbers are not
  an indicator of the publisher's own performance, and the documented history of methodology change
  and revision.
- [OECD Patent Statistics Manual](https://www.oecd.org/content/dam/oecd/en/publications/reports/2009/02/oecd-patent-statistics-manual_g1gh9fa4/9789264056442-en.pdf):
  that not all inventions are patented, that filing propensity differs sharply by field including
  deliberate flooding, that patent value is highly skewed so counts mislead, and the 18-month
  publication lag.

## What this package deliberately does not cite

- **TAM, SAM, and SOM as defined terms.** No standards body, regulator, or foundational paper defines
  them. This package treats them as convention and says so rather than manufacturing a pedigree.
- **A market-research report whose method is paywalled**, as evidence of anything but its own
  existence.
- **Any claim that the syndicated market-report industry is systematically wrong.** No academic,
  regulatory, or investigative source establishing that was found. The verified cases above concern
  individual figures. The defensible position is unknown provenance, not known falsehood.
- **A vendor's market-size forecast** as an input to a technical or investment decision.
- **A redistributor of a series** where the upstream publisher documents the method directly.
