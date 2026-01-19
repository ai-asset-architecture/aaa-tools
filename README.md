# aaa-tools

## Purpose / Scope
CLI and automation utilities that make aaa governance rules executable (linting, syncing, eval runs, scaffolding).

## Ownership / CODEOWNERS
Owned by the tools maintainers. See `CODEOWNERS` (to be added).

## Versioning / Release
CLI releases are tagged with `vX.Y.Z`. The recommended install method should pin to a released version.

## How to Consume / Use
Install the `aaa` CLI and use it to sync skills, lint docs, and run evals.

## Contribution / Promotion Rules
All new commands must include usage docs and tests. Breaking CLI changes require a major version bump.

## CLI Commands
- `aaa version` - print CLI version
- `aaa sync` - sync skills/assets to local targets
- `aaa lint` - validate required docs/sections
- `aaa eval` - run eval suites and report results
- `aaa init validate-plan` - validate plan JSON against schema
- `aaa init ensure-repos` - create repos if missing
- `aaa init apply-templates` - apply aaa templates to repos
- `aaa init protect` - apply branch protection baseline
- `aaa init open-prs` - open bootstrap PRs
- `aaa init verify-ci` - verify lint/test/eval checks
- `aaa init repo-checks` - run governance repo checks
- `aaa init --plan` - run full bootstrap from plan and emit report

## Skills Source of Truth
`aaa-tools/skills` is the source of truth for Codex/agent skills. Consumers should sync from this repo.

## Skills Index
See `aaa-tools/skills/README.md` for the current skill list and naming rules.

## Install & Update
TBD. Target state: `aaa` installed via a versioned package or a pinned binary. Until then, run from source after cloning this repo.

## CLI 背景與使用說明
See `aaa-tools/specs/aaa CLI 背景與使用說明.md`.
