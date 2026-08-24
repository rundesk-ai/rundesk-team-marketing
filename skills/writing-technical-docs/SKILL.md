---
name: writing-technical-docs
description: Use when asked to create, revise, or audit technical documentation for an existing codebase, including developer or consumer guides, API or CLI references, how-it-works explanations, architecture notes, troubleshooting, extension guides, and maintainer documentation. It supplies a provider- and language-neutral workflow for tracing claims to current contracts, code, configuration, tests, and real usage; writing verified examples and failure paths; and keeping one human- and agent-readable source from drifting. Do not use for implementation plans, code comments alone, or speculative designs for software that does not exist.
---

# Write technical documentation

Document the system that exists. Make every material statement traceable, every example honest, and
every page useful to someone trying to use, understand, extend, or maintain the code.

## Define the documentation contract

Before drafting, identify:

- the audience: consumer, integrator, operator, contributor, maintainer, or agent;
- the task or question the document must answer;
- the software version, environment, and boundaries in scope;
- the existing documentation home, style, build, and canonical source; and
- whether the page is a tutorial, how-to, reference, explanation, or troubleshooting guide.

Do not create a new documentation location when the repository already has one. Read
[references/documentation-types.md](references/documentation-types.md) when choosing the page type,
audience path, or document shape. Keep learning, task execution, factual lookup, and explanation
distinct enough that a reader can enter at the needed goal.

## Build evidence before prose

Trace from the public entry point inward. Use the strongest available evidence for each claim:

1. versioned public contracts, schemas, interfaces, help output, and supported configuration;
2. current implementation and wiring for mechanics, conditions, and side effects;
3. executed focused or integration tests and safe reproductions for the exact cases they exercise;
4. real consumer call sites and fixtures for representative usage shapes, not runtime proof; and
5. current decision records or named maintainer evidence for rationale.

Keep a working ledger:

```text
Claim | audience/page | contract or implementation | behavior verification | usage evidence | limits
```

A passing test proves its covered case, not a broader prose claim. Source shape does not prove
intent, and old design documents do not prove current behavior. When contracts, implementation, and
tests disagree, expose the conflict and narrow or defer the statement; never blend them into a
plausible story.

```text
Bad:  “The worker retries every failed job.” The repository merely contains a retry helper.
Good: Trace the caller, retry condition, configuration, and focused tests; document that bounded
      behavior, or say the retry policy could not be established.
```

Read [references/evidence-and-verification.md](references/evidence-and-verification.md) when the
codebase is unfamiliar, behavior crosses components, tests conflict with code, or claims need a
repeatable verification trail.

## Write the shortest useful path

Lead with purpose, audience, prerequisites, and the simplest supported outcome. For a task, give
numbered actions and the expected observation after meaningful steps. Follow with relevant failure
and recovery paths; do not bury the successful path under internals.

For understanding and maintenance, name responsibilities, boundaries, runtime flow, state changes,
failure behavior, extension points, and invariants. Link to stable files and symbols when repository
readers need to continue into code. Do not narrate every directory or infer why a design exists.

Use descriptive headings and links, defined terms, direct language, and correctly tagged code
blocks. Put one main question or task under each heading. Give diagrams titles, scope, labeled
relationships, legends, and an equivalent text explanation; never make a screenshot or diagram the
only carrier of a contract.

Humans and agents should reach the same canonical technical truth. Keep agent instruction files to
short routing and workflow constraints; do not copy the full documentation into provider-specific
files.

- Read [references/apis-and-examples.md](references/apis-and-examples.md) for HTTP or library APIs,
  CLIs, configuration, events, schemas, generated reference, errors, and runnable examples.
- Read [references/architecture-and-maintenance.md](references/architecture-and-maintenance.md) for
  how-it-works, architecture, runtime flows, extension points, diagrams, troubleshooting, and drift.

## Verify the deliverable

Use the repository's documentation checks and the real product surface:

1. Recheck every material statement against the evidence ledger.
2. Run the named focused behavior and integration tests or a safe reproduction. If that proof cannot
   run, mark the claim unverified and narrow the documentation.
3. Run copyable commands and examples in the documented environment when safe; record the result.
4. Confirm expected output, errors, defaults, constraints, versions, and links.
5. Build or render the docs, then run available lint, link, schema, and example checks.
6. Read once as the target audience: can they complete the task or find the contract without hidden
   context?
7. Name checks not run, unsupported environments, and unresolved evidence gaps.

```text
Bad:  `$ tool create [--force] <name>` presented as a command users can paste.
Good: `$ tool create example` as one verified path; document optional flags in reference and mark
      placeholders explicitly.

Bad:  “Documentation updated; tests pass.”
Good: Name the example or claim, exact check, observed result, and limits of that proof.
```

Keep documentation changes with the behavior they describe. Prefer contract-derived reference and
executable examples when the repository supports them, but review generated output for consumer
context, navigation, and failure guidance. Remove known-wrong material; a visible gap is safer than
confidently stale instructions.

Read [references/sources.md](references/sources.md) when auditing, challenging, or changing a lesson
in this package.
