---
name: aaa-asset-harvest
description: 用於從討論/修訂/驗證過程中萃取可沉澱的 AAA 資產（Evals / Templates / Prompts），並給出落地位置、命名建議與最小變更清單。當使用者詢問「這次有什麼可沉澱到 AAA？」或需要把經驗轉成資產時使用。
---

# AAA Asset Harvest

## Routing Logic

### Hard Rules (Governance)
- IF request includes secrets/credentials THEN stop and ask user to sanitize

### Soft Rules (Scoring)
- Base score: 0
- +1 if change scope is single doc/update
- +3 if multiple repos or multiple asset types involved

### Routing Decision
- Score < 3: single_path (produce minimal asset list)
- Score >= 3: deep_path (include owners, baselines, and promotion steps)

## Execution Steps
1. Scan the recent discussion or changes for reusable patterns.
2. List candidate assets (max 6) and map to repo types.
3. Provide minimal file list and updates needed (README/baseline/schema).
4. Flag any governance updates needed in `aaa-architecture.md`.

## Fallback (Resilience)
- IF context is unclear THEN ask for a short summary of changes before output.

## Inputs / Outputs
- Inputs: discussion summary, change list, target repos
- Outputs: asset candidates, target repos, required file updates


## Execution Test
- Run: `./tests/smoke.sh`
- Expected: `PASS` or `SKIP` with reason
- Notes: requires inputs; if missing, return SKIP

## Limitations
- Heuristic only; does not implement changes automatically.

## 目標
把「對話、修訂、驗證」中的可重用內容，轉成可落地的 AAA 資產建議與提交清單。

## 何時使用
- 使用者詢問：是否有可新增的 Evals / Templates / Prompts
- 完成修訂或驗證後，需要沉澱成 AAA 資產
- 需要為新規則建立治理檢查或 SOP 模板

## 工作流程（最短路徑）
1. 快速掃描本次對話與改動摘要，列出可沉澱項目（不超過 6 項）。
2. 對每一項決定資產類型與落點：
   - Evals → `aaa-evals`
   - Templates → `aaa-tpl-docs`
   - Prompts → `aaa-prompts`
3. 給出命名建議（小寫、語意清楚，必要時加 `aaa-` 前綴）。
4. 指出需更新的檔案（README / baselines / schema / SOP / reports）。
5. 若涉及治理或資產分類變更，提醒同步 `aaa-tpl-docs/arch/aaa-architecture.md`。

## 輸出格式（建議）
- Evals: `suite/case/baseline` + runner 變更（若需要）
- Templates: 新增檔案路徑 + README 引用
- Prompts: JSON 檔 + README example list

## 注意事項
- 僅列出「可重複使用、可驗證」的項目。
- 先建最小可用版本，避免一次做太大。
- 遵循 `aaa-evals/ASSET_PROMOTION.md` 的流程。
