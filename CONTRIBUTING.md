# Contributing to aaa-tools

## Scope

`aaa-tools` is the executable governance core of AAA. Contributions should strengthen deterministic workflows, machine-readable boundaries, and maintainer operations.

## Before You Open a Change

1. Check existing specs in `specs/` and tests in `tests/`.
2. Keep changes scoped to one behavior or boundary at a time.
3. Prefer script-first behavior over prompt-only logic.

## Pull Request Expectations

Every PR should include:

- A clear statement of the problem and intended boundary
- Tests for new or changed behavior
- Updated CLI/docs when command surface changes
- Notes on backward compatibility when touching existing commands

## Development Workflow

```bash
python3 -m pip install -e .
pytest
```

Recommended targeted checks while iterating:

```bash
pytest tests/test_public_package_cli_entry_surface.py -q
pytest tests/test_runbook_actions_fs.py -q
```

## Release Discipline

- Use semantic versioning tags for stable releases
- Run `./scripts/release-verify.sh <tag>` before tagging
- Update `CHANGELOG.md` when public behavior changes

## What Not to Submit

- Unbounded automation that bypasses approval boundaries
- Prompt-only features with no deterministic validation path
- Breaking CLI changes without explicit versioning intent
