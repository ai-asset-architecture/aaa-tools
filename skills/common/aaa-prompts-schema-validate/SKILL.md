# aaa-prompts-schema-validate

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
