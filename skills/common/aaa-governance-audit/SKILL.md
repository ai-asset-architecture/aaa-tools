# aaa-governance-audit

## Routing Logic

### Hard Rules (Governance)
- IF target repos missing THEN stop and request targets

### Soft Rules (Scoring)
- Base score: 0

### Routing Decision
- Score < 3: single_path (run governance audit)

## Execution Steps
1. Run governance checks for README/CODEOWNERS/workflows.
2. Aggregate results into a report.
3. Summarize failures and next actions.

## Fallback (Resilience)
- IF any check crashes THEN report partial results and stop.

## Inputs / Outputs
- Inputs: repo list or org, evals path
- Outputs: governance audit report


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Does not auto-fix; reports only.

## Purpose
Run governance checks across the local AAA org repos and save a report under `aaa-tpl-docs/reports/`.

## When to Use
- After bootstrap or major changes
- Before release/tagging

## Inputs
- `AAA_WORKSPACE` (optional): workspace root containing all AAA repos (default: current directory)
- `EVALS_ROOT` (optional): path to `aaa-evals` (default: `${AAA_WORKSPACE}/aaa-evals`)
- `DOCS_ROOT` (optional): path to `aaa-tpl-docs` (default: `${AAA_WORKSPACE}/aaa-tpl-docs`)

## Command
```bash
./scripts/run.sh
```

## Output
- Report: `aaa-tpl-docs/reports/governance_evals_report_YYYYMMDD_HHMM.md`
- Exit code non-zero if any check fails
