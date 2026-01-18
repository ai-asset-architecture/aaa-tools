# aaa-governance-audit

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
