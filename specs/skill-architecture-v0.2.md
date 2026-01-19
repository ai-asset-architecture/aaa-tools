# Skill Architecture v0.2 (Decision-Tree Driven)

本文件定義 `aaa-tools/skills` 的 v0.2 結構標準，目的在於把技能從「提示集合」升級為「可路由、可治理、可降級」的決策系統。

## 核心原則
- **Routing First**：先判斷再執行，避免一視同仁地使用昂貴路徑。
- **Governance as Code**：硬規則先行，避免敏感操作與違規行為。
- **Fallback Required**：任何失敗都必須提供降級路徑。
- **Executable Proof**：每個技能應提供最小可執行測試。

## 標準區塊（必備）
每個 `common/aaa-*` skill 必須包含以下區塊：

1. `## Routing Logic`
2. `## Execution Steps`
3. `## Fallback (Resilience)`
4. `## Inputs / Outputs`
5. `## Execution Test`
6. `## Limitations`

> 若無需分流，仍需保留區塊並標明固定路徑與降級方式。

## Routing 設計

### Hard Rules（治理/安全）
- 二元決策，違反即停止或升級。
- 範例：
  - IF input contains secrets THEN stop and request sanitization
  - IF files_changed > 20 THEN route to human review

### Soft Rules（複雜度評分）
- 以加分方式計算複雜度分數。
- 例：`.md` +1，`.py` +5，多 repo +2。

### Routing Decision（分流）
- 依分數選擇 `fast_path` / `standard_path` / `deep_path`。

## Fallback 設計
- 任何工具失敗必須有 Plan B。
- 最低要求：提供可手動執行的步驟或腳本。

## Execution Test
- 每個 skill 提供 `tests/smoke.sh`。
- 測試輸出需為：`PASS` / `SKIP` / `FAIL`。
- 若缺少必要輸入可回報 `SKIP`。

## 檢查與驗證
- `aaa-evals`：`skill_structure_v2` 檢查區塊完整性。
- `aaa-tools/skills/README.md`：列出技能與使用情境。

## 參考檔案
- `skills/SKILL_TEMPLATE.md`
- `skills/README.md`
