# AAA Skills Overview

This folder is the single source of truth (SSOT) for AAA skills.

## Structure
- `common/`: shared skills used by both Codex CLI and Antigravity
- `codex/`: Codex CLI-specific skills
- `agent/`: Antigravity-specific skills

## Naming Convention
- Use the `aaa-` prefix for all org skills to avoid collisions.

## Usage
- Codex CLI sync target: `.codex/skills/`
- Antigravity sync target: `.agent/skills/`

## Included Common Skills (v0.1)
- `aaa-evals-governance-check`
- `aaa-prompts-schema-validate`
- `aaa-init-validate-plan`
- `aaa-branch-protection-audit`
- `aaa-workflow-tag-audit`
- `aaa-docs-link-audit`
