# aaa-branch-protection-audit

## Purpose
Audit branch protection baseline for a target org or repo list.

## When to Use
- Before release gates
- After bootstrap to confirm governance

## Inputs
- `ORG` (required): target GitHub org
- `REPOS` (optional): comma-separated repo list

## Command
```bash
aaa init protect --org "${ORG}" --from-plan "${PLAN_PATH}" --dry-run --jsonl
```

## Output
- JSONL events to stdout
- Exit code 0 if compliant; non-zero otherwise
