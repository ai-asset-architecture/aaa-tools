# Operate & Maintain Guide v2.1.0
> AAA 版本開發與維運權威流程（AI/Agent 專用，無歧義可執行）。

## 文件中繼資料
- document_version: `v2.1.0`
- effective_date: `2026-03-01`
- replaces: `aaa-docs/bootstrap/operate_maintain_guide.md`（舊版）
- authority_level: `workflow-law`

## 0. 權威與優先序（MUST）
1. 本文件是 AAA 版本開發工作流唯一權威來源。
2. 任何自建 `task.md`、memo、agent checklist 不得覆寫本文件規則。
3. 優先序固定：`operate_maintain_guide.md > task.md > 臨時備忘`。
4. 違反本文件任一 blocking 規則，流程狀態必須標記為 `NOT READY` 或 `FAIL`。

## 1. 核心目標
1. 讓 AAA 本體與繼承專案可共用同一套版本治理流程。
2. 讓流程具 machine-checkable 特性，避免主觀判斷與語意漂移。
3. 以可執行證據鏈（remote run_ref + evidence paths）取代敘述式完成宣告。

## 2. Canonical Data Sources（MUST）
下列兩份 index 檔是版本/工作流程頁面的原始資料來源（raw data SSOT）：
- `aaa-tpl-docs/version_index.md`
- `aaa-tpl-docs/workflow_index.md`

規則：
1. 新版本開發時，Step1 必須先更新對應 index。
2. Step2~Step4 的完成狀態與 evidence 必須回寫對應 index 行。
3. `ops-registry` / `ops-version` 類頁面資料不得繞過上述 index 另建平行來源。

## 3. Release Type
- `NORMAL_RELEASE`：需完成 Step1 + Step2 + Step3 + Step4。
- `BRIDGE_RELEASE`：只做治理補洞，可停在 Step1；Step4 狀態僅可 `COMPLETED_STEP1` 或 `BRIDGE_ONLY`。

## 4. Strict Discipline（全部為 MUST）
1. Step1/Step2 邊界隔離：Step1 只允許治理資產，不得碰 runtime domain code。
2. No-Glob Policy：deliverables/evidence 路徑不得使用 `*`、`**`。
3. Step2 run_ref remote-only：僅允許 `gh-actions:<repo>@<workflow_file>#<run_id>`。
4. Completion Claim Guard：若缺 remote evidence，不得使用 `COMPLETED/PASS/已落地` 語意。
5. Full-File Consistency：修改多視圖文件（如 index + registry）必須全檔一致。
6. Guide Parity Gate（v2.1.0+）：`aaa-docs/bootstrap/operate_maintain_guide.md` 與 `aaa-tpl-docs/operate_maintain_guide.md` 的 canonical sections 必須通過 CI parity gate；不一致一律 FAIL。

## 5. 4-Step Lifecycle

### Step 1: Contract Baseline（契約基線）
**目標**：先鎖規格、邊界與驗收，再進入實作。

允許範圍（Step1）：
- `docs/plans/**`
- `docs/audits/**`
- `docs/reviews/**`
- `docs/contracts/**`
- `scripts/gates/**`
- `.github/workflows/**`（僅草案）

禁止範圍（Step1）：
- `src/**`
- `PRD/**`
- runtime/build config（如 `package.json`, `tsconfig*`, `next.config*`）

必備交付：
1. Plan：`docs/plans/YYYY-MM-DD-<version>-<name>-plan.md`
2. Audit：`docs/audits/YYYY-MM-DD-<version>-<name>-audit.md`
3. Diff Paths：`docs/reviews/YYYY-MM-DD-<version>-<name>-diff-paths.md`
4. Schema：至少 1 份 `*.schema.json`
5. Examples：至少 1 份 pass + 1 份 fail

Index 更新（Step1 Blocking）：
1. 必須追加/更新 `aaa-tpl-docs/version_index.md` 對應版本列。
2. 若涉及 workflow，必須追加/更新 `aaa-tpl-docs/workflow_index.md` 對應列。
3. 排序必須維持：日期 DESC；同日期下版本或 ID DESC。
4. Step1 允許 placeholder `run_ref=N/A (step2-pending)`，但不得宣稱 Step2 PASS。

#### Step 1 Exit Checklist（Machine-Scannable）
```yaml
ExitChecklistStep: 1
ExitChecklistVersion: v2.1.0
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
- [ ] Plan 已建立（No-Glob 路徑）
- [ ] Audit 已建立（含 1+2+1 coverage）
- [ ] Diff-Paths 已建立（含 allowlist/denylist/verdict）
- [ ] Schema + Pass/Fail examples 已建立
- [ ] Step1 邊界合規（無 `src/**` / `PRD/**`）
- [ ] `version_index.md` 已新增或更新對應版本列
- [ ] `workflow_index.md` 已新增或更新對應 workflow 列（若涉及）
- [ ] index 排序正確（日期/版本規則）
- [ ] Triple-Summary 已填寫

### Step 2: Implementation & Executable Evidence（實作與可執行證據）
**目標**：依 Step1 契約完成實作，並提供可重放證據。

硬規則：
1. run_ref 必須 remote-only：`gh-actions:<repo>@<workflow_file>#<run_id>`。
2. 禁止 `local:*`, `file:*`, `shell:*`, `gh://` 作為 Step2 新證據。
3. 任何 completion claim 必須附 remote run_ref + evidence_path。
4. 若新增/重大修改 workflow，至少 1 次 remote smoke run。

必備證據欄位：
- `run_ref`
- `computed_at_taipei`
- `inputs_digest`
- `source_paths`（No-Glob）
- `evidence_path`（No-Glob）

#### Step 2 Exit Checklist（Machine-Scannable）
```yaml
ExitChecklistStep: 2
ExitChecklistVersion: v2.1.0
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
- [ ] Step1 全項 PASS
- [ ] 實作變更符合 Step1 契約範圍
- [ ] run-evidence 文件已建立並含必要欄位
- [ ] run_ref 為 remote-only 合規格式
- [ ] workflow smoke run 已完成（若適用）
- [ ] `version_index.md` 對應列已更新 Step2 狀態與 run_ref/evidence
- [ ] `workflow_index.md` 對應列已更新 latest_run/evidence（若適用）

### Step 3: Asset Preservation（資產保存）
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

#### Step 3 Exit Checklist（Machine-Scannable）
```yaml
ExitChecklistStep: 3
ExitChecklistVersion: v2.1.0
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
- [ ] Valuable Assets 已分類（Templates/Prompts/Contracts/Workflows/Evals/Runbooks/UI）
- [ ] 每項資產已標註 `source_step`（Step1 或 Step2）
- [ ] `asset-manifest.v0.1.json` 已建立（或有 No-Asset Justification）
- [ ] 證據檔已保存（`result.json`, `index.json`, `run-evidence.md`）
- [ ] digest 欄位已填寫（含 asset_digest 類欄位）
- [ ] 里程碑摘要文件已建立

### Step 4: Completion & Delivery（結案與交付）
**目標**：鎖定版本、同步索引、完成可審計閉環。

必備文件：
1. `docs/milestones/YYYYMMDD_vX.Y_<name>.md`
2. `docs/milestones/completion-reports/vX.Y_completion_report_YYYYMMDD.md`
3. `docs/reviews/<YYYY-MM-DD>-<version>-playbook-compliance-checklist.md`

必做同步：
1. `version_index.md`：狀態更新為最終狀態（NORMAL: `COMPLETED` / BRIDGE: `COMPLETED_STEP1`）
2. `workflow_index.md`：對應 workflow 狀態/模式/latest_run 同步
3. 若宣稱 completed，必須可對應 Step2 remote evidence

Global MCP Validation（Step4 MUST）：
1. header 治理狀態
2. versions page（`/ops-registry?tab=versions`）
3. workflows page（`/ops-registry?tab=workflows`）
4. ops dashboard（`/ops-dashboard`）
5. version detail（`/ops-version/<version>`）

#### Step 4 Exit Checklist（Machine-Scannable）
```yaml
ExitChecklistStep: 4
ExitChecklistVersion: v2.1.0
ExitChecklistOwner: <ai-or-human-role>
ExitChecklistVerdict: PASS|FAIL|N/A
```
- [ ] completion report 已建立
- [ ] milestone 摘要已建立
- [ ] playbook compliance checklist 已建立（`docs/reviews/<date>-<version>-playbook-compliance-checklist.md`）
- [ ] index 同步完成（version/workflow）
- [ ] Step4 MCP 5頁驗證證據存在
- [ ] completion claim 與 remote evidence 一致

## 6. Import Model（給繼承專案）
能力名稱：`operate_maintain_workflow_v2`

規則：
1. 繼承專案可選擇是否匯入。
2. 未匯入時，不必提供 ops-registry/ops-version 能力。
3. 匯入後，必須遵守本文件 Step1~4 所有 MUST 規則。

## 7. 狀態列舉（Canonical Enums）
- `PLANNED`
- `UNVERIFIED`
- `COMPLETED_STEP1`
- `BRIDGE_ONLY`
- `COMPLETED`

## 8. 違規處置
1. 缺 Step1 index 追加：`Step1 FAIL`。
2. Step2 使用 non-remote run_ref：`Hard FAIL`。
3. completion claim 無 evidence：`Hard FAIL`。
4. index/頁面資料不一致：`Process Non-Compliance`，必須先修復再繼續。
