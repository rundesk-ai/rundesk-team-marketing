# Document interfaces and examples

Use this reference for HTTP and library APIs, commands, configuration, schemas, events, and other
consumer contracts.

## Start from the maintained contract

Prefer a repository's public schema, interface definition, signature, parser, or generated help over
hand-copying structural facts. Generate reference from that source when the project already supports
it, then add the context generation cannot supply.

| Interface | Establish from the repository |
|---|---|
| HTTP or RPC | Version, authentication, method, path/service, request, response, errors, limits, side effects. |
| Library | Import, signature, types, ownership/lifetime, return, exceptions, thread/async behavior, compatibility. |
| CLI | Command grammar, defaults, environment, exit status, stdout/stderr, prompts, destructive or preview behavior. |
| Configuration | Location, type, default, allowed values, precedence, reload/restart behavior, secret handling. |
| Event or stored format | Producer, trigger, schema, ordering, delivery/retention, compatibility, consumer recovery. |

Do not repeat generated tables manually. Generated reference is also not a complete consumer guide:
it rarely explains purpose, prerequisites, the simplest successful path, recovery, or why a field
matters.

## Make each contract usable

For each public operation, document what applies:

- purpose and appropriate use;
- prerequisites, permissions, authentication, and version;
- input names, locations, types, required/optional status, defaults, constraints, and units;
- successful output and externally visible side effects;
- error identifier, triggering condition, recovery, and retry safety;
- idempotency, ordering, pagination, rate, timeout, concurrency, or lifecycle behavior; and
- deprecation and compatibility boundary.

```text
Bad:  `timeout` — Request timeout.
Good: `<field>` — <unit and accepted range>; defaults to <verified value>. On expiry, <verified
      observable result>. State whether retry is safe only if the contract proves it.
```

Angle-bracket values are templates. Replace them with repository evidence; never publish the
template as though it were the product's contract.

## Write examples that can survive copying

Use the smallest supported example that demonstrates one meaningful outcome. Include all required
imports, setup, authentication shape, and cleanup, or mark exactly what is omitted. Use obvious
placeholders and synthetic data; never publish a live secret or owner-specific value.

Pair input with the exact stable output a reader needs to recognize. Explain constraints beside the
example because sample values do not reveal whether a field is required, optional, bounded, or
deprecated.

```text
Bad:  `<command> [--optional] <value>` under “Try it” with no expected result.
Good: one literal, verified command; an expected status or output; then a link to exhaustive options.

Bad:  A response example shows only success while the operation commonly rejects invalid input.
Good: Show the smallest success and the documented error shape, trigger, and safe next action.
```

Label illustrative fragments as fragments. If code is not runnable or omits production concerns,
say so beside it rather than hiding the limitation in a distant note.

## Prove examples through the product surface

Use the repository's native support where available:

- documentation tests or executable examples;
- contract/schema validation;
- CLI golden tests or captured stable help output;
- integration fixtures for requests and responses; and
- build and syntax checks for fenced samples.

Run the exact copied example, not a corrected private variant. Assert only stable output; avoid
timestamps, generated IDs, order, or environment-specific paths unless the example teaches how to
handle them. Report examples that could not run and why.
