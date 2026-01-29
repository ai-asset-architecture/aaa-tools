# Control Plane Command Contract (v1.0)

> **Purpose**: Definitive CLI interface for the AAA Governance Control Plane (aaa-tools).

## 1. Verification Gates
### `aaa check --enums`
- **Goal**: Validate that all documentation and code assets use canonical enums.
- **Checks**:
    - Scans `milestones/`, `specs/`, and `internal/` for Ledger/Court event strings.
    - Verifies against `ledger_event_enum_v1.md` and `court_case_type_enum_v1.md`.
    - **Outcome**: Returns `EXIT_CODE 0` on success; `1` on drift. **Enum mismatch MUST fail-closed and block Release.** (Reason: `ERR_AUDIT_SCHEMA_MISSING`).

### `aaa check --evidence-index`
- **Goal**: Validate the Release Gate Evidence Index.
- **Checks**:
    - `test -f` on all Related Assets.
    - `grep` for OMEGA Test IDs in the test suite.
    - Validates Evidence Bundle path patterns.

### `aaa export --evidence --version <ver>`
- **Goal**: Generate a cryptographically signed Evidence Bundle.
- **Mandatory Contents**:
    - `ledger_export.jsonl`: Time-bound audit traces.
    - `policy_snapshot.json`: Policy hash and content at time of execution.
    - `test_results.json`: OMEGA verification results for the session.
    - `hash_chain.txt`: Ordered Sha256 hashes of core files + `env_fingerprint`.
- **Packaging**: Container MAY be a `zip`. If zipped, core files MUST stay at zip root.
- **Ordering Rule**: Lexical filename order for hashing + `env_fingerprint` fields.

### `aaa omega replay --bundle <path>`
- **Goal**: Recreate the system state from an Evidence Bundle.
- **env_fingerprint fields**: `os_v, arch, py_v, aaa_v, policy_hash, capability_pack_hash`.
- **Audit Split**: 
    - Decision/Hash Mismatch -> `AUDIT_CORRUPTION` (Severity: CRITICAL). 
    - Case metadata MUST include `env_fingerprint` comparison to distinguish **Environment Drift** from **Evidence Tampering**.

---
*Mechanical baseline for Project OMEGA*
