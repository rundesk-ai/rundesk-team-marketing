# Keep product intent and evidence aligned

Use this reference when a PRD changes, an existing codebase constrains the discussion, or delivery
must be checked against approved product requirements.

## Reconcile with the current product

For existing behavior, trace the public entry point through current product documentation,
implementation, configuration, and focused tests. Run safe behavior checks when authorized. Record:

```text
Current behavior | evidence checked | requested behavior | product gap | decision needed
```

A code path proves mechanics only when it is reachable. A test proves only the case it executes. A
current implementation may be a bug, legacy constraint, or intentional contract; do not decide which
from code shape alone.

Use current-state research to clarify facts and expose feasibility risks. When it conflicts with an
explicit desired behavior, preserve both until the product authority confirms whether to change the
product, narrow the request, or accept the current behavior.

## Manage changes without freezing discovery

Follow the repository's status vocabulary. If none exists, a small set such as `draft`, `approved`,
`in delivery`, `implemented`, `validated`, and `superseded` is enough. Define who may approve product
direction and who maintains the document.

Record a change only when it alters product intent, target user, outcome, behavior, scope, constraint,
priority, measure, or acceptance. Include the decision, date, authority, reason or new evidence, and
affected requirements. Do not maintain a prose diary or treat approval as a promise that learning
will stop.

For an unresolved item, record:

```text
Question or contradiction | impact | owner | evidence or decision needed | decision point | status
```

Never leave a bare `TBD`. If its answer changes product behavior or acceptance, obtain the decision
before the affected work proceeds.

## Trace only what improves decisions

Keep stable requirement IDs and links to the owning user direction or evidence, delivery item,
relevant design decision, and acceptance result. Use fuller bidirectional traceability for regulated,
safety-critical, contractual, distributed, or high-change work; do not map every requirement to every
code line in an ordinary product increment.

Traceability should answer:

- Why is this requirement necessary?
- What work and product behavior does a change affect?
- What evidence shows the delivered product conforms?
- What outcome evidence shows the product solved the intended problem?

## Validate delivery and outcome separately

After implementation, use a compact evidence record:

```text
Requirement | executed evidence and result | delivery status | outcome evidence | last checked | gap
```

1. Re-read the approved requirement and acceptance condition.
2. Inspect the implemented public behavior and the tests that claim to cover it.
3. Execute the focused acceptance evidence in the named environment when safe.
4. Record the observed result and limit; do not infer success from a code link or test name.
5. Run the required broader release checks without claiming they prove unexamined requirements.
6. After release, evaluate the agreed product measure or user research against its baseline and
   window. Record adverse or guardrail effects as well as the desired outcome.

Use **implemented** only when the acceptance evidence passes. Use **outcome validated** only when the
agreed user or business evidence supports the intended effect. A shipped output may conform and still
fail to create value.

```text
Bad:  Requirement marked complete because a matching class and test file exist.
Good: Name the executed scenario, environment, observed result, and uncovered boundary.

Bad:  Rewrite a failed requirement after launch so the code appears compliant.
Good: Record the mismatch; the product authority decides whether code or requirement changes.
```

Keep historical baselines or superseded decisions available through the repository's normal history.
The current PRD should remain readable as current product truth, not accumulate every obsolete draft.
