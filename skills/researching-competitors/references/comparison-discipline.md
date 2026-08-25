# Building a comparison that survives being checked

## The failure modes are catalogued, and the base rate is bad

A peer-reviewed survey of systems-security evaluation identified **22 "benchmarking crimes"** and
audited 50 papers published in top venues against them. Tier-1 papers committed **an average of five**,
and the survey found **a single paper** in its sample that committed none.

That is the base rate among people writing for peer review, with reviewers and reputations at stake.
A vendor comparison page is not held to a higher standard. Assume any published comparison — including
one you are asked to reproduce — contains several of these until you have checked.

## The three that ruin competitive comparisons

**Selective criteria.** Described as the mother of all benchmarking crimes: using a biased set of
benchmarks to seemingly prove a point that broader coverage would contradict. The tell is language
like "we picked a representative subset" or "typical results are shown" — the subset is usually the
one that looked most favourable.

For a capability matrix this means: **choose the axes before you know who wins.** Write the criteria
list from the buyer's decision, get it agreed, and then fill it in. Criteria selected after seeing the
results is the single most common way an honest-looking matrix lies.

**Testing a rival's product yourself, badly.** The literature is blunt: doing benchmarks on
competitors is tricky and you must go out of your way not to treat them unfairly. You tuned your own
system as well as you could — did you make the same effort with theirs? Running someone else's system
sub-optimally and comparing against it is called highly unethical and probably scientific misconduct.
The remedy given is to **describe fully what you did with the competitor system**, including all
configuration, so a reader can judge fairness. And: be particularly circumspect when your results do
not match any published data about the competitor, and consider contacting them to confirm your
measurements are fair.

There is a worked case in the literature of a system being benchmarked with the open-source release's
default **debugging build** left enabled. The number was real. The comparison was worthless.

**Stale baselines and missing specification.** Where a newer result established the state of the art,
that is the baseline that must be used. The evaluation platform must be specified including anything
that could influence results, and **complete results should be given rather than ratios** — a ratio
can conceal that a result is very bad or entirely irrelevant.

## State the evidence tier for every cell

Research-artifact badging gives a usable three-tier vocabulary. Adapted:

| Tier | Means | Effort to establish |
|---|---|---|
| **Documented by vendor** | The vendor's own documentation says the capability exists | Read the page. Record the URL and date |
| **Available and inspected** | You saw it — in a trial, a sandbox, a demo, a public artifact | You looked but did not measure. Record version and date |
| **Independently reproduced** | You ran it and got the result yourself | Record configuration, version, date, and method |

The badging scheme's own distinction is instructive: the lower tier requires only that materials be
available and looked at, expected to take a very few hours, while reproduction requires actually
executing. **Do not let a documented claim sit in the same column as a reproduced one.** A matrix
where every cell is a checkmark has erased the only information that mattered.

Where a capability is genuinely unknown, write **not established**. An empty cell reads as absence and
absence is a claim.

## Version, date, and configuration are part of the claim

A comparison without them is unfalsifiable, which means it is also undefendable. Record for each
product:

- The **version or release** evaluated, and the plan or tier it was on.
- The **date** of evaluation. Published pricing and packaging change fast, and pricing configuration
  space grows exponentially with add-ons.
- The **configuration**, including anything you changed from default and anything you left at default
  that a knowledgeable user would change.
- Whether the account was a **trial, sandbox, or paid** instance, since gating differs.

## What a changelog claims, and does not

Version numbers only mean something where the project says it follows a versioning convention. The
common convention defines a major bump as incompatible changes, a minor as backward-compatible
functionality, and a patch as backward-compatible fixes. Changelog convention exists too, and its
guidance is memorable: do not dump git logs into changelogs.

Both are **conventions a vendor opts into**. A version bump is evidence of compatibility *intent*
only where adherence is stated. Release cadence tells you about a team's process, not about product
quality, and never about roadmap dates.

## The output contract

A defensible comparison states: the criteria and when they were fixed; each product's version, tier,
date, and configuration; each cell's evidence tier; what could not be established; and who chose the
criteria. If your comparison would embarrass you when the competitor read it, the problem is in one of
those lines.

**A last check before you hand it over.** Ask what a well-informed engineer at the competitor would
say about your matrix. If the answer is "they configured us wrong" or "they picked the four things
they win", you have the wrong artifact — and, since a comparison naming a rival on objectively
measurable attributes is a comparative claim, you also have a substantiation problem. See
`pricing-and-claims.md`.
