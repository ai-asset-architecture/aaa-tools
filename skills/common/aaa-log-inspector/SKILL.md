---
name: aaa-log-inspector
description: 分析 log/CSV/JSONL，產出協作決策所需摘要與警示。
---

# aaa-log-inspector

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
- Inputs: 檔案路徑 + 分析目標
- Outputs: 統計摘要 + 異常提示

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 需要可解析的結構化資料。

## Apply Scenario
排錯、行為分析、資料異常檢查。

## Usage Example
分析這個 log 檔，找出異常與缺失。
