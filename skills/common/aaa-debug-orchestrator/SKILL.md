---
name: aaa-debug-orchestrator
description: 統一管理多 Agent 除錯流程，避免重複調查與誤判。
---

# aaa-debug-orchestrator

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
- Inputs: 問題描述 + 影響範圍
- Outputs: Debug steps + 任務分派清單

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 需要明確模組邊界與 log/trace。

## Apply Scenario
跨模組 bug、修復需要協作時。

## Usage Example
產出 Debug Plan 並分派給不同 Agent。
