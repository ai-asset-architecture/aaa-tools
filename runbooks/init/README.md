# Init Runbooks

This folder contains the bootstrap runbooks and schemas for the AAA init flow.

## Source of Truth
- Codex bootstrap protocol: `/.github/BOOTSTRAP_PROTOCOL.md`
- Runbook (Codex): `runbooks/init/INIT_PROJECT_CODEX.md`
- Operator Guide (Human): `runbooks/init/INIT_PROJECT_HUMAN.md`
- Plan: `runbooks/init/plan.v0.1.json`
- Output schema: `runbooks/init/output.schema.json`
- Plan schema: `specs/plan.schema.json`

## Usage
- Use `INIT_PROJECT_CODEX.md` as the Codex execution script.
- Use `INIT_PROJECT_HUMAN.md` as the human operator guide.
- Validate plans against `specs/plan.schema.json` before running.
