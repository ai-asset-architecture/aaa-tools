# aaa CLI 背景與使用說明

簡單說：沒有 CLI 實作，這整套規格只是「文檔」；有了 CLI，才變成「可執行架構」。
你要的不是一份漂亮文件，而是「按下去就能把新專案建好、驗完、出報告」的工具。

以下說明為什麼一定要做 CLI 實作，以及它實際用在哪裡。

---

## 為什麼需要 CLI 實作？

### 1) 把規格變成「可執行」

你已經寫好：
- `CLI_CONTRACT.md`
- `plan.v0.1.json`
- `plan.schema.json`
- `output.schema.json`

但這些只是定義「應該怎樣」，沒有程式就無法自動完成任何事。
CLI 實作就是把「應該怎樣」變成「實際會怎樣」。

---

### 2) 確定性（Deterministic）流程

你要的是可重跑、可驗證、可回溯。
如果只靠 LLM，每次可能出不同結果。
CLI 實作就像「機器流水線」，每次執行都一致。

---

### 3) 給 Codex 用「穩定接口」

Codex 要自動化時，需要確定的入口：
- `aaa init validate-plan`
- `aaa init ensure-repos`
- `aaa init apply-templates`
- `aaa init protect`
- `aaa init verify-ci`

Codex 不適合自己臨時做決策，它需要你提供可呼叫的工具。
CLI 就是 Codex 的「手」。

---

## CLI 實作用在哪裡？

### A) 新專案初始化

你可以一鍵跑：

```bash
aaa init --plan runbooks/init/plan.v0.1.json --mode pr
```

這會自動完成：
- 建 repo
- 套模板
- 同步 workflows
- 設 branch protection
- 開 PR
- 驗 CI
- 輸出報告

---

### B) 治理驗證（品質門檻）

你可以在 CI 或本地跑：

```bash
aaa init validate-plan --plan plan.v0.1.json
```

確保計畫本身合法，避免跑到一半才崩。

---

### C) 讓 Codex 變成「執行者」

你可以只下指令：

> 「照 `CLI_CONTRACT.md` 實作全部命令」

Codex 就會幫你完成大量重複工作，你只需要 review 結果。

---

## 總結一句話

CLI 實作是把 AAA 變成真正可執行的系統。
沒有 CLI，你只是有文件；
有 CLI，你就有「可自動化開案」的能力。
