# Establish how the code works

Use this workflow before explaining an unfamiliar or cross-component behavior.

## Start at the public boundary

Identify what the consumer actually invokes or observes:

- exported function, class, package, protocol, or schema;
- command and `--help` surface;
- route, request, event, callback, or stored format;
- configuration key and its supported values; or
- UI action and resulting state.

Search for its definition and every registration or adapter that makes it reachable. A file with a
promising name is not evidence that production calls it.

## Trace a representative flow

Follow one successful path and the material failures through:

```text
entry -> authentication/authorization -> validation -> domain decision -> state or I/O
      -> asynchronous side effects -> response or observable result
```

Use the actual layers the codebase has; do not force this vocabulary onto another architecture.
Record conditions, defaults, feature gates, transactions, retries, ordering, timeouts, and cleanup
only when they change observable behavior.

Then inspect:

- focused tests for branches and error contracts;
- integration or end-to-end tests for wiring and real boundaries;
- fixtures and maintained examples for realistic inputs;
- current configuration and deployment defaults for environment-dependent behavior; and
- consumer call sites for the way the interface is actually used.

## Keep evidence roles distinct

| Evidence | What it can establish | Common trap |
|---|---|---|
| Versioned specification or public schema | Promised contract | Assuming deployment implements it correctly. |
| Current implementation | Actual mechanics and reachable paths | Calling a bug or incidental structure intentional. |
| Executed focused test | The asserted case in its test environment | Generalizing beyond its inputs or mocked boundary. |
| Executed integration or consumer path | Runtime wiring and the observed sequence | Treating one environment as universal. |
| Static call site or fixture | Representative usage shape | Calling an unexecuted example behavioral proof. |
| Decision record or history | Recorded context and rationale | Treating an old proposal as current behavior. |

When evidence conflicts, do not choose the most convenient source silently. State whether the task
is documenting the promised interface, observed implementation, or discrepancy. A documentation-only
change should not redefine product behavior.

## Maintain a claim ledger

Record one row for each consequential statement, not every sentence:

```text
Claim: <bounded statement>
Audience/type: <who needs it and where it belongs>
Contract/code: <file, symbol, schema, or help surface>
Behavior verification: <executed test or safe reproduction, command, and observed result>
Usage evidence: <consumer call site, maintained fixture, or example source>
Limits: <version, environment, mocked boundary, uncertainty>
```

Use stable paths and symbol names instead of brittle line numbers. Do not publish the ledger unless
the repository requires it; it is a drafting control that prevents citations, usage evidence, and
verification from being matched to prose after the fact.

## Verify without broadening authority

Prefer read-only inspection and repository-prescribed checks. Run examples only in a safe local or
test environment. Do not create accounts, spend money, contact users, deploy, mutate production,
use live credentials, or send external requests merely to prove documentation.

If safe execution is unavailable:

- validate syntax and contract shape with existing fixtures or test doubles;
- label the example as unexecuted and name the missing environment;
- avoid exact output claims that were not observed; and
- request authorization only when live proof is necessary to the requested deliverable.

Before delivery, deliberately search for claims that sound useful but are unsupported: `always`,
`never`, `automatically`, `safe`, `fast`, `recommended`, and inferred design rationale are common
places for documentation to outrun evidence.
