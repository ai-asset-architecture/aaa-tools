# aaa-prompts-schema-validate

## Routing Logic

### Hard Rules (Governance)
- IF schema path missing THEN stop and request path
- IF prompts dir missing THEN stop and request path

### Soft Rules (Scoring)
- Base score: 0

### Routing Decision
- Score < 3: single_path (validate prompts)

## Execution Steps
1. Load prompt.schema.json.
2. Validate all prompt JSON files under prompts/.
3. Report failures with file paths.

## Fallback (Resilience)
- IF validator missing THEN instruct to install jsonschema.

## Inputs / Outputs
- Inputs: schema path, prompts dir
- Outputs: pass/fail with file errors


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Schema validation only; no quality scoring.

## Purpose
Validate all prompts under `aaa-prompts` against `prompt.schema.json`.

## When to Use
- Before promoting new prompts.
- As part of CI or governance checks.

## Inputs
- `PROMPTS_ROOT` (required): path to `aaa-prompts` repo.
- `SCHEMA_PATH` (optional): schema path relative to `PROMPTS_ROOT` (default: `prompt.schema.json`).

## Command
```bash
python "${EVALS_ROOT}/runner/run_repo_checks.py" --check prompt --repo "${PROMPTS_ROOT}" --schema-path "${SCHEMA_PATH}" --prompts-dir prompts
```

## Output
- JSON output from prompt schema check (stdout)
- Exit non-zero if validation fails
