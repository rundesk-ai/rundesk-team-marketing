# AGENTS

## Purpose

This repository publishes Rundesk's marketing team as one versioned artifact. It contains its
specialist guidance skills, shared integration-catalog declarations, and canonical instructions
for Beacon, Scout, and Quill. `README.md` is the consumer contract, `manifest.json` is the
catalog identity, `team.json` declares the members, and `agents/<member>/AGENTS.md` defines each
member's always-on behavior.

Google, PostHog, and Stripe integration skills remain owned by their source catalogs. Every specialist
guidance package a member uses ships in this catalog. `team.json` declares exact catalog names and
sources, and members use fully qualified skill addresses.

## Before you work

1. Read `docs/BRIEF.md` and `docs/CODEMAP.md` for what this is and where its parts are,
   then this file, `README.md`, `team.json`, and every complete file you may change. For a package,
   read its `SKILL.md`, all linked references, runtime declarations, scripts, and tests.
2. Search before adding a member, package, term, integration, or rule. Extend the existing owner.
3. Use skill-authoring guidance for skill changes, naming guidance for recurring terminology, and
   guarded GitHub guidance for hosted delivery.
4. Inspect the branch, remotes, worktree, provenance, and current tests before editing. Preserve
   unrelated work.
5. Verify catalog and team behavior with a disposable `RUNDESK_HOME`. Never install this checkout
   into the live Rundesk install or use live credentials in tests.

## Repository layout

```text
agents/<member>/AGENTS.md          canonical member instructions
assets/readme/                     public README artwork
docs/                              orientation, guides/, and concepts/
skills/<name>/                     guidance-only specialist skill packages
tests/test_repository.py           repository and team contract
AGENTS.md and CLAUDE.md            byte-identical repository rules
README.md                          consumer contract
RELEASING.md                       publication contract
THIRD_PARTY_NOTICES.md             adapted package provenance
manifest.json and team.json        catalog and team declarations
```

Do not add empty optional directories, generated filler, provider-specific agent metadata, or a
second catalog or team declaration.

## Package and artifact contract

- `manifest.json` contains exactly `schema`, `name`, `version`, and `description`.
- Every package is entirely under `skills/<name>/`, contains a valid `SKILL.md`, and works without
  another repository checkout.
- Guidance packages contain references only when needed. Integration packages remain in the catalog
  that owns their runtime, permissions, tests, declarations, and references.
- `team.json` schema 2 contains exactly `schema`, `name`, `catalogs`, and `members`. Each catalog
  dependency contains exactly `name` and `source`; each member contains exactly `name`,
  `description`, `instructions`, `skills`, `delegates_to`, and `self_improve`.
- A member's `skills` is a sorted positive allowlist of fully qualified addresses from this catalog
  or a declared dependency. Only an integration package comes from a dependency. Product-owned
  Rundesk skills are never shipped or listed.

## Safety and approval gates

Get explicit approval before adding or broadening credentials, OAuth scopes, service mutations,
dependencies, executable behavior, members, delegation, public compatibility, versions, tags,
releases, or repository settings unless the request already authorizes that exact effect.

Never publish credentials, OAuth grants, tokens, personal or customer identifiers, private URLs,
private-project language, owner-specific paths, raw private evidence, or unsupported claims. Never
reset, discard, force-push, or rewrite another person's work. Never contact a live service from an
offline test or report an effect the service did not verify.

## Delegation

The team has no lead. Each member is an inbound-only specialist and returns to the requester.
Beacon owns traceable growth evidence, first-party measurement, and supplied-data verification;
Scout owns external research; and Quill owns messaging and content artifacts. The requester owns
ranking, recommendations, verdicts, and decisions.

Two boundaries keep those specialists distinct.

Growth evidence and external research are separated by how a claim is proved, not by its subject.
Growth evidence is retrieved from a property or serving surface and can be retrieved again. External
research is cited to a source someone else can look up. The same competitor belongs to Beacon as a
site and to Scout as a business, and a question needing both is two requests the requester sequences.

Beacon keeps two evidence modes distinct. Directional growth evidence names the check that would
settle it without ranking what to do. A derived statistic carries its physical inputs, formula,
source, comparable windows, population, denominator, uncertainty, and data-quality checks or is
returned as unestablished. A file or export is verified for provenance and integrity before use,
and two sources that disagree are reconciled rather than chosen between.

Inbound-only bounds named-agent handoffs, not provider subagents. A member may use bounded provider
subagents when their value exceeds coordination cost, but retains scope, integration, and proof.
Repository contributors may delegate only non-overlapping work and must verify every return.

## Architecture and conventions

Separate always-on responsibility from conditional capability. Each member instruction file has
exactly four sections after its title: `Before you act`, `Routing`, `Scope`, and `Return`, with no
skill names. A skill supplies reusable judgment or a guarded integration and never assumes this
team's topology.

Use the canonical terms growth evidence, external research, retrieval, citation, first-party data,
provenance, reconciliation, funnel, cohort, retention, attribution, experiment, segment, forecast, brief, message, and
content. The common noun `signal` means a suggestive input rather than a measurement. Preserve Google, PostHog, Stripe, and other
vendor names at their boundaries. Distinguish attribution from causal effect, forecast from target
or commitment, reported value from recognized revenue, and a source citation from an AI answer's
citation of a page.

## Documentation duties

Keep `docs/` in its layout. Only `README.md`, `BRIEF.md`, and `CODEMAP.md` sit at its root; a home is
added when there is a page for it and never left empty. Use the `structuring-project-docs` skill
before adding a home, moving a page, or changing the shape of one. Ecosystem root files stay at the
repository root, where consumers and tooling look for them.

Update `docs/CODEMAP.md` when a count, a layer, or a file it names changes, and `docs/BRIEF.md` only
when the purpose, audience, or refusals actually move. Keep pages thin: lead with the fact, use a
table wherever the content is tabular, and never restate a package's own guidance at the repository
level.

Keep README, manifest, tests, team declaration, member instructions, package tree, dependency
sources, provenance, and requirements synchronized. Verify source and local links. Record stable
behavior cases in `docs/guides/team-validation.md`; do not turn consumer documentation into maintainer
state.

## Build, test, and run

Run the root suite, local link checks, `git diff --check`, and privacy review. All tests use
synthetic fixtures and no network.

Prove skills-only preview/install and team preview/install/update against the exact compatible CLI
head in a disposable `RUNDESK_HOME`. Preview must change nothing, team installation must reconcile
exact members and grants, and gateways must remain stopped.

## Pull requests and releases

Use `.github/pull_request_template.md` for pull requests. Every claim and checked gate must describe
the exact head. Required CI must pass for that head. Follow `RELEASING.md`; do not tag unverified or
unmerged content, reuse a tag, or claim publication from a local commit.

## Definition of done

The requested scope is complete only when manifest, skills, dependency catalogs, provenance, README,
team declaration, member instructions, and tests agree; the full offline suite and package gates
pass with non-zero counts; applicable links and disposable install paths are verified; the diff and
privacy review is clean; and no placeholder, debug artifact, unexplained skip, temporary process, or
unreported limitation remains.
