# INIT_PROJECT_HUMAN.md — 本地操作流程 (v0.1)

這份文件提供使用 Codex CLI 進行新專案初始化的最小操作流程。

## 1) 前置條件
- 已安裝 `gh` CLI 並完成登入（`gh auth status`）
- 已安裝 `git`
- 已安裝 `aaa` CLI，且可執行（`aaa --version`）
- 已允許 GitHub 網路存取

## 2) 一鍵執行（Codex）
建議用絕對路徑執行（避免工作區混亂），先設定 `AAA_ROOT` 與 `WORKSPACE_DIR`：

```bash
export AAA_ROOT=/path/to/aaa-tools
export WORKSPACE_DIR=/path/to/projects/<PREFIX>_WORKSPACE
```

`aaa init` 會使用 `WORKSPACE_DIR` 作為本地 repo 的基準目錄。

再替換佔位符後執行：

```bash
codex exec --full-auto --json \
  --output-schema $AAA_ROOT/runbooks/init/output.schema.json \
  "請依照 $AAA_ROOT/runbooks/init/INIT_PROJECT_CODEX.md 執行初始化流程。 \n輸入參數：PROJECT_NAME=<NAME>、PROJECT_PREFIX=<PREFIX>、TARGET_ORG=<ORG>、VISIBILITY=private、WORKSPACE_DIR=$WORKSPACE_DIR。 \n先執行 deterministic 的 aaa init 流程，遇到例外再處理，最後僅輸出 JSON 報告。"
```

## 3) 預期輸出
- Codex 在 stdout 輸出單一 JSON 物件，需符合 `output.schema.json`。
- 若發生錯誤，會在 JSON 的 `failures` 或 `exceptions` 欄位中說明。
- `aaa init --plan` 會在 `WORKSPACE_DIR` 產生 `aaa-init-report.json`。

## 參考文件
- `aaa-tools/runbooks/init/INIT_PROJECT_CODEX.md`
- `aaa-tools/runbooks/init/plan.v0.1.json`
- `aaa-tools/specs/CLI_CONTRACT.md`
- `.github/BOOTSTRAP_PROTOCOL.md`
