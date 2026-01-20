---
name: aaa-triage-taxonomy
description: 維護任務分類 taxonomy 與分流規則，避免 triage 漂移。
---

# aaa-triage-taxonomy

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
- Inputs: 任務類型描述 / 規則條件
- Outputs: taxonomy 條目更新草稿

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 需與 triage 規則同步更新。

## Apply Scenario
新增技能或分流規則前。

## Usage Example
請新增一個任務類型到 taxonomy。
