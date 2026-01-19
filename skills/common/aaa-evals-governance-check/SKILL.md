# aaa-evals-governance-check

## Routing Logic

### Hard Rules (Governance)
- IF TARGET_PATH is missing THEN stop and request path

### Soft Rules (Scoring)
- Base score: 0

### Routing Decision
- Score < 3: single_path (run governance checks)

## Execution Steps
1. Resolve TARGET_PATH and EVALS_ROOT.
2. Run readme/workflow/skills/prompt checks.
3. Aggregate JSON results for the report.

## Fallback (Resilience)
- IF runner missing THEN instruct to install `aaa-evals/runner/requirements.txt`.

## Inputs / Outputs
- Inputs: TARGET_PATH, EVALS_ROOT, CHECKS
- Outputs: JSON lines per check, non-zero exit on failure


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Does not fix issues; only reports findings.

## Purpose
Run the AAA governance eval suites against a target repo or workspace and output a machine-readable report.

## When to Use
- Validate README/WORKFLOW/SKILLS/PROMPT schema compliance.
- Gate promotion or bootstrap verification.

## Inputs
- `TARGET_PATH` (required): path to repo/workspace to validate.
- `EVALS_ROOT` (optional): path to `aaa-evals` (default: `./aaa-evals`).
- `CHECKS` (optional): comma-separated checks to run (default: `readme,workflow,skills,prompt`).

## Command
```bash
CHECKS=readme,workflow,skills,prompt
python "${EVALS_ROOT}/runner/run_repo_checks.py" --check readme --repo "${TARGET_PATH}"
python "${EVALS_ROOT}/runner/run_repo_checks.py" --check workflow --repo "${TARGET_PATH}"
python "${EVALS_ROOT}/runner/run_repo_checks.py" --check skills --repo "${TARGET_PATH}" --skills-root skills
python "${EVALS_ROOT}/runner/run_repo_checks.py" --check prompt --repo "${TARGET_PATH}" --schema-path prompt.schema.json --prompts-dir prompts
```

## Output
- JSON lines from each check (stdout)
- Exit non-zero if any check fails
