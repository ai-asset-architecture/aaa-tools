---
name: aaa-triage
description: 依任務複雜度與風險進行路由（Routing），決定使用的模型/工具或是否需要人類審核。適用於所有先判斷再執行的任務分流。
---

# AAA Triage

## Routing Logic

### Hard Rules (Governance)
- IF input contains "secret" / "token" / "password" THEN route: human_review
- IF files_changed > 20 OR lines_changed > 500 THEN route: human_review

### Soft Rules (Scoring)
- Base score: 0
- +1 if docs-only change (.md)
- +3 if frontend change (.js/.ts/.tsx/.css)
- +5 if backend/infra change (.py/Dockerfile/.github/workflows)
- +2 if multi-repo dependency detected

### Routing Decision
- Score 0-2: fast_path (cheap model or deterministic script)
- Score 3-6: standard_path (general model)
- Score 7+: deep_path (reasoning model or human review)

## Execution Steps
1. Parse input (prompt or diff stats).
2. Apply hard rules.
3. Calculate score using soft rules.
4. Output decision JSON: {"route":"standard_path","score":5,"risk":"medium"}.

## Fallback (Resilience)
- IF unable to parse diff THEN assume high risk and route to human_review.

## Inputs / Outputs
- Inputs: user prompt, diff stats (files_changed, lines_changed, file types)
- Outputs: route, score, risk level


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Heuristics only; always allow override by human review.
