# aaa-docs-link-audit

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
