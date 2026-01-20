# AAA Skills Overview

This folder is the single source of truth (SSOT) for AAA skills.

## Structure
- `common/`: shared skills used by both Codex CLI and Antigravity
- `codex/`: Codex CLI-specific skills
- `agent/`: Antigravity-specific skills

## Naming Convention
- Use the `aaa-` prefix for all org skills to avoid collisions.

## Skill Architecture (v0.2)
All skills MUST follow `skills/SKILL_TEMPLATE.md` and include:
- Routing Logic (Hard Rules + Soft Rules)
- Execution Steps
- Fallback (Resilience)
- Inputs / Outputs + Limitations
- Execution Test (tests/smoke.sh)

**簡化規則**：若技能不需要分流，也必須保留三區塊並標明固定路徑與降級方式。

詳細說明：`aaa-tools/specs/skill-architecture-v0.2.md`

## Skill Execution Test (Standard)
- 每個 `common/aaa-*` 技能需提供 `tests/smoke.sh`
- 測試可在缺少必要輸入時回報 `SKIP`，不得直接失敗
- 測試需輸出 `PASS` / `SKIP` / `FAIL` 其中之一

## Usage
- Codex CLI sync target: `.codex/skills/`
- Antigravity sync target: `.agent/skills/`

## Included Common Skills (v0.2)
- `aaa-evals-governance-check`
- `aaa-prompts-schema-validate`
- `aaa-init-validate-plan`
- `aaa-branch-protection-audit`
- `aaa-workflow-tag-audit`
- `aaa-docs-link-audit`
- `aaa-governance-audit`
- `aaa-asset-harvest`
- `aaa-triage`
- `aaa-ops-lesson`
- `aaa-intent-clarify`
- `aaa-contract-consistency`
- `aaa-log-inspector`
- `aaa-mock-scaffold`
- `aaa-debug-orchestrator`
- `aaa-route-record` (under construction)
- `aaa-triage-taxonomy` (under construction)
- `aaa-change-impact` (under construction)
- `aaa-incident-postmortem` (under construction)

## Skills Catalog (aaa-*)

### `aaa-asset-harvest`
- **Description**: 從討論/修訂/驗證中萃取可沉澱的 AAA 資產（Evals / Templates / Prompts），給出落地位置與最小變更清單。
- **Apply Scenario**: 使用者詢問「這次是否有可沉澱資產」或需要把經驗轉成可重用資產。
- **Usage Example**:
  - 「這次修訂後，有沒有可以新增成 Evals / Templates / Prompts 的內容？」
- **Expected I/O**:
  - Input: 對話/修訂摘要 + 目前變更點
  - Output: 資產類型、落點 repo、命名建議、需更新檔案清單
- **Limitations**:
  - 僅產出「最小可用」清單，不自動實作與提交

### `aaa-ops-lesson`
- **Description**: 將多 Agent 協作過程的關鍵決策與修正整理成可追溯紀錄。
- **Apply Scenario**: 協作過程結束、重大修正完成後、要沉澱為團隊知識時。
- **Usage Example**:
  - 「請整理這次協作的 Lesson Learned。」
- **Expected I/O**:
  - Input: 對話摘要 / 變更重點 / 決策清單
  - Output: Lesson 紀錄（Markdown 草稿）
- **Limitations**:
  - 不自動寫檔，僅產出內容草稿

### `aaa-intent-clarify`
- **Description**: 將模糊需求轉換為可執行的任務定義與約束條件。
- **Apply Scenario**: 需求過於抽象、任務拆解前置。
- **Usage Example**:
  - 「把這個需求轉成可交付的 Architect Prompt。」
- **Expected I/O**:
  - Input: 使用者需求 / 專案背景
  - Output: 結構化任務定義（含範圍、非目標、限制）
- **Limitations**:
  - 需要基本上下文文件（PRD/Playbook）

### `aaa-contract-consistency`
- **Description**: 驗證 API/Schema/Contracts 是否一致，避免協作造成合約漂移。
- **Apply Scenario**: 變更 API / Schema 後、合約優先流程。
- **Usage Example**:
  - 「確認 contract 與 schema 是否同步。」
- **Expected I/O**:
  - Input: contract 路徑 + schema 路徑
  - Output: PASS/FAIL + 差異清單
- **Limitations**:
  - 需專案提供檔案路徑與格式規格

### `aaa-log-inspector`
- **Description**: 分析 log/CSV/JSONL，產出協作決策所需摘要與警示。
- **Apply Scenario**: 排錯、行為分析、資料異常檢查。
- **Usage Example**:
  - 「分析這個 log 檔，找出異常與缺失。」
- **Expected I/O**:
  - Input: 檔案路徑 + 分析目標
  - Output: 統計摘要 + 異常提示
- **Limitations**:
  - 需要可解析的結構化資料

### `aaa-mock-scaffold`
- **Description**: 依 API/Schema 產生 mock scaffold，支援多 Agent 並行開發。
- **Apply Scenario**: 合約已定義但實作未完成時。
- **Usage Example**:
  - 「為這個 endpoint 生成 mock handler scaffold。」
- **Expected I/O**:
  - Input: OpenAPI/Schema + target 路徑
  - Output: scaffold 模板或生成指令
- **Limitations**:
  - 不含實作邏輯，只提供 scaffold

### `aaa-debug-orchestrator`
- **Description**: 統一管理多 Agent 除錯流程，避免重複調查與誤判。
- **Apply Scenario**: 跨模組 bug、修復需要協作時。
- **Usage Example**:
  - 「產出 Debug Plan 並分派給不同 Agent。」
- **Expected I/O**:
  - Input: 問題描述 + 影響範圍
  - Output: Debug steps + 任務分派清單
- **Limitations**:
  - 需要明確模組邊界與 log/trace

### `aaa-route-record` (under construction)
- **Description**: 產生 Route Decision Record（RDR）以利路由決策可審計。
- **Apply Scenario**: 需要記錄 triage 路由原因與 fallback chain 時。
- **Usage Example**:
  - 「請輸出這次 triage 的 RDR。」
- **Expected I/O**:
  - Input: task_id / input_hash / chosen_route / reason_code / fallback_chain / status
  - Output: RDR JSON 或 log line
- **Limitations**:
  - 需上游提供路由決策資料

### `aaa-triage-taxonomy` (under construction)
- **Description**: 維護任務分類 taxonomy 與分流規則，避免 triage 漂移。
- **Apply Scenario**: 新增技能或分流規則前。
- **Usage Example**:
  - 「請新增一個任務類型到 taxonomy。」
- **Expected I/O**:
  - Input: 任務類型描述 / 規則條件
  - Output: taxonomy 條目更新草稿
- **Limitations**:
  - 需與 triage 規則同步更新

### `aaa-change-impact` (under construction)
- **Description**: 分析跨模組變更影響範圍，協助協作分工。
- **Apply Scenario**: 跨模組 PR / 需求變更分析。
- **Usage Example**:
  - 「評估這次變更對哪些模組有影響。」
- **Expected I/O**:
  - Input: 變更清單 / 模組邊界
  - Output: 影響範圍與風險清單
- **Limitations**:
  - 依賴模組邊界定義

### `aaa-incident-postmortem` (under construction)
- **Description**: 產出事件回顧（Incident Postmortem）結構化草稿。
- **Apply Scenario**: 事故處理結束後。
- **Usage Example**:
  - 「請產出本次事故的 postmortem 草稿。」
- **Expected I/O**:
  - Input: 事故時間線 / 影響範圍 / 修復措施
  - Output: Postmortem Markdown 草稿
- **Limitations**:
  - 不自動收集事件資料

### `aaa-triage`
- **Description**: 依任務複雜度與風險進行路由，決定模型/工具或是否需要人類審核。
- **Apply Scenario**: 需要先分流再執行的任務（修訂、重構、CI 修復）。
- **Usage Example**:
  - 「先做 triage 再決定用哪個模型」
- **Expected I/O**:
  - Input: prompt 或 diff stats（檔案類型/行數/檔案數）
  - Output: route + score + risk
- **Limitations**:
  - 規則為啟發式，允許人類覆寫

### `aaa-evals-governance-check`
- **Description**: 彙整治理規則相關檢查並輸出報告。
- **Apply Scenario**: 發版前、治理規則更新後、或懷疑 repo 不符合規範時。
- **Usage Example**:
  - 「跑一次治理檢查並輸出報告」
- **Expected I/O**:
  - Input: 目標 repo / org
  - Output: 檢查結果與缺失清單
- **Limitations**:
  - 只檢查已定義的 governance evals

### `aaa-prompts-schema-validate`
- **Description**: 檢查 aaa-prompts 中的 prompts 是否符合 `prompt.schema.json`。
- **Apply Scenario**: 新增/修改 prompt 後的驗證。
- **Usage Example**:
  - 「驗證 aaa-prompts 的 schema 合規性」
- **Expected I/O**:
  - Input: prompt 檔案或 repo 路徑
  - Output: 通過/失敗與錯誤明細
- **Limitations**:
  - 僅驗 schema，不評估內容品質

### `aaa-init-validate-plan`
- **Description**: 驗證 `plan.v0.1.json` 是否符合 `plan.schema.json`。
- **Apply Scenario**: 任何 `aaa init` 執行前的 fail-fast 檢查。
- **Usage Example**:
  - 「請先 validate-plan，確保欄位與 required checks 完整」
- **Expected I/O**:
  - Input: plan + schema 路徑
  - Output: pass/fail 與錯誤路徑
- **Limitations**:
  - 不做業務邏輯檢查（例如 repo 是否存在）

### `aaa-branch-protection-audit`
- **Description**: 檢查 repo 分支保護是否符合治理基線。
- **Apply Scenario**: repo 初始化後或治理規則更新後。
- **Usage Example**:
  - 「確認所有 repo 的 branch protection 設定」
- **Expected I/O**:
  - Input: org / repos
  - Output: 合規/不合規與差異清單
- **Limitations**:
  - 權限不足時只能回報，無法修復

### `aaa-workflow-tag-audit`
- **Description**: 檢查 workflows 是否使用 `aaa-actions@<tag>`。
- **Apply Scenario**: workflow 更新或發版前。
- **Usage Example**:
  - 「檢查 workflows 是否全部 pin 到 tag」
- **Expected I/O**:
  - Input: repo 路徑
  - Output: 未 pin 的 workflow 清單
- **Limitations**:
  - 僅檢查 uses 字串，不執行 workflow

### `aaa-docs-link-audit`
- **Description**: 檢查 docs 指向 `<org>-docs` 的連結一致性。
- **Apply Scenario**: 新專案初始化或 docs 結構更新後。
- **Usage Example**:
  - 「確認 service/frontend docs 連回 docs repo」
- **Expected I/O**:
  - Input: repo 路徑
  - Output: 缺失連結清單
- **Limitations**:
  - 只驗證連結存在與一致性

### `aaa-governance-audit`
- **Description**: 組合式治理稽核（README、CODEOWNERS、workflow pinning 等）。
- **Apply Scenario**: release 前或治理例外檢查。
- **Usage Example**:
  - 「跑治理稽核並輸出報告」
- **Expected I/O**:
  - Input: org / repos
  - Output: 稽核報告與缺失清單
- **Limitations**:
  - 不會自動修復
