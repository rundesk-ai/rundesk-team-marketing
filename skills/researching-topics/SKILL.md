---
name: researching-topics
description: Use when asked to research, investigate, fact-check, find authoritative sources, prepare a cited briefing, or compare or verify claims that require external evidence, whether the question is broad or narrowly focused. It provides a provider-neutral workflow for scoping the question, finding and evaluating relevant evidence, tracing claims to original context, citing precisely, and distilling findings into readable, actionable output. Do not use for repository-only investigation that needs no external evidence.
---

# Research topics

Produce an answer whose important claims can be checked. Research is not a collection of links or a
copy of the documentation; it is a scoped inquiry that turns relevant evidence into a useful result.

## Set the research contract

Before searching, state or infer:

- the question and the decision, task, or audience the answer must serve;
- scope boundaries, definitions, jurisdiction, versions, and time window;
- the required depth and confidence; and
- the deliverable shape and citation style, if one was requested.

Clarify only when a missing choice would materially change the research. Otherwise declare a
reasonable assumption and proceed.

Research is read-only discovery unless the user authorizes more. Do not purchase access, create an
account, contact people, bypass access controls, or upload private material merely to obtain a
source. Report an access or evidence gap instead.

Choose the smallest mode that can answer responsibly:

- **Narrow verification:** establish one claim, value, behavior, or current fact.
- **Broad landscape:** map a topic, its vocabulary, major positions, evidence, and open questions.
- **Rigorous review:** predefine search and selection methods when the user requests systematic,
  reproducible, or high-stakes evidence synthesis.

Read [references/research-modes.md](references/research-modes.md) for mode-specific search and stop
conditions. Do not impose systematic-review ceremony on a simple lookup.

## Search from claims, not conclusions

Break the question into claims or evidence needs. For each one, identify who would create the most
direct evidence and search there first:

1. primary material: specifications, laws, source code, official records, original studies, data,
   release notes, or statements from the responsible organization;
2. independent analysis: peer-reviewed synthesis, regulators, standards bodies, specialist
   reporting, or recognized domain experts; and
3. practitioner evidence: maintainer discussions, postmortems, issue threads, field reports, and
   community examples that expose traps the formal contract may omit.

Search results, snippets, generated summaries, and citations found in another article are leads.
Open the source, locate the supporting passage, inspect its context, and trace secondary claims
upstream before relying on them.

```text
Bad:  search result says the feature is supported -> cite the result snippet
Good: open the versioned feature documentation -> confirm its scope and exceptions -> cite that page

Bad:  three articles repeat one announcement -> call that independent confirmation
Good: trace their lineage -> count the announcement once -> seek an independent test or analysis
```

## Keep an evidence ledger

Record evidence while researching, not after drafting:

```text
Claim | source and stable URL | source type | supporting section | date/version | limits or conflict
```

This may remain working notes unless the user requests the research trail. It prevents source drift,
lost provenance, and citations added later because they merely sound compatible with the prose.

For each candidate source, use lateral reading: leave the page, investigate who produced it, find
better coverage, and trace its claims to original context. Then inspect the source itself for
methods, scope, date, version, conflicts of interest, corrections, and retractions. Authority is
contextual; a famous source outside its domain is not automatically strong evidence.

Read [references/source-evaluation.md](references/source-evaluation.md) when evidence is contested,
high stakes, unfamiliar, empirical, or heavily re-reported.

## Synthesize, then cite

Lead with the answer. Organize the result around the user's question or decision, not around the
order in which sources were opened.

- Separate sourced fact, reasoned inference, recommendation, and unresolved uncertainty.
- Represent material disagreement and explain why evidence differs; do not average incompatible
  claims into false consensus.
- State limits that change how the answer should be used.
- Prefer paraphrase. Quote only when exact wording is itself evidence.
- Put each citation beside the claim it supports and link the most specific stable source available.
- Split compound claims when one source does not establish every part.

```text
Bad:  Source A says..., Source B says..., Source C says...
Good: Finding -> strongest evidence -> disagreement or limit -> implication

Bad:  The tool is faster, safer, and universally supported. [one source about speed]
Good: The benchmark reports lower latency in its tested workload. [benchmark]
      Compatibility is documented for versions X-Y. [versioned documentation]
```

Read [references/citations-and-synthesis.md](references/citations-and-synthesis.md) for output shapes,
claim-level citation traps, and a final evidence audit. Read
[references/sources.md](references/sources.md) to audit or update this package's own lessons.

## Stop with a defensible answer

For a narrow lookup, stop when direct evidence answers the exact claim and material caveats are
known. For broad research, stop when additional credible searches no longer change the major themes
and the important disagreements are represented. For a rigorous review, stop only at the declared
search date and selection protocol.

Before delivery, verify:

- every material factual claim has support at the right scope;
- every cited source was opened and says what the output attributes to it;
- dates, versions, jurisdictions, units, and definitions match;
- mirrors and repeated reporting were not mistaken for independent evidence;
- uncertainty and inaccessible or missing evidence are visible; and
- the result is concise enough to use without rereading the source set.
