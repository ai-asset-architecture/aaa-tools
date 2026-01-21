# Post-init Audit Runbook (v0.1)

## Purpose
Verify governance integrity after `aaa init` completes. This audit ensures repo state matches plan expectations.

## When to Run
- Immediately after `aaa init --plan ...` completes.
- After any manual repo changes that could affect governance.

## Required Command

```bash
aaa init repo-checks \
  --org <TARGET_ORG> \
  --from-plan /tmp/aaa_plan_resolved.json \
  --suite governance \
  --jsonl
```

## Required Outputs
- JSONL stdout (for automation ingestion)
- Summary report stored under `aaa-tpl-docs/reports/`

## Failure Handling
- If `REPO_CHECKS_FAILED` (exit code 44), review the detailed check list and fix the failed repos.

## Notes
- This runbook is mandatory for post-init governance closure.
