# Where counted data on commerce actually lives

Every source here publishes a documented method, a stated period, and named exclusions. The
exclusions decide whether you can use it, so they are listed first-class rather than as footnotes.

## United States

| Source | Publishes | Granularity | Lag |
|---|---|---|---|
| Economic Census | Establishments, employment, payroll, and output | ~950 industries, ~21,000 geographies | Every 5 years, years ending 2 or 7 |
| County Business Patterns | Establishments, employment, payroll | To ZIP code and detailed industry | Annual, published since 1964 |
| Annual Integrated Economic Survey | Annual business statistics | By industry | Annual |
| Quarterly e-commerce retail sales | E-commerce and total retail sales | National, with sampling error stated | Quarterly |
| BLS QCEW | Employment and wages | 6-digit industry, county and state | Within 6 months of quarter end |

**What each one leaves out, and it matters more than what it includes:**

- The **Economic Census** covers only establishments that have paid employees. A category dominated
  by sole proprietors — artists, consultants, single-operator shops — is largely invisible in it.
- **County Business Patterns** excludes crop and animal production, rail transportation, the Postal
  Service, most government establishments, and the self-employed without employees. Small cells are
  protected by noise infusion, so a narrow geography-by-industry cell is deliberately imprecise.
- **QCEW** covers more than 95% of US jobs but excludes proprietors, the unincorporated
  self-employed, unpaid family members, and some farm and domestic workers. As of the second quarter
  of 2025 it publishes metropolitan-area data as totals only, so metro-by-industry sizing no longer
  works from it.
- The **Annual Retail Trade Survey is retired.** It was folded into the Annual Integrated Economic
  Survey, which consolidated seven annual business surveys. Guidance that tells you to pull ARTS is
  out of date; check what the current program publishes before assuming a series continues.

**The quarterly e-commerce release is the model for how to report a number.** It states its sampling
error inline — an increase of a given percent plus or minus a stated tolerance. Carry your own ranges
the same way.

## Industry codes are not markets

Industry classification is **production-oriented**: it groups establishments by the activity they are
primarily engaged in, not by who buys the output. A code rarely equals a market, and a business
selling into three markets sits in one code.

Two consequences for a multi-year series:

- The classification is periodically revised, and the revisions **create time series breaks**. Every
  sector has been restructured and redefined at some point. A ten-year line built across a revision
  is not one series.
- An establishment is classified by its primary activity, so revenue from secondary activities lands
  under the wrong heading.

Use a code to find a ceiling and a denominator. Do not present it as the market.

## Europe and the United Kingdom

- **Eurostat structural business statistics** covers the business economy — industry, construction,
  and many services — publishing enterprise counts, turnover, value added, and persons employed,
  available at several hundred economic activities. Employment is head counts, not full-time
  equivalents, so it is not a labour-cost denominator.
- The **UK Annual Business Survey** covers the non-financial business economy, roughly two thirds of
  the UK economy — financial services are absent. Nationally it reaches four-digit industry class;
  regionally only two-digit division.

The ABS documentation states the trade-off every sizing exercise runs into: it is a sample survey, so
more detailed breakdowns result in reduced statistical quality. **Precision and granularity trade
off against each other.** An analyst who drills into a narrow regional cell has bought noise and
should say so.

## Company filings as a ceiling

Full-text search of electronic filings reaches back to 2001 and no further, so a pre-2001 question
needs a different route.

What a filing gives you:

- **Audited revenue** for the entity, at the segment level the entity chose.
- **Segment structure** that follows internal management reporting, not any industry taxonomy.
- Occasionally the company's own market claim — hundreds of annual reports use the phrase "total
  addressable market", which makes it real disclosure language and also an interested party's
  estimate.

What it does not give you. Segments follow how management runs the business, so a company with
hundreds of billions in revenue can resolve to three segments — enough to bound a market from above,
never enough to resolve a product line. And the standard-setter's own post-implementation review of
the segment standard records the complaint directly: respondents were concerned that segments are not
comparable across entities even within the same industry, and the board's response was that
comparability can rarely be achieved however segmentation is defined, because the components of
different businesses are not identical.

**So: a filing bounds a market. It does not let you compare two companies' slices of one.**

## Choosing between them

- Need a **denominator** — how many buyers, establishments, or employees exist: establishment and
  employment programs.
- Need a **revenue total** for a broad category: the e-commerce and retail series, or filings.
- Need a **narrow product category**: usually nothing counted exists. Say so, give the bound from the
  nearest counted total, and name the assumption that would close the gap.
