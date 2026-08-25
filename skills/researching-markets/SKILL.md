---
name: researching-markets
description: Use when a question asks how large a market or category is, whether demand is growing or shrinking, what a segment is worth, or what share is realistically available — including total addressable market, TAM, SAM, SOM, category demand, adoption, and market trend. It supplies a bottom-up method built on counted public data, the discipline for reporting a range with stated assumptions, and the provenance traps that make published market figures unreliable. Do not use it for first-party analytics or a company's own forecast, for auditing a website, or for a general research question with no size or demand component.
---

# Researching markets

A market size is an estimate, not a fact. Your job is to produce one whose arithmetic someone else
can redo, disagree with, and move — not to find a number and cite whoever printed it.

The general research method in `researching-topics` still governs: claim-level sourcing, an evidence
ledger, and lateral reading. This skill adds what that method cannot know — where counted data on
commerce actually lives, why published market figures are usually worthless, and how to combine
imperfect inputs without inventing precision.

## Define the market before you size it

Most disagreement about a market's size is undisclosed disagreement about its boundary. Settle these
first and write them into the answer:

- **Who buys** — the population of buyers, and whether it is businesses, consumers, or both.
- **What they buy** — the product boundary, including what is deliberately excluded.
- **Where** — the geography, named to the level the data supports.
- **When** — the period, and whether the figure is annual revenue, units, or buyers.
- **At what price level** — list, realized, or gross merchandise value. These differ by a lot.

Two competent analysts put Uber's addressable market 25× apart while using the same framework, and
the disagreement was entirely about boundary and share, not arithmetic
(`references/sizing-and-uncertainty.md`). If you skip this step, your number is not comparable to any
other number, including a later one of your own.

## Prefer counted to claimed

Rank evidence by whether somebody counted it:

1. **Counted** — a statistical agency's census or survey of establishments, employment, or sales; a
   filer's audited revenue. Comes with a documented method, a stated period, and known exclusions.
2. **Reported** — a company's own disclosure about its market, a trade body's tally, a platform's
   index of its own activity. Real data, interested party, undocumented method.
3. **Claimed** — a market-research firm's headline figure in a press release, with the report
   itself paywalled. Treat as an assertion of unknown provenance until you can open the method.

`references/public-data.md` names the counted sources, what each publishes, at what granularity, with
what lag, and — the part that decides whether you can use it — what each one excludes.

**A claimed figure is not evidence, and repetition is not corroboration.** Ten outlets carrying one
press release is one source. `references/vendor-reports.md` shows what this looks like in the wild,
including the same market valued at $467 billion and $1,811.75 billion for the same year.

## Size bottom-up, and show the arithmetic

Build the number from quantities somebody counted:

```text
buyers in scope  ×  purchase rate  ×  price  =  market size
```

Each factor is either counted, or an assumption you state and label. Then:

- **Write every assumption down with its source and its effect.** An assumptions log is the
  deliverable, not a working note — a reader must be able to change one input and see the answer move.
- **Cross-check with a second, independent method** before believing your own result. A top-down
  figure derived from a broader counted total is a legitimate check on a bottom-up build, and
  reconciling the two is where you learn something. Examine the difference; never average it away.
- **Report a range.** A single number implies a precision the inputs cannot support.

Never combine two sources that copied one another — that double-counts confidence rather than adding
evidence, and it is the most common way a market estimate becomes falsely certain.

## Say what kind of number you produced

| Label it | When |
|---|---|
| Counted | Every input came from a statistical or audited source at the stated scope |
| Estimated | Counted inputs plus stated assumptions, reported as a range |
| Bounded | You can establish a ceiling or floor but not a value |
| Unestablished | The boundary or the data does not exist, and you say which |

**Unestablished is a legitimate answer and often the correct one.** A question about a narrow product
category in one country in the current year frequently has no counted data at all. Returning the
bound plus what would close it beats returning a number that will be quoted back to you in a board
deck.

## TAM, SAM, and SOM are conventions, not standards

No standards body, regulator, or foundational paper defines them. They are venture-capital and
textbook convention. Use the vocabulary when the requester does, define each one in the answer, and
do not let the framework imply a rigor it has never had. "Total addressable market" appears in
hundreds of annual reports, and in every one of them the company defining its own market is an
interested party.

## Demand is a different question from size

"Is this growing?" is answerable when a series exists; it is not answerable from a size estimate.
`references/demand-signals.md` covers what search interest, job postings, patent filings, and public
filings can and cannot establish. The short version: **share-of-search is not volume, a vendor's
index of its own platform is not the market, and an instrument its owner keeps re-tuning does not
produce a comparable multi-year series.**

## Return

State the boundary, then the number, then how you got it.

```text
Market: US direct-to-consumer art prints, annual retail revenue, 2024
Estimate: $310M-$520M (estimated; range reflects the two assumptions below)
Built from: Census e-commerce retail sales for NAICS 4541 [counted, 2024]
            x share attributable to art prints [assumed 0.6%-1.0%, no counted source]
Assumptions: (1) NAICS 4541 includes non-art sellers, so the share is judged, not measured.
             (2) Excludes marketplace GMV where the seller is not US-based.
Cross-check: bottom-up from establishment counts gives $280M-$490M. Difference is
             marketplace treatment, not method.
Cannot establish: unit volume, or any split by price tier. No counted source publishes it.
```

Read [sizing and uncertainty](references/sizing-and-uncertainty.md) for method and range discipline,
[public data](references/public-data.md) for the counted sources, [vendor
reports](references/vendor-reports.md) before citing any published market figure, [demand
signals](references/demand-signals.md) for trend questions, and
[sources](references/sources.md) to audit any claim above. Use
[validation](references/validation.md) when testing this skill's activation and boundaries.
