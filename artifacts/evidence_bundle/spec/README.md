# Evidence Bundle Specification (v1.0)

## Overview
An "Evidence Bundle" is a cryptographically signed package containing all artifacts required to verify a specific release or operation.

## Mandatory Contents
1. **`manifest.json`**: 
    - `version`, `timestamp`, `actor_id`
    - `file_hashes` (SHA-256)
2. **`ledger_export.jsonl`**: 
    - A hash-chained export of the `RiskLedger` for the relevant session.
3. **`test_report.json`**: 
    - Full output from the OMEGA test suite.
4. **`court_case_audit/`**: 
    - Snapshots of any Court Cases triggered during the execution.
5. **`policy_snapshot/`**: 
    - The active ruleset and the global `policy_hash` used during the session.

## Verification
Bundles are verified using the `aaa-tools trust verify-bundle <file>` command.
Verification fails if:
- Hash chain is broken.
- Signatures do not match the Global Trust Network.
- Timestamps are outside the allowed grace period.
