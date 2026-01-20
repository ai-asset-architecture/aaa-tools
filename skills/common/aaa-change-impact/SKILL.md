---
name: aaa-change-impact
description: 分析跨模組變更影響範圍，協助協作分工。
---

# aaa-change-impact

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
- Inputs: 變更清單 / 模組邊界
- Outputs: 影響範圍與風險清單

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 依賴模組邊界定義。

## Apply Scenario
跨模組 PR / 需求變更分析。

## Usage Example
評估這次變更對哪些模組有影響。
