---
name: arch-verify-contract
description: Enforce Single Source of Truth by verifying if API Contracts and Shared Schemas are synchronized.
metadata:
  domain: architecture
  owner: Architect
  short-description: 合約同步檢核
---

# Arch Verify Contract

## When to use
- Use this skill BEFORE creating a git commit.
- Use when the user modifies `pbos-shared-schemas` (Zod) or `pbos-api-contracts` (OpenAPI).
- Use to ensure "Contract-first" governance is respected.

## How to execute

1.  **Run Validation Script**
    The script checks the git status. If `pbos-shared-schemas` is modified but `pbos-api-contracts` is not, it indicates a potential drift.
    
    Execute the following command:
    ```bash
    node scripts/check_drift.js
    ```

2.  **Analyze Result**
    - If the script returns **Exit Code 0**: Validation Passed. You may proceed.
    - If the script returns **Exit Code 1**: Validation Failed.
      - **Action**: Stop the current task.
      - **Fix**: You MUST update `pbos-api-contracts/openapi/v1.yaml` to reflect the changes made in schemas.

## Governance Rule
> "API Contracts are the Single Source of Truth." (Playbook Section 4.1)
