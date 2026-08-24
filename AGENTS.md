# AGENTS

## Purpose

This repository publishes Rundesk's marketing team as one versioned artifact. It contains a mixed
guidance and read-only integration skill catalog, the team declaration, and canonical instructions
for Beacon, Scout, Signal, and Quill. `README.md` is the consumer contract, `manifest.json` is the
catalog identity, `team.json` declares the members, and `agents/<member>/AGENTS.md` defines each
member's always-on behavior.

The repository is self-contained at runtime. Adapted packages preserve their source commit and
license in `THIRD_PARTY_NOTICES.md`. No package may depend on another checkout.

## Before you work

1. Read this file, `README.md`, `team.json`, and every complete file you may change. For a package,
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
docs/                              stable validation method, evidence, and coverage gaps
skills/<name>/                     guidance or self-contained integration packages
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
- Guidance packages contain references only when needed. Integration packages keep their complete
  runtime, tests, declarations, and references inside the package.
- Runtime packages use Python 3.9+ and the standard library, bound reads, explicit resource and
  account selection, safe output, offline tests, and preview-first confirmation for mutations.
- `team.json` contains exactly `schema`, `name`, and `members`. Each member contains exactly `name`,
  `description`, `instructions`, `skills`, `delegates_to`, and `self_improve`.
- A member's `skills` is a sorted positive allowlist containing only packages this catalog ships.
  Product-owned Rundesk skills are never shipped or listed.
- `google-auth` is the catalog's sole Google OAuth provider declaration and is not a member grant.

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
Beacon owns external growth evidence, Scout owns external research, Signal owns first-party
measurement and analysis, and Quill owns messaging and content artifacts.

Growth evidence and external research are separated by how a claim is proved, not by its subject.
Growth evidence is retrieved from a property or serving surface and can be retrieved again. External
research is cited to a source someone else can look up. The same competitor belongs to Beacon as a
site and to Scout as a business, and a question needing both is two requests the requester sequences.

Inbound-only bounds named-agent handoffs, not provider subagents. A member may use bounded provider
subagents when their value exceeds coordination cost, but retains scope, integration, and proof.
Repository contributors may delegate only non-overlapping work and must verify every return.

## Architecture and conventions

Separate always-on responsibility from conditional capability. Each member instruction file has
exactly four sections after its title: `Before you act`, `Routing`, `Scope`, and `Return`, with no
skill names. A skill supplies reusable judgment or a guarded integration and never assumes this
team's topology.

Use the canonical terms growth evidence, external research, retrieval, citation, first-party data,
funnel, cohort, retention, attribution, experiment, segment, forecast, brief, message, and content. Preserve Google,
PostHog, and other vendor names at their boundaries. Distinguish attribution from causal effect,
forecast from target or commitment, and a source citation from an AI answer's citation of a page.

## Documentation duties

Keep README, manifest, tests, team declaration, member instructions, package tree, environment
requirements, and provenance synchronized. Update `THIRD_PARTY_NOTICES.md` when adapted content or
its source commit changes. Verify source and local links. Record stable behavior cases in
`docs/team-validation.md`; do not turn consumer documentation into maintainer state.

## Build, test, and run

Run the root suite, every integration package suite, credential-free `--help` and `profiles` paths,
local link checks, `git diff --check`, and privacy review. Run launchers once from outside the
repository to prove package-relative execution. All tests use synthetic fixtures and no network.

Prove skills-only preview/install and team preview/install/update against the exact compatible CLI
head in a disposable `RUNDESK_HOME`. Preview must change nothing, team installation must reconcile
exact members and grants, and gateways must remain stopped.

## Pull requests and releases

Use `.github/pull_request_template.md` for pull requests. Every claim and checked gate must describe
the exact head. Required CI must pass for that head. Follow `RELEASING.md`; do not tag unverified or
unmerged content, reuse a tag, or claim publication from a local commit.

## Definition of done

The requested scope is complete only when manifest, skills, runtime packages, provenance, README,
team declaration, member instructions, and tests agree; the full offline suite and package gates
pass with non-zero counts; applicable links and disposable install paths are verified; the diff and
privacy review is clean; and no placeholder, debug artifact, unexplained skip, temporary process, or
unreported limitation remains.
