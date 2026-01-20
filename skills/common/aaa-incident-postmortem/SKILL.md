---
name: aaa-incident-postmortem
description: 產出事件回顧（Incident Postmortem）結構化草稿。
---

# aaa-incident-postmortem

## Routing Logic

### Hard Rules (Governance)
- IF input is missing THEN ask for required context

### Soft Rules (Scoring)
- Base score: 0
- +1 if scope is single doc/update
- +3 if multi-module impact

### Routing Decision
- Score < 3: single_path (produce minimal output)
- Score >= 3: deep_path (include risks and dependencies)

## Execution Steps
```sh
# Step 1: collect inputs
# Step 2: generate structured draft
# Step 3: review and refine
```

## Fallback (Resilience)
```sh
# If context is missing, ask for a short summary and retry.
```

## Inputs / Outputs
- Inputs: 事故時間線 / 影響範圍 / 修復措施
- Outputs: Postmortem Markdown 草稿

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 不自動收集事件資料。

## Apply Scenario
事故處理結束後。

## Usage Example
請產出本次事故的 postmortem 草稿。
