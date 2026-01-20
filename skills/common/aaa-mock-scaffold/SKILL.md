---
name: aaa-mock-scaffold
description: 依 API/Schema 產生 mock scaffold，支援多 Agent 並行開發。
---

# aaa-mock-scaffold

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
- Inputs: OpenAPI/Schema + target 路徑
- Outputs: scaffold 模板或生成指令

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 不含實作邏輯，只提供 scaffold。

## Apply Scenario
合約已定義但實作未完成時。

## Usage Example
為這個 endpoint 生成 mock handler scaffold。
