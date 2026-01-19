# AGENT_BOOTSTRAP.md — AAA Project Bootstrap Runbook (v0.1)

本 Runbook 用於讓本地 Codex CLI 在「可聯網」環境下，依照 AAA v0.1 的治理與模板規範，完成新專案初始化。
核心原則：**Deterministic（aaa init）為主，LLM（Codex）只做例外處理與報告生成。**

---

## 0. 角色分工（很重要）

### A) aaa init（Script-first，必須確定性）
負責「可重跑 / 可驗證」的初始化核心：
- 建立 repos（或確認已存在）
- 套用模板（aaa-tpl-docs / service / frontend）
- 寫入標準檔案（README、docs 指向、最小骨架）
- 同步 workflows / skills（aaa sync）
- 設定 branch protection（required checks: lint/test/eval）
- 建立 PR（建議）或 push（不建議直接推 main）

### B) Codex（LLM-last，處理例外）
只負責：
- 讀取 runbook + plan
- 觸發 `aaa init` 並收集輸出（stdout/stderr、產出檔案、PR/CI 狀態）
- 若 `aaa init` 回傳非 0 或檢查不通過：
  - 依「例外處理規則」定位問題
  - 以最小變更修補（prefer: PR）
- 產出最終 JSON 報告（符合 output.schema.json）

---

## 1. 必要前置條件（Preflight）

Codex 在開始前必須檢查並紀錄：

### 1.1 本地工具
- `git`、`gh`（GitHub CLI）、`python3`（>= 3.10）
- `aaa` CLI 可用（例如：`aaa --version` 回傳版本）
- 已登入 GitHub（`gh auth status` 成功）

### 1.2 權限與安全
- GitHub Token 權限需最小化（至少能建 repo、開 PR、設 branch protection）。
- 僅允許與下列網路端點互動：
  - GitHub API / git remote
  - OpenAI/Codex 端點（由 Codex CLI 使用）
  - 其他外部下載行為需在報告中標記 `external_downloads: true` 並列出來源（v0.1 預設不應發生）

---

## 2. 輸入參數（Inputs）

Codex 必須取得下列輸入（可來自環境變數或 CLI 參數）：

- `AAA_VERSION`：例如 `v0.1.0`
- `AAA_ORG`：固定 `ai-asset-architecture`
- `TARGET_ORG`：新專案 GitHub Organization 名稱
- `PROJECT_SLUG`：專案代號（小寫、kebab-case）
- `REPOS`：要初始化的 repos 清單（至少 docs/service/frontend）
- `DEFAULT_BRANCH`：預設 `main`
- `MODE`：`pr`（預設）或 `direct`（不建議）
- `VISIBILITY`：`private`（預設）或 `public`
- `WORKSPACE_DIR`：本地工作區路徑（絕對或相對路徑）

---

## 3. 執行計畫來源（Plan Source of Truth）

本 runbook 配套 machine-readable 計畫檔：
- `plan.v0.1.json`

Codex 必須：
1) 讀取 `plan.v0.1.json`
2) 依序執行每個 step（不得跳步）
3) 將每個 step 的結果寫入最終報告

---

## 4. 主流程（Happy Path）

### Step A — Preflight
1) `gh auth status`
2) `aaa --version`
3) `python3 --version`

若任何一項失敗 → 走「例外處理 E1」。

### Step B — Run aaa init（核心）
Codex 必須呼叫（示例，實際參數以 plan 為準）：

- 建議 PR 模式：
  - `WORKSPACE_DIR="<WORKSPACE_DIR>" aaa init --plan aaa-tools/runbooks/init/plan.v0.1.json --mode pr`

aaa init 預期行為：
- 建 repo（若不存在）
- 套模板並寫檔
- 同步 workflows / skills
- 套 branch protection
- 建 PR（每個 repo 一個 PR 或單一統一 PR，依 plan 設定）

若 `aaa init` exit code != 0 → 走「例外處理 E2」。

### Step C — CI 驗證
- 確認每個 repo 的 PR 有觸發 CI
- required checks 必須存在並通過：`lint` / `test` / `eval`

若缺 check 或未通過 → 走「例外處理 E3」。

### Step D — 產出最終報告（JSON）
Codex 必須輸出一份 JSON，並通過 `output.schema.json` 驗證。
報告內容至少包含：
- inputs
- created/updated repos
- PR URLs
- branch protection 狀態
- CI checks 狀態
- exceptions / fixes（若有）

---

## 5. 例外處理規則（Exception Playbook）

### E1) 環境缺失 / 未登入
處理順序：
1) 若 `gh auth status` 失敗 → 要求使用者完成 `gh auth login`（不得自行嘗試繞過）
2) 若 `aaa` 不存在 → 提示安裝或在 repo root 執行 `pip install -e .`（取決於你的發佈策略）
3) 重新執行 Step A

報告標記：
- `exceptions[].code = "E1_PRECHECK_FAILED"`

### E2) aaa init 失敗
Codex 必須：
1) 收集 `aaa init` 完整 stderr/stdout（必要時存檔）
2) 根據錯誤碼判斷類型（常見）：
   - repo 已存在但無權限
   - template 拉取失敗（tag 不存在）
   - branch protection API 權限不足
   - workflows 引用錯誤（tag/ref）
3) 優先採取「修正設定 / 重跑」策略，不直接手改大量檔案
4) 若為 Network/Timeout 類錯誤：
   - 重試至多 3 次（每次間隔 5 秒）
   - 仍失敗則產出 `manual_bootstrap.sh`（寫入 WORKSPACE_DIR），內容包含失敗的指令
   - 回報「已降級為手動模式」，請使用者執行腳本
5) 修復後再次 `aaa init --plan ...`（必須可重跑）

報告標記：
- `exceptions[].code = "E2_AAA_INIT_FAILED"`

### E3) CI 或 required checks 不符合
常見原因與處理：
- required checks 名稱不匹配（必須是 `lint/test/eval`）
- workflow uses tag 不存在或拼錯（必須 pinned 到 `@AAA_VERSION`）
- repo 缺 `.github/workflows/ci.yml`

Codex 必須：
1) 在 PR 上修補（prefer PR，不直接推 main）
2) 確認 CI 再次通過

報告標記：
- `exceptions[].code = "E3_CI_GATES_FAILED"`

---

## 6. Codex 執行建議（非必要，但可參考）

建議以「自動化 + 結構化輸出」方式執行（示意）：
- `codex exec --full-auto --json --output-schema aaa-tools/runbooks/init/output.schema.json "<instructions>"`

Codex 輸出必須是單一最終 JSON（stdout）。
中間過程可用 `--json` events 記錄，但最終輸出需符合 schema。

---

## 7. 完成定義（Definition of Done）
- repos 皆存在（docs/service/frontend）
- 每個 repo：
  - `main` branch protection 套用完成（或報告明確列出失敗原因）
  - required checks：lint/test/eval 可見且通過（或報告列出阻塞原因）
  - docs repo 具備 ACC/PP/.ai-context 與 PRD/ADR 模板
  - service/frontend repo 有最小可跑骨架、且 docs 指向 `<TARGET_ORG>-docs`
- 最終 JSON 報告通過 schema 驗證
