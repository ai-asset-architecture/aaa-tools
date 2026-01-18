# aaa-init-validate-plan

## Purpose
Validate an init plan against `specs/plan.schema.json` before running bootstrap.

## When to Use
- Before `aaa init --plan ...`
- In CI to enforce deterministic plans

## Inputs
- `PLAN_PATH` (required): path to plan file
- `SCHEMA_PATH` (optional): path to schema (default: `specs/plan.schema.json`)

## Command
```bash
aaa init validate-plan --plan "${PLAN_PATH}" --schema "${SCHEMA_PATH}" --jsonl
```

## Output
- JSONL events to stdout
- Exit code 0 if valid; 10/11 on failure
