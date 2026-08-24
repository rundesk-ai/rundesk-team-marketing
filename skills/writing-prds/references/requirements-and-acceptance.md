# Write product requirements that can be accepted

Use this reference to turn an approved product direction into clear behavior and evidence without
writing the implementation design.

## Write one product condition at a time

Give each consequential requirement a stable local ID. State:

```text
In <context>, <user or actor> can / cannot <behavior>, producing <observable result>, subject to
<material product boundary>.
```

Use the form as a clarity check, not mandatory prose. Scenarios, examples, tables, or user stories are
equally valid when they communicate the behavior better.

Avoid terms whose interpretation changes the delivered product: `appropriate`, `seamless`, `normal`,
`etc.`, `and/or`, `user-friendly`, and `as needed`. Replace them with the actual state, actor, outcome,
or measurable condition. Do not split terminology hairs that product collaborators can resolve through
ordinary review; focus on ambiguity that could change behavior, scope, or acceptance.

```text
Bad:  R-4 — Users can easily manage notifications and other settings.
Good: R-4a — In <supported context>, <target user> can <notification behavior> and sees <result>.
      R-4b — <Separate settings behavior, if actually required>.
```

Name each actor, object, and event in the word the domain already uses, and keep one term per concept
for the whole document. A PRD that calls the same person a buyer in one requirement, a client in the
next, and a user in the third states three conditions nobody can check against each other, and the
delivery team resolves the difference by guessing — in one study of how developers choose names, the
median chance that two of them picked the same name was 6.9%. A broader term invented for the
document costs the same clarity: `buyer` says who it is, `party` and `entity` do not.

```text
Bad:  R-7 — The relevant party is recorded, along with the reason.
Good: R-7 — Each completed sale records <the buyer, in the domain's own word> and <the named
      cancellation reason>, both visible on <the order record>.
```

## Cover behavior, not an exhaustive catalog

For each product flow, include only applicable cases:

- successful user path and meaningful alternative paths;
- empty, invalid, unavailable, interrupted, or repeated actions;
- eligibility, role, permission, privacy, and destructive-action boundaries;
- state retained, changed, communicated, or recovered;
- compatibility and migration visible to users; and
- material product qualities such as accessibility, safety, security, reliability, performance, or
  supportability.

Quality categories are prompts, not mandatory sections. Specify a quality only when user direction,
evidence, risk, policy, or an existing product promise makes it consequential. State the context,
measure, threshold, and verification method when known; otherwise keep the threshold as an owned open
decision.

```text
Bad:  “The page must be fast, secure, scalable, and accessible.”
Good: State each applicable product condition with its approved measure and evidence method; do not
      invent targets to make the row look complete.
```

## Separate priority from necessity

A requirement is necessary when removing it prevents the stated outcome or violates an explicit
constraint. Priority determines delivery order or release inclusion. Record who set priority and what
the label means. Keep optional ideas out of the committed set instead of disguising them as low-priority
requirements.

Check the set for contradictions, duplicates, missing product states, and requirements that prescribe
one technical solution without product justification. Resolve material product trade-offs with the
decision-maker; let delivery specialists choose ordinary implementation details.

## Define acceptance evidence

Pair every requirement with the observable proof that distinguishes met from unmet. Choose the method
that fits the claim:

| Claim | Suitable evidence |
|---|---|
| User-visible behavior or error | Executed acceptance scenario, demonstration, or end-to-end test |
| Business rule | Focused behavior tests plus representative boundary cases |
| Measurable quality | Test or analysis under named conditions and dataset/load |
| Visual or content requirement | Inspection against approved design/content and relevant accessibility checks |
| External constraint | Inspection, test, or review required by the governing contract or policy |

Acceptance criteria describe product-observable conditions, not private implementation steps.

```text
Bad:  “Use Redis and add unit tests.”
Good: State the required observable behavior and product condition; link the technical design and
      name executed evidence separately.

Bad:  “Passes QA.”
Good: Name the scenario, conditions, expected observation, and evidence method.
```

Feature acceptance proves the specified behavior. A shared Definition of Done covers the team's
release-quality baseline. Neither proves that users received the intended value after release; keep
success measures separate.
