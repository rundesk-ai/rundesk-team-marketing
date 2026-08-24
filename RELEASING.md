# Releasing Rundesk Team Marketing

The manifest version labels the catalog Rundesk reports. Catalog content remains authoritative for
update detection, while the matching tag and GitHub Release provide an auditable snapshot.

## Prepare

1. Put every intended catalog change on `main` or in one pull request against `main`.
2. Before the first `v0.1.0` publication, keep unreleased iteration at `0.1.0`. After publication,
   use semantic versioning: patch for compatible corrections, minor for a new skill or compatible
   capability, and major for an incompatible catalog, member, or package contract.
3. Run the complete repository and package gate from `README.md` and wait for the `build` workflow
   on the exact commit.
4. Review the complete package tree, team declaration, README, provenance, environment requirements,
   compatibility impact, sources, and licenses.

Do not tag unmerged content, reuse a published tag, or move a published tag.

## Publish

Read the manifest version and tag the exact verified `main` commit:

```sh
version=$(python3 -c 'import json; print(json.load(open("manifest.json"))["version"])')
git tag "v$version" <main-commit>
git push origin "v$version"
```

The release workflow refuses a mismatched tag, reruns the repository suite, and creates the GitHub
Release. Verify the workflow and stored release:

```sh
gh run list --workflow release.yml --limit 1
gh release view "v$version"
```

Tagging, releasing, or publishing always requires explicit authority for that repository, version,
and commit.
