---
name: writing-prds
description: Use when asked to create, revise, review, or validate a product requirements document (PRD), product brief, feature definition, or product requirement set from user or stakeholder direction. It supplies a provider-neutral workflow for preserving product intent, grounding the problem and solution in evidence, defining concise user-visible requirements and success measures, resolving contradictions without guessing, and checking the implemented product against the approved requirements. Do not use for technical design, implementation plans, or documentation of current code behavior alone.
---

# Write product requirements

Turn the user's direction into a product contract that a non-technical reader can understand and a
delivery team can verify. Preserve what was requested; never manufacture the reason, audience,
priority, or evidence behind it.

## Establish authority and scope

Identify the product or increment, document owner, decision-maker, target reader, current status,
and requested outcome. Use the destination the user names, then an existing product-document
convention, then an established shared documentation area; otherwise return the PRD in the response.
Do not invent a repository directory.

For an existing product, read
[references/lifecycle-and-validation.md](references/lifecycle-and-validation.md) before describing
the current state or reconciling the request with code and tests.

Create a working direction ledger:

```text
Direction or claim | source | decision / evidence / assumption | PRD section | conflict or gap
```

Treat explicit user decisions as product authority. Treat user suggestions, research findings,
analytics, current behavior, and practitioner guidance according to what they actually establish.
Do not relabel a requested feature as a proven user need or cite general best practice as the user's
intent.

## Resolve contradictions before hiding them

Never merge conflicting product directions into plausible prose or let current code silently redefine
the desired product. The lifecycle reference owns the conflict, current-state, feasibility, decision,
and change workflow. Continue with unaffected sections while a material product choice is unresolved.

## Write the smallest decision-ready PRD

Use the repository's template when one exists. Otherwise use only the applicable parts of this shape:

```markdown
# <Product outcome or increment>

**Status:** <draft / approved / local equivalent>
**Owner:** <person or role>
**Last updated:** <date>

## Problem and evidence
<Target user, situation, obstacle, consequence, and source of each material claim.>

## Outcome and success
<User or business change sought; baseline, measure, target, window, and evidence plan when known.>

## Product solution
<The intended experience and product boundaries in plain language.>

## Requirements
| ID | User-visible behavior or product condition | Priority | Acceptance evidence |

## Scope
**In:** <release boundary>
**Out:** <nearest tempting expansions>

## Assumptions, risks, and open decisions
| Item | Impact | Owner | Evidence or decision needed |

## Validation
| Requirement or outcome | Evidence | Result | Last checked |
```

Angle-bracket text is a drafting prompt, never product fact. Omit empty sections rather than filling
them with boilerplate. Keep the problem, outcome, and solution scannable; link research, design,
technical decisions, work items, and detailed evidence instead of copying them.

Read [references/product-shape.md](references/product-shape.md) when turning mixed notes, feature
requests, research, or stakeholder input into the problem, outcome, solution, scope, and evidence.

## Make each requirement observable

Read [references/requirements-and-acceptance.md](references/requirements-and-acceptance.md) when
defining functional behavior, product qualities, edge cases, priority, or acceptance evidence. It
owns the requirement form, product-versus-implementation boundary, quality coverage, and distinction
between feature acceptance, delivery quality, and product success.

## Keep the PRD true through delivery

Use the lifecycle reference when revising an approved PRD or validating an implementation or released
outcome. It owns decision history, proportional traceability, executed delivery evidence, mismatch
handling, and post-release outcome validation. Link execution trackers and technical designs instead
of turning the PRD into either.

Read [references/sources.md](references/sources.md) when auditing or changing a lesson in this package.

Before delivery, confirm every user direction is represented or explicitly out of scope, every
material claim has the right kind of support, contradictions are resolved or visible, requirements
are observable without prescribing hidden implementation, and validation claims name the evidence
actually checked.
