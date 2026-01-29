# Control Plane Command Contract (v1.0)

> **Purpose**: Definitive CLI interface for the AAA Governance Control Plane (aaa-tools).

## 1. Verification Gates
### `aaa check --enums`
- **Goal**: Validate that all documentation and code assets use canonical enums.
- **Checks**:
    - Scans `milestones/`, `specs/`, and `internal/` for Ledger/Court event strings.
    - Verifies against `ledger_event_enum_v1.md` and `court_case_type_enum_v1.md`.
    - Returns `EXIT_CODE 0` on success; `1` on drift.

### `aaa check --evidence-index`
- **Goal**: Validate the Release Gate Evidence Index.
- **Checks**:
    - `test -f` on all Related Assets.
    - `grep` for OMEGA Test IDs in the test suite.
    - Validates Evidence Bundle path patterns.

## 2. Replay & Export
### `aaa export --evidence --version <ver>`
- **Goal**: Generate a cryptographically signed Evidence Bundle.
- **Contents**:
    - `manifest.json` (hashes of all parts).
    - `ledger_snapshot.json` (time-bound audit traces).
    - `case_snapshot.json` (linked court rulings).
    - `test_results.xml` (OMEGA verification output).

### `aaa omega replay --bundle <path>`
- **Goal**: Recreate the system state from an Evidence Bundle for audit verification.
- **Outcome**: Deterministic confirmation of the original governance decision.

---
*Mechanical baseline for Project OMEGA*
