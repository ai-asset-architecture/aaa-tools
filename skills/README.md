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

## Usage
- Codex CLI sync target: `.codex/skills/`
- Antigravity sync target: `.agent/skills/`

## Included Common Skills (v0.1)
- `aaa-evals-governance-check`
- `aaa-prompts-schema-validate`
- `aaa-init-validate-plan`
- `aaa-branch-protection-audit`
- `aaa-workflow-tag-audit`
- `aaa-docs-link-audit`
- `aaa-governance-audit`
- `aaa-asset-harvest`
- `aaa-triage`

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
