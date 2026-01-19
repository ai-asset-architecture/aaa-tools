# aaa-workflow-tag-audit

## Routing Logic

### Hard Rules (Governance)
- IF repo path missing THEN stop and request target

### Soft Rules (Scoring)
- Base score: 0

### Routing Decision
- Score < 3: single_path (audit workflow tag pinning)

## Execution Steps
1. Scan .github/workflows files.
2. Check uses lines for aaa-actions@<tag>.
3. Report unpinned workflows.

## Fallback (Resilience)
- IF workflows missing THEN report no workflows to check.

## Inputs / Outputs
- Inputs: repo path
- Outputs: list of unpinned workflows


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- String check only; does not run workflows.

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
