# aaa-workflow-tag-audit

## Purpose
Audit workflow references to ensure aaa-actions uses are pinned to tags.

## When to Use
- After template application
- Before branch protection enforcement

## Inputs
- `TARGET_PATH` (required): repo path to check
- `EVALS_ROOT` (optional): path to `aaa-evals` (default: `./aaa-evals`)

## Command
```bash
python "${EVALS_ROOT}/runner/run_repo_checks.py" --check workflow --repo "${TARGET_PATH}"
```

## Output
- JSON output from workflow tag check (stdout)
- Exit non-zero if validation fails
