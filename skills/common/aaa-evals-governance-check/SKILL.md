# aaa-evals-governance-check

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
