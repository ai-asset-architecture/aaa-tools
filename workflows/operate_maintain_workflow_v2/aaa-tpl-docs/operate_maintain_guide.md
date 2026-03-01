# Operate & Maintain Guide v2.0.1
> AAA 版本開發與維運工作流（AI / AI Agent 專用，無歧義可執行模板）

## 文件中繼資料
- document_version: `v2.0.1`
- effective_date: `2026-03-01`
- authority_level: `workflow-law`
- capability_name: `operate_maintain_workflow_v2`
- applies_to:
  - `AAA core`
  - `AAA inherited projects`（選擇匯入後生效）

## 0. 權威與優先序（MUST）
1. 本文件是版本開發流程唯一權威來源（Single Source of Workflow Truth）。
2. 任何 `task.md` / memo / 自建 checklist 不得覆蓋或改寫本文件規則。
3. 固定優先序：`operate_maintain_guide.md > task.md > memo`。
4. 違反 blocking 規則時，狀態必須標記為 `NOT READY` 或 `FAIL`，不得宣稱完成。

## 1. 核心目標
1. AAA 本體與繼承專案使用同一套 4-Step 版本治理語言。
2. 流程與證據可機器檢查（machine-checkable），避免敘述式完成宣告。
3. 版本/工作流程可在 registry 與 version 頁面完整追溯。

## 2. Canonical Sources（MUST）
以下兩份檔案是 `ops-registry` / `ops-version` 類頁面的 raw data SSOT：
- `aaa-tpl-docs/version_index.md`
- `aaa-tpl-docs/workflow_index.md`

硬規則：
1. 每次版本開發 Step1，必須新增或更新 `version_index.md` 對應列。
2. 若版本涉及 workflow，Step1 必須同步新增或更新 `workflow_index.md` 對應列。
3. Step2~Step4 的 run_ref / evidence / final status 必須回寫 index 對應列。
4. 不得繞過上述 index 建立平行資料來源。

## 3. Release Type
- `NORMAL_RELEASE`：Step1 + Step2 + Step3 + Step4 全完成。
- `BRIDGE_RELEASE`：治理補洞型版本；可停在 Step1，Step4 僅可標記 `COMPLETED_STEP1` 或 `BRIDGE_ONLY`。

## 4. Strict Discipline（全部 MUST）
1. **Step1/Step2 邊界隔離**：Step1 只允許治理資產，禁止修改 runtime domain code。
2. **No-Glob**：所有 deliverables/evidence 路徑禁止 `*`、`**`，必須具體檔名。
3. **Remote-Only Evidence（Step2+）**：run_ref 僅允許 `gh-actions:<repo>@<workflow_file>#<run_id>`。
4. **Completion Claim Guard**：缺 remote evidence 禁止使用 `COMPLETED/PASS/已落地` 語意。
5. **Full-File Consistency**：涉及 index 或 dashboard raw data 的更新，必須維持全檔排序與語意一致。
6. **Guide Parity Gate（v2.0.1+）**：`aaa-docs/bootstrap/operate_maintain_guide.md` 與 `aaa-tpl-docs/operate_maintain_guide.md` 的 canonical sections 必須通過 CI parity gate；不一致一律 FAIL。

## 5. 4-Step Lifecycle

### Step 1: Contract Baseline（契約基線）
**目標**：先鎖規格與驗收，再進入實作。

允許（Step1）：
- `docs/plans/**`
- `docs/audits/**`
- `docs/reviews/**`
- `docs/contracts/**`
- `docs/templates/**`
- `scripts/gates/**`
- `.github/workflows/**`（僅草案狀態）

禁止（Step1）：
- `src/**`
- `PRD/**`
- runtime/build config（`package.json`, `tsconfig*`, `next.config*`, `eslint*`）

必備交付（No-Glob）：
1. `docs/plans/YYYY-MM-DD-<version>-<name>-plan.md`
2. `docs/audits/YYYY-MM-DD-<version>-<name>-audit.md`
3. `docs/reviews/YYYY-MM-DD-<version>-<name>-diff-paths.md`
4. 至少 1 份 `*.schema.json`
5. 至少 1 組 pass example + 1 組 fail example

Step1 Index Blocking（MUST）：
1. `aaa-tpl-docs/version_index.md` 必須有新版本列（或更新既有列）。
2. 涉及 workflow 時，`aaa-tpl-docs/workflow_index.md` 必須有新列（或更新既有列）。
3. 排序規則：日期 DESC；同日期下版本/ID DESC。
4. Step1 可使用 `run_ref=N/A (step2-pending)`，但不得宣稱 Step2 PASS。

#### Step 1 Exit Checklist
```yaml
ExitChecklistStep: 1
ExitChecklistVersion: v2.0.1
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
- [ ] Plan 已建立（No-Glob）
- [ ] Audit 已建立（含驗收標準）
- [ ] Diff-Paths 已建立（含 allowlist/denylist/verdict）
- [ ] Schema + pass/fail examples 已建立
- [ ] 無 runtime domain code 變更（Step1 邊界合規）
- [ ] `version_index.md` 已更新
- [ ] `workflow_index.md` 已更新（若適用）
- [ ] 排序與欄位語意一致

### Step 2: Implementation & Executable Evidence
**目標**：依契約完成實作並產生可重放證據。

必備欄位（MUST）：
- `run_ref`（remote-only）
- `computed_at_taipei`
- `inputs_digest`
- `source_paths`（No-Glob）
- `evidence_path`（No-Glob）

硬規則：
1. 僅允許 `gh-actions:<repo>@<workflow_file>#<run_id>`。
2. 禁止 `local:*`, `file:*`, `shell:*`, `gh://` 作為 Step2 新證據。
3. 新增/重大修改 workflow 時，至少 1 次 remote smoke run。
4. Step2 完成後需更新 index 對應列（status/run_ref/evidence）。

#### Step 2 Exit Checklist
```yaml
ExitChecklistStep: 2
ExitChecklistVersion: v2.0.1
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
- [ ] Step1 全項 PASS
- [ ] 實作與 Step1 契約一致
- [ ] run-evidence 具備必要欄位
- [ ] run_ref remote-only 合規
- [ ] workflow smoke run 已完成（若適用）
- [ ] index 對應列完成 Step2 回寫

### Step 3: Asset Preservation
**目標**：把 Step1/Step2 產生的可重用成果轉成 AAA 資產，形成可回放、可匯入、可審計的資產鏈。

AAA Valuable Assets（MUST）：
1. Templates：
   - 例：`docs/templates/**`、可被繼承專案直接套用的 SOP/規格模板。
2. Prompts：
   - 例：`prompts/**`、agent/system prompt bundles、審核提示詞。
3. Contracts：
   - 例：`docs/contracts/**/*.schema.json`、reason-codes、pass/fail fixtures。
4. Workflows/Gates：
   - 例：`.github/workflows/*.yml`、`scripts/gates/**`。
5. Evals/Test Assets：
   - 例：`evals/**`、測試資料、驗證案例與 replay inputs。
6. Runbooks/Operational Guides：
   - 例：`docs/runbooks/**`、`docs/reviews/*-checklist.md`。
7. UI/Observability Assets（若有）：
   - 例：dashboard spec、MCP screenshots、ops/version page mapping docs。

來源規則（MUST）：
1. Step1 產物：以「治理可重用」為主（templates/contracts/gates/workflow specs）。
2. Step2 產物：以「可執行證據可重用」為主（run evidence/evals/replay assets）。
3. Step3 必須明確標示每項資產來自 Step1 或 Step2，不得混寫為不明來源。

最小保存交付（MUST）：
1. `docs/evidence/<version>/<asset>/result.json`
2. `docs/evidence/<version>/<asset>/index.json`
3. `docs/evidence/<version>/<asset>/run-evidence.md`
4. `docs/evidence/<version>/<asset>/asset-manifest.v0.1.json`
   - 至少欄位：`asset_id`, `asset_type`, `source_step`, `source_paths`, `reuse_target`, `owner`, `digest`

Value Gate（MUST）：
1. 若本版本沒有任何可沉澱 AAA 資產，必須在 Step3 checklist 填寫 `No-Asset Justification`（不可留空）。
2. 若有資產，`asset-manifest.v0.1.json` 至少 1 筆 `reuse_target` 必須是 `AAA core` 或 `AAA inherited projects`。
3. 每筆資產都要有對應 digest（如 `inputs_digest`, `policy_digest`, `dataset_digest`, `asset_digest`）。

#### Step 3 Exit Checklist
```yaml
ExitChecklistStep: 3
ExitChecklistVersion: v2.0.1
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
- [ ] Value Check 完成
- [ ] Valuable Assets 已分類（Templates/Prompts/Contracts/Workflows/Evals/Runbooks/UI）
- [ ] 每項資產已標註 `source_step`（Step1 或 Step2）
- [ ] `asset-manifest.v0.1.json` 已建立（或有 No-Asset Justification）
- [ ] 證據檔已保存（`result.json`, `index.json`, `run-evidence.md`）
- [ ] digest 欄位齊全（含 asset_digest 類欄位）
- [ ] milestone 摘要已建立

### Step 4: Completion & Delivery
**目標**：完成版本閉環交付並可跨頁追溯。

必備文件：
1. `docs/milestones/YYYYMMDD_vX.Y_<name>.md`
2. `docs/milestones/completion-reports/vX.Y_completion_report_YYYYMMDD.md`

必做同步（MUST）：
1. `version_index.md` 更新最終狀態（NORMAL=`COMPLETED`；BRIDGE=`COMPLETED_STEP1`/`BRIDGE_ONLY`）。
2. `workflow_index.md` 同步 workflow 的 latest_run/evidence/mode/status。
3. 任何 completion claim 必須對應 Step2 remote evidence。

Global MCP Validation（Step4 MUST）：
1. Header（治理狀態）
2. `/ops-registry?tab=versions`
3. `/ops-registry?tab=workflows`
4. `/ops-dashboard`
5. `/ops-version/<version>`

#### Step 4 Exit Checklist
```yaml
ExitChecklistStep: 4
ExitChecklistVersion: v2.0.1
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
- [ ] completion report 已建立
- [ ] milestone 摘要已建立
- [ ] version/workflow index 同步完成
- [ ] MCP 5 頁驗證證據存在
- [ ] completion claim 與 remote evidence 一致

## 6. Import Model（給繼承專案）
Capability: `operate_maintain_workflow_v2`

規則：
1. 繼承專案可選擇是否匯入本 workflow。
2. 未匯入時，可不提供 ops-registry / ops-version 相關能力。
3. 一旦匯入，必須遵守本文件 Step1~4 所有 MUST 規則。
4. 推薦透過 `aaa-tools` 匯入命令安裝本 capability（避免手動遺漏）。

## 7. Canonical Status Enums
- `PLANNED`
- `UNVERIFIED`
- `COMPLETED_STEP1`
- `BRIDGE_ONLY`
- `COMPLETED`

## 8. Violation Handling
1. Step1 未更新 index：`Step1 FAIL`。
2. Step2 使用非 remote run_ref：`Hard FAIL`。
3. completion claim 缺 evidence：`Hard FAIL`。
4. index 與頁面資料語意不一致：`Process Non-Compliance`，必須先修復再繼續。
