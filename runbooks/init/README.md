# Init Runbooks

This folder contains the bootstrap runbooks and schemas for the AAA init flow.

## Source of Truth
- Codex bootstrap protocol: `/.github/BOOTSTRAP_PROTOCOL.md`
- Runbook (Codex): `runbooks/init/AGENT_BOOTSTRAP.md`
- Post-init audit runbook: `runbooks/init/POST_INIT_AUDIT.md`
- Plan: `runbooks/init/plan.v0.1.json`
- Output schema: `runbooks/init/output.schema.json`
- Plan schema: `specs/plan.schema.json`

## Usage
- Use `AGENT_BOOTSTRAP.md` as the Codex execution script.
- Validate plans against `specs/plan.schema.json` before running.
