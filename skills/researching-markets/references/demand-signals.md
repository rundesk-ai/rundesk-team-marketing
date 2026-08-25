# Trend and demand signals, and what each can establish

"Is this growing?" is a different question from "how big is this?" It needs a series, and the series
has to mean the same thing at both ends.

## Search interest

Search-trend data is **share of search, never volume.** Each data point is divided by the total
searches for the geography and period it represents, then scaled to a 0-100 range against the topic's
proportion of all searches. Two regions showing the same interest do not have the same underlying
volume.

Documented exclusions to know before reading a line as demand:

- Searches made by very few people are returned as zero, not as a small number.
- Duplicate searches by one person over a short period are removed.
- Queries with apostrophes and other special characters are dropped.
- Internal searches made by AI answer surfaces are excluded, which changes what the series counts as
  the way people search changes.
- The output sometimes reflects statistical noise rather than actual interest, especially at low
  volume.

The publisher's own disclaimer is the one to quote to a stakeholder: it is not a scientific poll and
should not be confused with polling data.

**Can establish:** the relative direction of attention within one geography and timeframe; that one
term is searched more than another in the same place and period.
**Cannot establish:** absolute demand, market size, revenue, or magnitude compared across regions.

### Why a long search series is not a measurement series

The instructive failure is a widely praised flu-prediction model built on search data. At its worst
it predicted more than double the proportion of doctor visits that public-health surveillance
recorded, and it ran high for 100 out of 108 consecutive weeks.

The published post-mortem named two traps that apply directly here:

- **Big data hubris** — the implicit assumption that a large incidental dataset substitutes for,
  rather than supplements, purpose-built data collection.
- **Algorithm dynamics** — the instrument is continuously changed by its owner to improve the
  commercial service, and by users in how they use it.

The underlying point is that most large datasets receiving popular attention are not the output of
instruments designed to produce valid, reliable, scientifically usable data. Search interest is a
by-product of a product that is re-tuned constantly. **Treat a multi-year line as a sequence of
differently calibrated instruments, not one series.**

## Hiring activity

A job-postings index built on one platform's own data can indicate direction of hiring intent in a
category. The credible ones are transparent about being indexed to a baseline date, seasonally
adjusted per series, and smoothed over a trailing window.

Read the publisher's own limits first. A well-documented index states that its numbers are provided
for information only and should not be viewed as an indicator of the platform's own performance, that
methodologies may change to preserve reliability and representativeness, and that historical numbers
have been revised and may differ from previously reported values.

**Can establish:** direction and rough magnitude of hiring intent for a role or category, on that
platform. **Cannot establish:** total labour demand, revenue, or anything about hiring that does not
pass through that platform. It is a vendor's index of its own marketplace, with a documented history
of revision.

## Patent filings

Patent counts are publicly available in long time series for most countries, which makes them
tempting. Their documented drawbacks are severe:

- **Not all inventions are patented.** Firms can prefer secrecy or rely on other routes to market
  position.
- **Propensity to file differs sharply by technical field.** In some industries a patented invention
  is surrounded by applications covering incremental variations, specifically to deter entrants and
  improve cross-licensing position. Fields subject to this produce far larger counts for reasons
  unrelated to invention.
- **Value is highly skewed.** Many patents have no industrial application; a few carry very high
  value. Simple counts are therefore misleading.
- Publication generally occurs only 18 months after first filing, which is a hard recency floor.

**Can establish:** that firms are investing effort in a technical area, as of 18 months ago.
**Cannot establish:** demand, revenue, market size, or value. Counts are strategic behaviour and are
not comparable across fields.

## The two checkable growth proxies

When a trend claim has to hold up, prefer:

- **An official employment or sales series** for the industry, read with its exclusions and its
  classification-revision breaks in mind.
- **Segment revenue trend in company filings** for the firms that dominate a category — audited,
  periodic, and comparable to itself over time even though it is not comparable across filers.

Both are slower and narrower than a search line. Both mean the same thing at both ends of the series,
which is the property that makes a trend claim defensible.

## The honest summary for a stakeholder

Attention signals are fast, free, directional, and unstable. Counted series are slow, coarse, and
comparable. A trend claim built only on attention signals should be labelled directional and paired
with the counted series that would settle it — which is the same discipline this catalog applies to
suggestive evidence everywhere else.
