# Codemap — rundesk-team-marketing

Where each part lives. Counts are of artifacts, so they survive a rename and go wrong visibly when
the tree moves on without this page.

Two things share one tree: a guidance-only skill catalog, and the declaration of the four agents
Rundesk creates from it. The team also declares shared integration catalogs its members borrow.

## Packages (skills/ — 12, 61 reference files)

Each holds `SKILL.md` for routing and core procedure, and `references/` for detail loaded on demand.
`references/sources.md` is required in every touched package.

| Package | References | Command |
|---|---|---|
| `analyzing-growth-data` | 4 | — |
| `conversion-landing-pages` | 4 | — |
| `lead-compliance-gates` | 4 | — |
| `managing-marketing-work` | 2 | — |
| `researching-competitors` | 7 | — |
| `researching-customers` | 5 | — |
| `researching-markets` | 6 | — |
| `researching-topics` | 4 | — |
| `seo` | 12 | — |
| `verifying-datasets` | 4 | — |
| `writing-prds` | 4 | — |
| `writing-technical-docs` | 5 | — |

Every package is guidance only: no script, executable, credential, or network call.

## Team (agents/ — 4 members)

Each member's `agents/<name>/AGENTS.md` is its whole operating contract, and `team.json` declares
which skills it holds and who it may delegate to.

| Member | Owns |
|---|---|
| `beacon` | organic and AI search, from ranked opportunity to proposed test |
| `scout` | markets, customers, and competitors, from published sources |
| `signal` | first-party data: integrity, reconciliation, and what it certifies |
| `quill` | requirements, documentation, and messaging from an approved brief |

## Identity (root)

| File | What it is |
|---|---|
| `manifest.json` | schema, name, version (`0.5.0`), and description |
| `README.md` | the consumer contract: the team, its skills, and how to install both |
| `team.json` | the declaration Rundesk reconciles against, including borrowed catalogs |
| `agents/<member>/AGENTS.md` | one member`s whole operating contract |
| `AGENTS.md`, `CLAUDE.md` | the repository guide, byte-identical by contract |
| `RELEASING.md` | the publication contract |
| `THIRD_PARTY_NOTICES.md` | adapted package provenance |

## Tests (tests/ — 1 suite)

The repository contract: the manifest and the tree agree, every package is complete and correctly
named, the README lists exactly what ships, and the guide pair stays byte-identical.

## Automation (.github/)

Issue templates, the pull-request template, and the workflow that runs the suite.

## Documentation (docs/)

`README.md`, `BRIEF.md`, and `CODEMAP.md` at the root, plus `guides/`, `concepts/`.
