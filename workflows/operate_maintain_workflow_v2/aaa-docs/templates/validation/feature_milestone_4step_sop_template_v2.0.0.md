---
summary_zh: 'AAA v2.0.0 版本開發 4-Step SOP 可貼用模板（AI/Agent 直接使用）。'
summary_en: 'AAA v2.0.0 4-Step lifecycle copy-paste template for AI/agents.'
version: '2.0.0'
created: '2026-03-01'
usage: 'Use this template to execute Step1~Step4 with machine-checkable evidence.'
---

# AAA 4-Step SOP Template v2.0.0

## Step 1 Plan Template (`plan-strict`)
```markdown
# Implementation Plan: {version} {title}

## Goal
{one-line objective}

## Step Boundary (Strict)
- Step 1 allowed: docs/**, scripts/gates/**, .github/workflows/**
- Step 1 forbidden: src/**, PRD/**, runtime/build config

## Proposed Changes
### [{repo-name}]
#### [NEW/MODIFY] {path}
- {change description}

## Deliverables (No-Glob)
- [ ] docs/plans/YYYY-MM-DD-{version}-{name}-plan.md
- [ ] docs/audits/YYYY-MM-DD-{version}-{name}-audit.md
- [ ] docs/reviews/YYYY-MM-DD-{version}-{name}-diff-paths.md
- [ ] docs/contracts/{name}.schema.json
- [ ] docs/contracts/examples/pass/{name}.pass.json
- [ ] docs/contracts/examples/fail/{name}.fail.json

## Index Update (Step1 Blocking)
- [ ] aaa-tpl-docs/version_index.md append/update done
- [ ] aaa-tpl-docs/workflow_index.md append/update done (if workflow involved)

## Triple-Summary Protocol
### 1. Strategic Plan
### 2. Schema Evolution
### 3. Component Architecture
```

## Step 1 Audit Template (`audit-strict`)
```markdown
# Validation Audit: {version} {title}

## Meta
- audit_id: {id}
- plan_ref: {path}
- required_at_step mapping: Step1/Step2

## Controls
### CTRL-00 Step Boundary
- required_at_step: Step1
- Evidence: diff_paths_report={path}

### CTRL-INDEX-01 Version Index Update
- required_at_step: Step1
- Acceptance: new/updated row exists in version_index.md

### CTRL-INDEX-02 Workflow Index Update
- required_at_step: Step1
- Acceptance: new/updated row exists in workflow_index.md (if involved)

### CTRL-REMOTE-01 Remote run_ref only
- required_at_step: Step2
- Acceptance: run_ref scheme is `gh-actions:`

## 1+2+1 Coverage
- [ ] Happy Path
- [ ] Edge Case
- [ ] Edge Case
- [ ] Negative Case
```

## Step 2 Run Evidence Template
```markdown
# Run Evidence: {version} {title}

- run_ref: gh-actions:{repo}@{workflow_file}#{run_id}
- computed_at_taipei: {RFC3339+08:00}
- inputs_digest: sha256:{64hex}
- source_paths:
  - {path-1}
  - {path-2}
- evidence_path: {specific/path/no-glob}
- notes: {optional}
```

## Step 3 Preservation Template
```markdown
# Preservation Evidence: {version} {title}

## Value Check
- Evals:
- Templates:
- Policy Packs:
- Tools:

## Evidence Files
- result.json: {path}
- index.json: {path}
- run-evidence.md: {path}

## Digests
- inputs_digest: sha256:{64hex}
- policy_digest: sha256:{64hex}
- dataset_digest: sha256:{64hex}
```

## Step 4 Completion Template
```markdown
# Completion Report: {version} {title}

## Status
- final_status: COMPLETED | COMPLETED_STEP1 | BRIDGE_ONLY

## Deliverables
- milestone_summary: docs/milestones/YYYYMMDD_{version}_{name}.md
- completion_report: docs/milestones/completion-reports/{version}_completion_report_YYYYMMDD.md

## Index Sync
- version_index.md updated: yes/no
- workflow_index.md updated: yes/no

## MCP Validation Verdicts
- header_governance: PASS/FAIL
- ops_registry_versions: PASS/FAIL
- ops_registry_workflows: PASS/FAIL
- ops_dashboard: PASS/FAIL
- ops_version_detail: PASS/FAIL
```

## Machine-Scannable Exit Checklist Block
```yaml
ExitChecklistStep: <1|2|3|4>
ExitChecklistVersion: v2.0.0
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
