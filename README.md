# aaa-tools

`aaa-tools` is the executable core of AAA.

AAA is an open-source governance toolkit for turning AI-assisted work into reusable, versioned, testable, and auditable engineering assets. Instead of treating AI output as one-off chat results, AAA turns work into durable project assets such as CLI workflows, schemas, runbooks, eval checks, templates, and approval/evidence boundaries.

## Why This Repo Qualifies for Codex for OSS

`aaa-tools` is the main executable repository of AAA, maintained as public open-source infrastructure for AI-assisted software governance. It provides real maintainer workflows, not just ideas: bootstrap automation, schema validation, repo checks, CI verification, runbook execution, and safety boundaries. The project is aimed at an emerging OSS problem with clear ecosystem value: helping teams make agent-assisted engineering repeatable, reviewable, and auditable while keeping human approval in the loop.

## What Is AAA?

AAA is a multi-repo open-source system for teams that want to use AI in real software delivery without losing structure or accountability.

The project exists to solve a specific problem:

> Agent productivity increases faster than governance capacity.

Without stable structure, AI-assisted work tends to drift into undocumented decisions, inconsistent quality, and review-heavy maintenance. AAA addresses that with executable governance.

In practice, AAA packages AI-native engineering controls into reusable assets:

- CLI workflows for deterministic operations
- Schemas and contracts for machine-checkable structure
- Runbooks and playbooks for repeatable execution
- Eval-oriented checks for quality and regression control
- Templates and scaffolding for consistent project setup
- Evidence and approval boundaries for human accountability

## Why `aaa-tools` Matters

AAA spans multiple repositories, but `aaa-tools` is the main executable entry point. It is the repo that turns AAA from a documentation concept into runnable maintainer automation.

If a reviewer needs to understand AAA quickly, this repo should answer:

- what AAA is
- what AAA can do today
- how the system becomes executable
- what capabilities are already public and testable

## What Problem AAA Solves

Agent-assisted development increases output speed faster than most teams can increase governance capacity. AAA addresses that gap with deterministic CLI workflows, schemas, runbooks, eval-oriented checks, and explicit human approval boundaries.

AAA is designed for teams that need more than prompts:

- Stable bootstrap workflows for new repos and multi-repo workspaces
- Schema-backed plans and machine-checkable governance checks
- Runbook execution with safety boundaries
- Evidence-oriented maintainer automation instead of free-form agent drift

## What AAA Can Do Today

The current public runtime in `aaa-tools` already supports:

- Deterministic project bootstrap through `aaa init`
- Schema-backed init plan validation
- Multi-repo setup and template application
- Branch protection and CI verification workflows
- Governance repo checks and machine-readable reports
- Runbook execution with explicit runtime and file-system boundaries
- JSON and JSONL output for automation
- Skill, template, prompt, and eval distribution support across AAA repos
- Safety boundaries such as `PATH_TRAVERSAL` protection and readiness/truth gating

## How AAA Is Structured

AAA is organized as a set of focused public repositories:

- `aaa-tools`: CLI runtime and governance automation
- `aaa-actions`: workflow automation building blocks
- `aaa-evals`: evaluation and regression assets
- `aaa-prompts`: prompt assets separated from executable logic
- `aaa-observability`: reporting and visibility surfaces
- `aaa-tpl-docs`: documentation and playbook templates
- `aaa-tpl-service`: backend/service starter template
- `aaa-tpl-frontend`: frontend starter template

This repo is where those governance ideas become executable.

## 5-Minute Quickstart

```bash
gh auth setup-git
python3 -m pip install "git+https://github.com/ai-asset-architecture/aaa-tools.git@v2.0.0"
aaa --version
```

Validate an init plan:

```bash
aaa init validate-plan --plan path/to/plan.json --schema specs/plan.schema.json --jsonl
```

Apply the bootstrap flow:

```bash
aaa init ensure-repos --org <github-org> --from-plan path/to/plan.json --jsonl
aaa init apply-templates --org <github-org> --from-plan path/to/plan.json --aaa-tag v2.0.0 --jsonl
aaa init protect --org <github-org> --from-plan path/to/plan.json --jsonl
aaa init verify-ci --org <github-org> --from-plan path/to/plan.json --jsonl
aaa init repo-checks --org <github-org> --from-plan path/to/plan.json --suite governance --jsonl
```

Run a runbook with bounded machine-readable output:

```bash
aaa run runbook operate-maintain-workflow-v2 --runbook-file runbooks/example.json --json
```

## Architecture Overview

AAA follows a script-first, LLM-last model:

1. Schemas define allowed structure and boundary conditions.
2. Deterministic CLI commands execute bootstrap, validation, protection, and verification workflows.
3. Runbooks and eval-style checks provide repeatable operational paths.
4. Humans retain approval authority for merges, releases, policy changes, and trust-boundary decisions.

This repo contains the executable runtime for those guarantees: CLI entrypoints, governance checks, package/readiness gates, runbook execution, skill distribution, and supporting tests.

## CLI Surface

Core commands:

- `aaa version`
- `aaa sync`
- `aaa lint`
- `aaa eval`
- `aaa outdated --json`
- `aaa governance update-index`
- `aaa governance validate-session-readiness-state`
- `aaa governance readiness-inspect`
- `aaa run runbook <id> --runbook-file <path> --json`

Init and bootstrap commands:

- `aaa init validate-plan`
- `aaa init ensure-repos`
- `aaa init apply-templates`
- `aaa init protect`
- `aaa init open-prs`
- `aaa init verify-ci`
- `aaa init repo-checks`
- `aaa init --plan`

## Proven Capabilities

The current public runtime already includes:

- Deterministic `aaa init` orchestration
- Schema validation for initialization plans and runtime bundles
- JSON and JSONL machine interfaces for automation
- `--runbook-file` support for explicit runbook execution
- `PATH_TRAVERSAL` protections in runbook file operations
- Readiness and support-truth boundary checks
- Orphaned asset and package prerequisite gating
- Skill distribution and workspace bootstrap support

## Repository Map

- `aaa/`: CLI runtime, governance commands, package/readiness gates, runbook runtime
- `tests/`: regression coverage for CLI commands and governance boundaries
- `runbooks/`: executable runbook inputs and examples
- `templates/`: reusable bootstrap/template assets
- `skills/`: source-of-truth skill assets distributed to agents
- `specs/`: CLI contracts and supporting design references
- `scripts/`: release and maintenance scripts

## Maintainer Model

AAA is maintained as a multi-repo governance toolkit. `aaa-tools` is the executable core, while adjacent repos provide templates, prompts, evals, docs, actions, and observability surfaces.

Maintainer expectations:

- New commands require tests and usage documentation
- Breaking CLI changes require an intentional version bump
- Public releases should run `./scripts/release-verify.sh <tag>` before tagging
- Human approval remains mandatory for merge, release, and policy decisions

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [ROADMAP.md](ROADMAP.md).

## Current Release

- Current packaged CLI version: `2.0.0`
- Recommended install pin: `v2.0.0`
- Experimental import tag present in git history: `v2.1.0-operate-maintain-import`

Release validation:

```bash
./scripts/release-verify.sh v2.0.0
```

## Public Roadmap

Near-term public priorities:

- Harden public release cadence and changelog discipline
- Expand quickstart and multi-repo bootstrap examples
- Publish more sanitized dogfooding case studies
- Improve maintainer automation for PR review, release closure, and regression analysis
- Continue tightening readiness, permission, and evidence-promotion boundaries

See [ROADMAP.md](ROADMAP.md) for the detailed roadmap.

## Dogfooding Case Study

AAA is most persuasive when shown on a real agent-assisted workflow. See [docs/case-studies/agent-orchestrated-engineering-project.md](docs/case-studies/agent-orchestrated-engineering-project.md).

## Related Repositories

- `aaa-docs`: public documentation and governance references
- `aaa-tpl-docs`: document template repo and project playbooks
- `aaa-actions`: GitHub Actions and workflow building blocks
- `aaa-evals`: evaluation assets and regression scaffolding
- `aaa-observability`: instrumentation and operational visibility assets
- `aaa-prompts`: prompt assets separated from executable governance logic

## Additional References

- CLI background: `specs/aaa CLI 背景與使用說明.md`
- CLI contract: `specs/CLI_CONTRACT.md`
- Historical release notes: `RELEASE_NOTES_v0.2.md`
