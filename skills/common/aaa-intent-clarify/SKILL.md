---
name: aaa-intent-clarify
description: 將模糊需求轉換為可執行的任務定義與約束條件。
---

# aaa-intent-clarify

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
- Inputs: 使用者需求 / 專案背景
- Outputs: 結構化任務定義（含範圍、非目標、限制）

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 需要基本上下文文件（PRD/Playbook）。

## Apply Scenario
需求過於抽象、任務拆解前置。

## Usage Example
把這個需求轉成可交付的 Architect Prompt。
