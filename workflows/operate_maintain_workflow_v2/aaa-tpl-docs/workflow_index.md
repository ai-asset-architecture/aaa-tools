# Workflow Index (Canonical Source)

- updated_at_taipei: 2026-03-01T22:20:00+08:00
- source_of_truth: raw rows for `/ops-registry?tab=workflows`
- maintenance_rule: workflow change MUST append/update in Step1

| 日期 | ID | 工作流程 | 目的 | 目標 | 場合 | 觸發時機 | 模式 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-03-01 | .github/workflows/v2-0-1-guide-parity-gate.yml | v2.0.1 Guide Parity Gate | PR 自動比對 core/template guide canonical sections，不一致即 fail。 | 保證 workflow law 在核心與模板層長期一致，並提供 workflow_dispatch auto-fix PR 選項。 | operate_maintain_workflow_v2 governance | pull_request(main) + workflow_dispatch(auto_fix_pr) | auto+manual |
| 2026-03-01 | operate_maintain_workflow_v2 | AAA 4-Step Version Development Workflow | 定義 Step1~Step4 的唯一權威流程與 evidence gate。 | 確保版本治理可追溯、可審計、可被繼承專案匯入。 | AAA core + inherited projects | version development lifecycle | manual+automation |
