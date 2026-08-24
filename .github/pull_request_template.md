## Problem

<!-- State the current behavior or limitation, who or what it affects, and the consequence. -->

## Proposed solution

<!-- Describe the implemented outcome, important decisions and rationale, its boundary, and preserved behavior. -->

## Evidence

<!-- Give concise before-and-after observations, source locations, measurements, or contract links that support the merge case. Distinguish evidence from validation. -->

## Scope and compatibility

- Skills changed:
- User-visible guidance:
- Preserved behavior:
- Executables, service adapters, credentials, or network behavior added: none

## Risks and safeguards

<!-- Cover material credential, privacy, destructive, deployment, compatibility, or other risks. State "No material risk identified" when none applies. -->

- Risk:
- Guard:

## Acceptance criteria

- [ ] <!-- Independently checkable outcome proven by this exact head. -->

## Validation

- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Every touched `SKILL.md` and `references/sources.md` was read completely.
- [ ] Every source link added or relied on was verified, or no source link changed.
- [ ] `git diff --check`
- [ ] Required GitHub checks pass for the exact head commit.

```text
# Exact validation and manual verification commands with observed results
```

## Repository gates

- [ ] The diff contains no credential, customer identifier, private-project language, owner-specific path, generated filler, or unrelated artifact.
- [ ] Every skill remains guidance-only: no script, executable, `rundesk.json`, credential, service adapter, or network call was added.
- [ ] Each touched skill's name, routing description, core guidance, references, and package layout follow `AGENTS.md`.
- [ ] Each touched `references/sources.md` maps concrete claims to verified sources and separates source facts from catalog conclusions.
- [ ] `README.md`, `manifest.json`, `tests/test_repository.py`, `skills/`, `team.json`, and `agents/` agree.
- [ ] Any required semantic `manifest.json` version change follows `RELEASING.md` and is stated below.

## Release

- Manifest version: `<before>` → `<after>`
- SemVer reason:
- Release or follow-up required after merge:

## Manual user path

<!-- Give the shortest representative trigger or workflow and expected agent behavior. Explain when no manual user path applies. -->

```text

```

## Agent

<!-- Only for a named agent: replace the placeholder with its name and keep this section. Anyone else deletes the section entirely. Never add provider, model, tool, session, or generated-by branding. -->

🤖 by <Agent>
