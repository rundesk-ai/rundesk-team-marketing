---
name: researching-competitors
description: Use when a question asks who the competitors are, how a rival's business or pricing works, how they position themselves, what their product can actually do, or how offerings compare — including competitive landscapes, alternatives, win-loss context, pricing teardowns, and capability matrices built from public sources. It supplies the filing and registry routes, the difference between a published price and a realized one, the legal bar on comparative claims, and the discipline that keeps a comparison honest. Do not use it for auditing a competitor's website as a serving surface, for first-party analytics, or for writing the comparison page that results.
---

# Researching competitors

A competitor question is nearly always two questions wearing one sentence: what is verifiably true
about this company, and what would we like to be true about them. Your job is the first one, stated so
clearly that the second becomes obvious.

The general research method in `researching-topics` still governs. This skill adds the routes to
records companies are obliged to file, the reason a published price is not a price, the legal standard
their claims and yours must meet, and why most published comparisons are indefensible.

## The boundary that matters most

A competitor is two different objects depending on how you prove a claim about them:

- **Their business** — model, pricing, positioning, funding, scale, roadmap intent. Established by
  citing a record or publication someone else can look up. **That is this skill.**
- **Their serving surface** — what a URL returns, how a page renders, what a feed contains, whether
  they rank. Established by retrieving it, repeatably. **That is search and site retrieval, not this
  skill.**

Reading a competitor's pricing page as one published source is research. Auditing that page's markup,
canonical, indexing, or field performance is not. When a request needs both, say so and treat them as
two pieces of work with different evidence standards.

## Start with what they were obliged to file

Ranked by how hard it is to lie in:

1. **Audited filings** — revenue, segments, named competitors, stated basis of competition, risk
   factors, and subsequent events. A company under obligation to file, signed off by an auditor.
2. **Registry records** — incorporation, directors, officers where the jurisdiction publishes them,
   charges, and confirmation statements. Filed under legal duty and often **not checked for
   accuracy** by the registry.
3. **Statutory notices** — a securities exemption notice states the amount raised. It does **not**
   state a valuation, whatever the press release said.
4. **Their own publications** — pricing pages, docs, changelogs, job postings, engineering blogs.
   Truthful about intent, silent about outcome.
5. **The press and their own announcements** — a claim about the future by an interested party.

`references/filings-and-registries.md` gives the routes, what each disclosure item actually requires,
and the hard limits — including that full-text filing search reaches back only to 2001, that patent
applications publish 18 months after filing and can be withheld entirely, and that US beneficial
ownership reporting no longer applies to US companies.

## A published price is not a price

The revenue-recognition standard says it outright: a contractually stated price or a list price
**may be, but shall not be presumed to be**, the standalone selling price. Vendors estimate the
standalone price from historical discounts off list, and auditors treat that estimate as a matter of
significant judgment — which is direct evidence that the gap between list and realized is large and
variable.

So a pricing page establishes the **published offer**, its packaging, and its metering. It does not
establish what anyone paid. `references/pricing-and-claims.md` covers where filings disclose the
price-versus-volume split, and what published pricing structures can and cannot tell you.

## Their claims — and yours — have a legal standard

Comparative advertising is encouraged, not discouraged: policy in this area encourages naming or
referring to competitors, but requires clarity and, where necessary, disclosure to avoid deception,
and it is described as a source of important information that assists rational purchase decisions.
Disparaging advertising is permissible so long as it is truthful and not deceptive.

Two consequences most teams get backwards:

- **A comparative claim is held to the same substantiation bar as any other objective claim**, not a
  higher one. Imposing a higher bar on comparative claims is treated as inappropriate.
- **A superlative like "#1" is not puffery.** The self-regulatory position is that while being best is
  a matter of opinion, *how many people hold that opinion* is provable — so the claim carries a real
  substantiation burden, and a broad-category "#1" is expected to compare against most of the
  relevant marketplace.

Never repeat a competitor's unsubstantiated superlative as a fact about them. Report it as a claim
they make, and note whether they published a basis.

## Reviews tell you sentiment, never capability

The endorsement rules are explicit that consumer endorsements **are not competent and reliable
scientific evidence**. A star rating is not a capability finding, and a rating gap is not a quality
gap.

`references/review-platforms.md` carries what each platform documents about how it solicits, labels,
and monetizes reviews — including that **G2, Capterra, GetApp and Software Advice are now one
company**, so agreement between them is not independent corroboration.

## Comparisons fail in known, named ways

The systems-security literature surveyed 50 papers in top venues against a list of 22 "benchmarking
crimes" and found tier-1 papers committed an average of five, with a single paper committing none.
Published vendor comparisons are not more careful than that. The three failures that matter here:

- **Selective criteria** — choosing the axes on which you win. Described as the mother of all
  benchmarking crimes.
- **Testing a rival's product yourself, badly** — running someone else's system sub-optimally and
  comparing against it. In research this is called probable misconduct; in marketing it is called a
  comparison page.
- **Stale baselines and missing version, date, and configuration.**

State every claim's tier: **documented by the vendor**, **available and inspected**, or
**independently reproduced**. `references/comparison-discipline.md` gives the vocabulary and the
checks.

## Return

```text
Competitor: Example Inc.
Business:   $X revenue FY2025, two segments, names us among competitors in Item 1
            [10-K filed 2026-02-11]
Pricing:    published tiers $29/$79/seat-metered; enterprise "contact us"
            [pricing page retrieved 2026-08-25]. Realized price unknown -- list is
            not presumed to be standalone selling price.
Positioning: claims "#1 for teams". No basis published. Recorded as their claim.
Capability:  SSO documented by vendor; not inspected. Bulk import inspected in trial
            2026-08-20, version 4.2. Migration tooling: not established.
Cannot establish: churn, realized ACV, roadmap dates, or why they chose this packaging.
```

Read [filings and registries](references/filings-and-registries.md) for the record routes,
[pricing and claims](references/pricing-and-claims.md) before repeating any price or superlative,
[review platforms](references/review-platforms.md) before citing a rating, [comparison
discipline](references/comparison-discipline.md) before building a matrix, [public
signals](references/public-signals.md) for hiring, infrastructure, and changelog inference, and
[sources](references/sources.md) to audit any claim above. Use
[validation](references/validation.md) when testing this skill's activation and boundaries.
