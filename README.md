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
- `aaa run runbook <id>@<version>` - execute a runbook by id and version
- `aaa governance update-index` - generate README.md/index.json for a directory
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

## Governance Audits
- `aaa-gh-org-audit` - audit GitHub org settings and repo compliance (writes report to `aaa-tpl-docs/reports/`).

## Install & Update
Recommended install is pinned to a released tag.

```bash
# Ensure git uses your GitHub CLI credentials (required for private repos)
gh auth setup-git

# Install a pinned version
python3 -m pip install "git+https://github.com/ai-asset-architecture/aaa-tools.git@v0.7.1"

# Verify
aaa --version
```

Update to a newer version by re-running the install command with a newer tag:

```bash
python3 -m pip install --upgrade "git+https://github.com/ai-asset-architecture/aaa-tools.git@v0.7.1"
```

## CLI 背景與使用說明
See `aaa-tools/specs/aaa CLI 背景與使用說明.md`.

## Release Notes
- `aaa-tools/RELEASE_NOTES_v0.2.md`
