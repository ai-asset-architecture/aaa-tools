---
name: aaa-ops-lesson
description: 將多 Agent 協作過程的關鍵決策與修正整理成可追溯紀錄。
---

# aaa-ops-lesson

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
- Inputs: 對話摘要 / 變更重點 / 決策清單
- Outputs: Lesson 紀錄（Markdown 草稿）

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 不自動寫檔，僅產出內容草稿。

## Apply Scenario
協作過程結束、重大修正完成後、要沉澱為團隊知識時。

## Usage Example
請整理這次協作的 Lesson Learned。
