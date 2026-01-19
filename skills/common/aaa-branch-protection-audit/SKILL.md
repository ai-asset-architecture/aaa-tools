# aaa-branch-protection-audit

## Routing Logic

### Hard Rules (Governance)
- IF repo list is missing THEN stop and request targets

### Soft Rules (Scoring)
- Base score: 0

### Routing Decision
- Score < 3: single_path (audit branch protection)

## Execution Steps
1. Collect target repos.
2. Check branch protection settings against baseline.
3. Report mismatches and missing permissions.

## Fallback (Resilience)
- IF API access fails THEN ask user to verify org permissions and retry.

## Inputs / Outputs
- Inputs: org or repo list, baseline settings
- Outputs: audit report with mismatches


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Read-only audit; does not apply fixes.

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
