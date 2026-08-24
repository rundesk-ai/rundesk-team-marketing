# Explain architecture and keep it current

Use this reference for how-it-works pages, architecture views, extension guides, maintainer guides,
diagrams, and documentation lifecycle.

## Explain responsibilities and flow

Start with the system boundary and audience question. Show only the components needed to answer it:

- responsibility and public boundary of each component;
- dependencies and direction of control or data;
- state ownership and durable storage;
- representative success and error flows;
- asynchronous work, retries, ordering, and recovery where relevant; and
- external systems and trust boundaries.

Map each named component and interaction to current code or configuration. A directory tree is an
inventory, not an architecture explanation.

```text
Bad:  A box named “Business logic” points to “Database”; arrows and abstraction levels are unlabeled.
Good: Name the diagram type and scope, label each responsibility and relationship, include a legend,
      and link the represented boundaries to their source owners.
```

Use the least diagram detail that answers the question. Preserve an equivalent text description for
search, accessibility, review, and agent use.

## Separate behavior from rationale

Current code and tests can establish what happens. They cannot reliably establish why a choice was
made. Cite a current decision record or named maintainer statement for rationale.

```text
Bad:  “The cache exists to improve performance.” The writer inferred intent from a class name.
Good: “Reads pass through `<cache symbol>` before `<store symbol>`.” Link recorded rationale if it
      exists; otherwise say the rationale is not documented.
```

Treat old design proposals as historical context. Once implemented, they must not masquerade as
half-current operating documentation.

## Document extension points as contracts

An extension guide should name:

1. the supported extension boundary and when to use it;
2. required interface, lifecycle, ownership, and invariants;
3. registration, discovery, configuration, or migration steps;
4. one minimal extension modeled on a maintained real example;
5. focused tests and required broader checks;
6. compatibility and failure behavior; and
7. cleanup or removal steps when state persists.

Do not teach consumers to reach into an internal class because it is easier to find than the public
extension point. If no stable extension contract exists, say so instead of blessing one accidentally.

## Write maintenance and troubleshooting guidance

Keep setup, test, lint, debug, release, migration, and recovery commands tied to the repository's
actual automation. State prerequisites and expected signals. Link common failure symptoms to the
narrowest verified diagnostic and correction.

Do not preserve a stale workaround after its triggering version or code path disappears. Remove or
scope it as part of the same change.

## Prevent drift

- Version technical docs with the code when the repository supports it.
- Review affected docs in the same behavioral change instead of opening an unowned follow-up.
- Generate volatile structural reference from one maintained contract where practical.
- Execute examples and validate schemas, links, and builds in existing automation.
- Give each page one canonical owner and link to it instead of copying prose.
- Prefer stable high-level boundaries and cross-cutting invariants over exhaustive volatile internals.
- Remove material known to be wrong; mark an unresolved gap rather than retaining false certainty.

Use change impact, not elapsed time alone, to trigger review: public interface, default, configuration,
schema, error, dependency, runtime flow, extension point, or supported-version changes should route
to the documentation they affect.
