# AAA v0.2 Release Notes: Decision Tree Update

**Date:** 2026-01-20
**Codename:** Bifrost
**Status:** Stable (Structure) / Beta (Semantics)

---

## Executive Summary
AAA v0.2 將技能從「提示集合」升級為「決策樹驅動」結構，強化 Routing / Rules / Fallback 與最小執行測試。結構層面已穩定，語義層面的可審計性與分流穩定度將在 v0.2.1 進一步補強。

---

## Key Features

### 1) Decision-Tree Skill Architecture
- 統一 `SKILL_TEMPLATE.md`，強制 Routing / Execution / Fallback / I/O / Limitations / Execution Test。
- Skills 不再線性執行，而是先判斷再執行。

### 2) Triage Root Node
- 新增 `aaa-triage` 作為路由入口。
- 分流依據 Hard Rules + Soft Rules（複雜度評分）。
- 模型選擇以抽象標籤表示（`fast_model` / `reasoning_model`），實際模型由環境配置決定。

### 3) Governance Checks v2
- 新增 `skill_structure_v2` 驗證。
- `common/aaa-*` 技能必須通過結構檢查與 `tests/smoke.sh`。

### 4) Member Onboarding v0.2
- `gh auth setup-git` + `gh api` 私有下載流程。
- SOP 與 Start Here 同步，避免多版本分叉。

---

## Breaking Changes
- **技能結構要求提升**：新技能若缺少 Routing/Fallback/Execution Test 等區塊，驗證會以 non-zero exit code 失敗。
- **建議路由入口變更**：建議先走 `aaa-triage`；直接呼叫技能仍可行但不具 fallback guard。

---

## Migration Guide

### For Users
```bash
python3 -m pip install --upgrade "git+https://github.com/ai-asset-architecture/aaa-tools.git@<tag>"
```
> 若尚未釋出對應 tag，請暫時改用 `@main`（僅限測試）。

### For Contributors
1) 使用 `skills/SKILL_TEMPLATE.md` 補齊區塊。
2) 新增 `tests/smoke.sh` 並回報 PASS/SKIP/FAIL。

---

## Compatibility Matrix
| 項目 | v0.1 | v0.2 | 備註 |
|---|---|---|---|
| Skills 結構（Routing/Execution/Fallback） | Optional | Required | 缺少會驗證失敗 |
| Triage 入口 | N/A | Recommended | 直接呼叫仍可，但缺 fallback guard |
| `gh` 工具依賴 | Optional | Required | 私有 repo 安裝與下載需要 |

---

## Known Limitations

### 1) Smoke PASS ≠ 功能正確
目前 smoke test 僅驗證「可執行、必要檔案存在、基本輸出格式」，不保證路由邏輯或 fallback 行為正確。

### 2) Auditability 缺口
Triage 目前未產生 Route Decision Record（RDR），決策原因無法結構化稽核。

### 3) Taxonomy 漂移風險
Triage 規則仍為啟發式，缺少固定 taxonomy 與測試集，新增技能可能導致分流漂移。

### 4) Operational Limits
- Observability 仍以 stdout 為主，尚未提供集中式 log sink / correlation id。
- Rate limit / retry policy 尚未統一規範。

---

## Success Criteria (v0.2.1)
- 100% triage runs 產生 RDR（JSON）。
- RDR 至少包含：task_id / input_hash / chosen_route / reason_code / fallback_chain / status。
- `tests/triage_cases` 覆蓋核心任務類別，通過率 100%。

---

## Roadmap

### v0.2.1: Auditability (P0)
- RDR 結構化輸出。
- triage_taxonomy + tests/triage_cases。

### v0.2.2: Reliability (P1)
- Fallback fault-injection 測試。
- 技能間 IO contract 測試。

---

*End of Release Notes*
