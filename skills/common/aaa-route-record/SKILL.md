---
name: aaa-route-record
description: 產生 Route Decision Record（RDR）以利路由決策可審計。
---

# aaa-route-record

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
- Inputs: task_id / input_hash / chosen_route / reason_code / fallback_chain / status
- Outputs: RDR JSON 或 log line

## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- 需上游提供路由決策資料。

## Apply Scenario
需要記錄 triage 路由原因與 fallback chain 時。

## Usage Example
請輸出這次 triage 的 RDR。
