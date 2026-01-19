# aaa-init-validate-plan

## Routing Logic

### Hard Rules (Governance)
- IF plan path missing THEN stop and request path
- IF schema path missing THEN stop and request path

### Soft Rules (Scoring)
- Base score: 0

### Routing Decision
- Score < 3: single_path (validate plan)

## Execution Steps
1. Validate plan JSON against schema.
2. Report first failure path if invalid.
3. Exit non-zero on failure.

## Fallback (Resilience)
- IF schema missing THEN instruct to download plan.schema.json via gh api.

## Inputs / Outputs
- Inputs: plan path, schema path
- Outputs: pass/fail and error path


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Validates structure only; no business logic checks.

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
