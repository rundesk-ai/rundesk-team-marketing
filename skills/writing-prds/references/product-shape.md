# Shape the product before listing features

Use this reference when the input mixes requests, observations, research, constraints, and possible
solutions.

## Preserve the source of direction

Classify each input before synthesizing it:

| Input | Preserve as | Do not turn it into |
|---|---|---|
| Explicit user or decision-maker direction | Approved intent, constraint, or requested solution | Independent customer evidence |
| User/customer observation or research | Evidence with population, context, date, and limits | A universal need |
| Analytics or operational data | Measured behavior with definition, baseline, and window | A causal explanation |
| Existing product or code | Current-state evidence | The desired future state |
| Team or stakeholder idea | Proposal or assumption | A mandatory requirement |
| Law, policy, contract, or platform boundary | Cited external constraint | An unexplained preference |

Do not invent personas to make a feature sound user-centred. If the user supplied only a target role,
use that role. If no target user is known, keep it as an open product decision.

## Connect problem, outcome, and solution

Write the chain in this order:

```text
target user and context -> obstacle or unmet job -> consequence -> desired outcome
                         -> proposed product solution -> observable requirements
```

The problem should make the present failure understandable without assuming the proposed feature.
The outcome should describe the beneficial change, not merely the shipped output. The solution should
make the intended product experience concrete enough to judge against the problem while leaving
implementation choices open.

```text
Bad:  Problem — We do not have a dashboard. Outcome — Launch a dashboard.
Good: Problem — <target user> cannot <job> in <context>, causing <supported consequence>.
      Solution — <requested product experience>. Outcome — <observable beneficial change>.
```

Angle-bracket text is a template. Replace it only with user direction or cited evidence.

## Bound one coherent increment

State the smallest release or increment that can deliver and test the intended value. Put the nearest
tempting expansions under **Out of scope** so silence is not mistaken for inclusion. Keep deferred
ideas separate from committed requirements.

Identify dependencies and constraints only when they affect product scope, timing, eligibility, or
experience. Link detailed architecture and delivery sequencing elsewhere.

Use priority labels only when their meaning and authority are established. Do not invent `must` or
`P0` because a requirement appears important. Every in-scope requirement should trace to the stated
problem, outcome, explicit constraint, or user decision; cut attractive features with no such owner.

## Keep evidence proportional

A small, reversible increment may need a short problem statement, explicit direction, acceptance
evidence, and one success signal. Higher-risk, regulated, costly, irreversible, or cross-team work
needs stronger user evidence, quality requirements, dependencies, rollout boundaries, and validation.

Do not lengthen a weak PRD to make it look rigorous. If evidence is absent, state the assumption and
how it will be tested. A visible gap is more useful than several paragraphs of plausible rationale.
