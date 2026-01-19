# CLI_CONTRACT.md — AAA Tools CLI Contract (v0.1)

Location (recommended):
- `aaa-tools/specs/CLI_CONTRACT.md`

This document defines the contract for the `aaa` CLI used in the "Script-first, LLM-last" bootstrap flow.
Primary consumers:
- Human operators (local)
- Codex CLI (automation agent)
- CI pipelines

Design goals:
1) Deterministic behavior for core bootstrap operations
2) Idempotent operations where applicable
3) Machine-readable streaming outputs (JSON Lines)
4) Stable exit codes and error taxonomy for precise exception handling

---

## 0. Terminology

- **JSONL**: Newline-delimited JSON objects (one JSON object per line).
- **Step**: A top-level command execution unit from `plan.v0.1.json`.
- **Operation**: A subtask within a step (e.g., create repo, apply template, open PR).
- **Idempotent**: Re-running produces no further changes (or results in a clean "no-op" state).

---

## 1) Global Conventions

### 1.1 Command Family

- Primary:
  - `aaa init ...` — deterministic project bootstrap commands
- Support:
  - `aaa sync ...` — deterministic asset sync commands (skills/workflows)
  - `aaa version` — returns CLI version (human + machine)

### 1.2 Required Flags (ALL `aaa init *` subcommands)

All `aaa init <subcommand>` must accept:

- `--org <TARGET_ORG>` (required)
- `--from-plan <PATH>` (required)
- `--jsonl` (optional, recommended for automation)
  - When enabled, stdout emits JSONL events (see Section 3).
- `--log-dir <PATH>` (optional)
  - If set, write artifacts: stdout.log, stderr.log, and any generated reports.
- `--dry-run` (optional)
  - Do not mutate state; still emit events indicating what would change.
- `--timeout-seconds <int>` (optional)
  - Default: 1800 seconds (30 min). Subcommands may override.

`aaa init` (top-level umbrella command) must accept:
- `--plan <PATH>` (required)
- `--mode pr|direct` (optional, default: `pr`)
- `--jsonl` / `--log-dir` / `--dry-run` / `--timeout-seconds`

### 1.3 Determinism & Idempotency Rules

- `ensure-repos`, `apply-templates`, `protect`, `open-prs`, `verify-ci`, `repo-checks` MUST be idempotent.
- When no changes are needed, the command MUST:
  - exit code `0`
  - emit a final JSONL event with `status="noop"`
- No interactive prompts in automation mode.
  - If user input is required, exit with a specific error code and message.

---

## 2) Exit Codes

Exit codes are stable and must not change across minor versions.

### 2.1 Success Codes
- `0` — OK (operation completed or no-op)

### 2.2 General Failure Codes
- `1` — GENERAL_ERROR (unexpected exception, bug, uncategorized failure)
- `10` — INVALID_ARGUMENT (missing/invalid CLI args, invalid plan path, parse error)
- `11` — PLAN_VALIDATION_FAILED (plan missing required fields or violates schema)
- `12` — ENV_PRECHECK_FAILED (missing gh/git/python/aaa, or `gh auth` not ready)
- `13` — PERMISSION_DENIED (GitHub token/org permissions insufficient)

### 2.3 Repo/Org Lifecycle Codes
- `20` — ORG_NOT_FOUND
- `21` — REPO_CREATE_FAILED
- `22` — REPO_ALREADY_EXISTS_BUT_INACCESSIBLE (exists but no access)
- `23` — REPO_CLONE_FAILED
- `24` — GIT_PUSH_FAILED
- `25` — PR_CREATE_FAILED

### 2.4 Template / Sync Codes
- `30` — TEMPLATE_SOURCE_NOT_FOUND (AAA template repo or tag missing)
- `31` — TEMPLATE_APPLY_FAILED
- `32` — SYNC_WORKFLOWS_FAILED
- `33` — SYNC_SKILLS_FAILED

### 2.5 Governance / Protection / CI Codes
- `40` — BRANCH_PROTECTION_APPLY_FAILED
- `41` — REQUIRED_CHECKS_MISMATCH (required check names not matching lint/test/eval)
- `42` — CI_CHECKS_MISSING
- `43` — CI_CHECKS_FAILED
- `44` — REPO_CHECKS_FAILED (governance-related eval suite failure)

### 2.6 Notes
- In `--jsonl` mode, even on failure, the command MUST emit an `error` event with details before exiting.
- `aaa init` umbrella command should return the **first non-zero** code encountered (or the most severe if aggregating).

---

## 3) Output Format (JSON Lines)

### 3.1 When `--jsonl` is enabled
Stdout MUST be JSONL events (one JSON object per line). No extra text.

Each event MUST include:
- `event` (string)
- `ts` (RFC3339 date-time string)
- `command` (string)
- `step_id` (string; if applicable)
- `status` (string; see below)

Allowed `status` values:
- `start` — started an operation/step
- `progress` — intermediate progress update
- `noop` — nothing changed, already compliant
- `ok` — operation succeeded with changes
- `warn` — succeeded but with warnings
- `error` — failed (paired with `code`, `message`)

### 3.2 Common Event Schemas

#### 3.2.1 start
```json
{"event":"start","ts":"2026-01-18T10:00:00+08:00","command":"aaa init apply-templates","step_id":"apply_templates","status":"start","data":{"org":"X","repo":"Y"}}
```

#### 3.2.2 progress
```json
{"event":"progress","ts":"...","command":"...","step_id":"...","status":"progress","data":{"op":"clone","repo":"Y","pct":30}}
```

#### 3.2.3 result (ok/noop/warn)
```json
{"event":"result","ts":"...","command":"...","step_id":"...","status":"ok","data":{"repo":"Y","changed_files":12,"commit":"abc123","pr_url":"https://..."}}
```

#### 3.2.4 error
```json
{"event":"error","ts":"...","command":"...","step_id":"...","status":"error","code":31,"message":"TEMPLATE_APPLY_FAILED","data":{"repo":"Y","details":"...","hint":"Check AAA_VERSION tag exists"}}
```

### 3.3 When `--jsonl` is NOT enabled

- Stdout may be human-readable.
- However, the last line SHOULD still be a single JSON object if `--output-json <path>` is provided (optional feature).
- For automation, always use `--jsonl`.

---

## 4) Subcommand Specifications (v0.1)

All commands below assume:

- `--org <TARGET_ORG>`
- `--from-plan <PATH>`
- Optional: `--jsonl`, `--log-dir`, `--dry-run`, `--timeout-seconds`

### 4.1 `aaa init ensure-repos`

Purpose:
- Ensure target repositories exist (create if missing).
- No-op if already exist and accessible.

Required Inputs:
- plan must include `repos[]` with `name`, `type`, `visibility`, `default_branch`.

Command:
- `aaa init ensure-repos --org <TARGET_ORG> --from-plan <PATH> [--jsonl]`

Behavior:
- For each repo:
  - If missing -> create
  - If exists -> verify access
  - If exists but inaccessible -> fail with `22`

Outputs (`result` event `data`):
- `repo`
- `status`: `created|exists|failed`
- `url` (if known)
- `visibility`
- `default_branch`

Exit Codes:
- 0 OK / noop
- 13 permission denied
- 21 create failed
- 22 exists but inaccessible
- 20 org not found

---

### 4.2 `aaa init apply-templates`

Purpose:
- Apply AAA template content to each repo and commit changes on a branch.
- Ensures docs repos contain ACC/PP/.ai-context and PRD/ADR templates; service/frontend contain minimal skeleton + docs link.

Required Inputs:
- plan `aaa.templates` mapping (docs/service/frontend)
- `aaa.version_tag` (or CLI flag `--aaa-tag`)

Required Flags:
- `--aaa-tag <vX.Y.Z>` (required)

Command:
- `aaa init apply-templates --org <TARGET_ORG> --from-plan <PATH> --aaa-tag <TAG> [--jsonl]`

Behavior:
- For each repo:
  - clone (or reuse existing working dir)
  - checkout/create branch: `bootstrap/{{PROJECT_SLUG}}/v0.1`
  - apply template matching repo type
  - ensure repo has `.github/workflows/ci.yml` calling `aaa-actions@<TAG>` (unless excluded)
  - commit changes if diff exists
  - push branch

Outputs (`result` event `data`):
- `repo`
- `branch`
- `changed_files`
- `commit`
- `template_source` (e.g., `ai-asset-architecture/aaa-tpl-docs@v0.1.0`)
- `status`: `ok|noop|warn`

Exit Codes:
- 0 OK/noop
- 30 template/tag not found
- 31 apply failed
- 23 clone failed
- 24 push failed

---

### 4.3 `aaa init protect`

Purpose:
- Apply branch protection baseline to `main` with required checks `lint/test/eval` and review requirements.

Behavior:
- For each repo:
  - set protection on default branch
  - set required checks: `lint`, `test`, `eval`
  - enforce PR approvals = 1
  - dismiss stale approvals
  - prevent force push
  - linear history per plan setting (default recommended true)

Outputs (`result` event `data`):
- `repo`
- `applied` (bool)
- `required_checks`
- `settings` (same keys as output.schema.json branch_protection.settings)

Exit Codes:
- 0 OK/noop
- 13 permission denied
- 40 protection apply failed
- 41 required checks mismatch

---

### 4.4 `aaa init open-prs`

Purpose:
- Open PR(s) for branches created in apply-templates.
- One PR per repo by default.

Behavior:
- If branch exists and PR absent -> create PR
- If PR already exists -> no-op and return existing PR URL

Outputs:
- `repo`
- `pr_url`
- `base_branch` (usually `main`)
- `head_branch`

Exit Codes:
- 0 OK/noop
- 25 PR create failed
- 13 permission denied

---

### 4.5 `aaa init verify-ci`

Purpose:
- Verify CI required checks exist and are passing for each repo PR (or for latest main if mode=direct).
- Required checks: `lint`, `test`, `eval`

Behavior:
- For each repo:
  - locate relevant PR (from open-prs output or search)
  - query check runs / workflow status
  - if missing check -> `42`
  - if failing check -> `43`
  - if all pass -> ok

Outputs:
- `repo`
- `checks`: array of `{name,status,details_url}`
- `overall`: `pass|fail|partial`

Exit Codes:
- 0 OK
- 42 checks missing
- 43 checks failed
- 13 permission denied

---

### 4.6 `aaa init repo-checks`

Purpose:
- Run governance-related repository checks (local runner or remote) to validate:
  - readme_required
  - workflow_tag_refs
  - skills_structure
  - prompt_schema
- This step aligns with `aaa-evals` governance suite.

Required Flags:
- `--suite <name>` (required; v0.1 expects `governance`)

Command:
- `aaa init repo-checks --org <TARGET_ORG> --from-plan <PATH> --suite governance [--jsonl]`

Behavior:
- For each repo:
  - run `aaa-evals/runner/run_repo_checks.py` (or equivalent) against repo content
  - return structured results per check

Outputs:
- `repo`
- `suite`
- `checks`: array `{id,status,message}`

Exit Codes:
- 0 OK
- 44 repo checks failed
- 10 invalid args

---

## 5) Umbrella Command: `aaa init --plan <PATH>`

Purpose:
- Execute the entire bootstrap sequence defined by plan steps in order.
- Equivalent to running subcommands in sequence:
  - ensure-repos
  - apply-templates
  - sync workflows/skills (if plan includes)
  - protect
  - open-prs (if mode=pr)
  - verify-ci
  - repo-checks

Required Flags:
- `--plan <PATH>`

Optional:
- `--mode pr|direct` (default `pr`)
- `--jsonl`
- `--log-dir`

Behavior:
- MUST execute steps in plan order.
- On first failure:
  - emit `error` event
  - exit with corresponding code
- MAY support `--continue-on-error` in future versions (not in v0.1).

Outputs:
- JSONL events with `step_id` matching plan step ids.

Exit Codes:
- 0 success
- otherwise propagate first non-zero code

---

## 6) Compatibility Requirements

### 6.1 Stable Check Names

To satisfy branch protection required checks:
- `aaa-actions` workflows MUST expose checks named exactly:
  - `lint`
  - `test`
  - `eval`

If names differ, `aaa init protect` MUST fail with `41`.

### 6.2 Tag Pinning

All generated workflow references MUST pin to `ai-asset-architecture/aaa-actions@<AAA_VERSION_TAG>`.
If the tag is missing, `apply-templates` MUST fail with `30`.

---

## 7) Logging & Artifacts

If `--log-dir` is provided, the CLI MUST write:
- `stdout.log` (raw stdout; in jsonl mode this is the same events)
- `stderr.log`
- Optional:
  - `plan.resolved.json` (plan after variable substitution)
  - `report.partial.json` (if failure occurred mid-way)

---

## 8) Security Constraints

- No secrets may be printed in stdout/stderr.
- When errors include hints, they MUST be non-sensitive.
- Network access is allowed, but any external downloads beyond GitHub must be logged (future extension).

---

## 9) Versioning

- Contract version: `v0.1`
- Any breaking change requires bump to `v0.2` and updates to:
  - INIT_PROJECT_CODEX.md
  - plan schema expectations
  - output schema (if needed)
