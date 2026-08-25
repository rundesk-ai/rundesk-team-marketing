---
name: researching-customers
description: Use when a question asks who the customers or audience are, how they are segmented, what they need, believe, or complain about, why they choose or reject a product, or what jobs they are trying to get done — and when designing or reviewing a survey, interview guide, or other primary research about people. It supplies the bias structure of published customer evidence, question and sample design that survives scrutiny, and the honest provenance of segmentation and jobs-to-be-done frameworks. Do not use it for first-party product analytics, for contacting people without authority, or for writing the messaging that results.
---

# Researching customers

What people do, what people say, and what a framework says about people are three different kinds of
evidence. Most bad customer research collapses them, then presents the result with more confidence
than any of the three would carry alone.

The general research method in `researching-topics` still governs. This skill adds what that method
cannot know: how customer evidence is selected before you ever see it, what question wording does to
an answer, and which popular frameworks have evidence behind them.

## Start from what already exists

Published customer evidence is free, immediate, and systematically biased. Use it first, and name the
bias in the same breath:

- **Reviews and ratings** — biased twice over, by who buys and by who bothers to write.
- **Forums, communities, and social threads** — dominated by a small, atypical minority of
  participants.
- **Support tickets and sales-call notes** — your own customers only, filtered by who complains.
- **Public filings, help centres, changelogs, and job postings** — what a company says about its
  customers, which is a claim rather than an observation.

`references/published-voc.md` gives the mechanisms and the size of each effect. The one-line version:
**a rating average is not a quality estimate, and a forum thread is not a population.**

## Ask people only when you are authorized to

Contacting customers is an external effect. It requires explicit authority, and it requires keeping
research separate from selling. The industry code is unambiguous: a data subject must be told about
any non-research purpose before collection begins, and **separate consent must be obtained for
non-research purposes.** Recruiting from a customer list for "research" that feeds a sales sequence
breaks that line.

Before designing anything, settle: who is being contacted, on what basis, what they will be told, what
happens to their data, how long it is kept, and how they withdraw. `references/asking-people.md`
carries the design and consent requirements.

## Design the question before you worry about the sample

Question wording changes answers more than most people believe, and the effect is measured, not
theoretical. Support for military action ran 68% in one split and 43% in the other when the second
version named the possibility of thousands of casualties. Naming "the economy" as a closed option got
58%; leaving it open got 35%. A logically equivalent forbid-or-allow pair produces different
marginals for the same underlying opinion.

So:

- **Write the exact wording down and report it with the result.** A finding without its question text
  is not reviewable.
- **Ask about behaviour and specifics, not preference and hypotheticals.** "What did you do the last
  time this happened" beats "would you use a feature that".
- **Do not build an instrument that argues.** A questionnaire that only offers negative framings of
  one option and conceals who is asking is a persuasion tool wearing a survey's clothes, whatever it
  is called internally.
- Expect **acquiescence** — a tendency to agree with a statement, stronger among less informed
  respondents — and **social desirability**, where respondents understate the unflattering and
  overstate the creditable.

## Be honest about how much a sample supports

- **Qualitative work saturates early and narrowly.** A systematic review of studies that tested it
  empirically found saturation reached within 9-17 interviews or 4-8 focus groups — and specifically
  in homogeneous populations with narrowly defined objectives. Diverse populations and questions about
  meaning rather than themes need more.
- **A small-n finding establishes that something exists, and its mechanism.** It does not establish
  prevalence. "Six of nine interviewees hit this" is a real finding about nine people.
- **Non-probability online panels carry roughly twice the error** of probability-based panels, and
  the error concentrates in exactly the subgroups people most want to read. A share of respondents in
  opt-in panels answer without effort and skew positive, so they bias results rather than adding
  noise.
- **Matching demographics does not fix it.** A representative demographic profile does not predict
  accuracy. Quota-matching an opt-in sample buys the appearance of representativeness, not the thing.

Report the sample as it is: how recruited, how many, over what period, and what it cannot support.

## Treat segments, personas, and jobs as hypotheses

These are useful thinking tools with weaker provenance than their popularity implies, and
`references/segments-and-jobs.md` states each one's actual standing.

- **Jobs-to-be-done** is an influential practitioner framework, not a validated method. No
  peer-reviewed evaluation of it was found. Its most famous case study was a single day of
  observation in one restaurant with an unstated number of interviews. Use the lens; do not cite it
  as evidence.
- **Personas** cannot be verified or falsified, and the specificity that makes them feel real is what
  makes them unrepresentative. Without multivariate data nobody has, you cannot know whether a
  persona describes a million people or none.
- **Needs-based segmentation** has a longer pedigree than demographic segmentation and a live
  practitioner critique that both have become weak predictors of purchasing behaviour.

A segment is a claim that a group exists, behaves differently, and can be reached. Say which of the
three you have evidence for.

## Return

Separate what was observed, what was said, and what you inferred.

```text
Question: why do investors abandon setup before importing a list?
Observed (published): 11 of 40 reviews mentioning setup name list import; all 11 rate 1-2 stars.
                      [reviews, platform X, retrieved 2026-08-25]
Said (interviews):    6 of 9 interviewees described giving up at field mapping. [n=9, recruited
                      from churned trials, Aug 2026, question text attached]
Inferred:             field mapping is a likely abandonment cause. Directional.
Cannot establish:     prevalence. Reviews self-select toward extremes and 9 interviews establish
                      the mechanism, not its frequency. First-party funnel data would settle it.
```

Read [published voice of customer](references/published-voc.md) before treating reviews or forums as
evidence, [asking people](references/asking-people.md) before designing a survey or interview,
[segments and jobs](references/segments-and-jobs.md) before using a framework, and
[sources](references/sources.md) to audit any claim above. Use
[validation](references/validation.md) when testing this skill's activation and boundaries.
