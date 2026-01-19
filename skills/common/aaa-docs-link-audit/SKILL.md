# aaa-docs-link-audit

## Routing Logic

### Hard Rules (Governance)
- IF repo path is missing THEN stop and request target

### Soft Rules (Scoring)
- Base score: 0

### Routing Decision
- Score < 3: single_path (check docs links)

## Execution Steps
1. Locate README/docs files.
2. Verify links point to <org>-docs repo.
3. Report missing or inconsistent links.

## Fallback (Resilience)
- IF files not found THEN report missing docs and stop.

## Inputs / Outputs
- Inputs: repo path, expected docs repo name
- Outputs: list of missing/incorrect links


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Does not rewrite docs; reports only.

## Purpose
Verify that service/frontend repos link docs to the <org>-docs repo.

## When to Use
- After template application
- During governance checks

## Inputs
- `TARGET_PATH` (required): repo path to check
- `DOCS_PATTERN` (optional): regex for docs link (default: "<org>-docs")

## Command
```bash
rg -n "${DOCS_PATTERN}" "${TARGET_PATH}/docs/README.md"
```

## Output
- Exit 0 if match found; non-zero otherwise
