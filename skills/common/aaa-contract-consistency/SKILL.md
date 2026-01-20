---
name: aaa-contract-consistency
description: 驗證 API/Schema/Contracts 是否一致，避免協作造成合約漂移。
---

# aaa-contract-consistency

## Routing Logic

### Hard Rules (Governance)
- IF input is missing THEN ask for required context

### Soft Rules (Scoring)
- Base score: 0
- +1 if scope is single file or doc-only
- +3 if multi-module or cross-team impact

### Routing Decision
- Score < 3: single_path (produce minimal output)
- Score >= 3: deep_path (include risks and dependencies)

## Execution Steps
1. Clarify inputs and constraints.
2. Produce the expected output in the required format.
3. Add risks or next actions when needed.

## Fallback (Resilience)
- IF context is unclear THEN request a short summary before proceeding.

## Inputs / Outputs
- Inputs: contract 路徑 + schema 路徑
- Outputs: PASS/FAIL + 差異清單

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 需專案提供檔案路徑與格式規格。

## Apply Scenario
變更 API / Schema 後、合約優先流程。

## Usage Example
確認 contract 與 schema 是否同步。
