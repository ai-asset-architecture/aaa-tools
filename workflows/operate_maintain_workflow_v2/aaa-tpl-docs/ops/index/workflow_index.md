# Workflow Index (Canonical Source)

- updated_at_taipei: 2026-03-02T11:20:00+08:00
- source_of_truth: raw rows for `/ops-registry?tab=workflows`
- maintenance_rule: workflow change MUST append/update in Step1

| 日期 | ID | 工作流程 | 目的 | 目標 | 場合 | 觸發時機 | 模式 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-03-01 | .github/workflows/v2-1-0-guide-parity-gate.yml | v2.1.0 Guide Parity Gate | PR 自動比對 core/template guide canonical sections，不一致即 fail。 | 保證 workflow law 在核心與模板層長期一致，並提供 workflow_dispatch auto-fix PR 選項。 | operate_maintain_workflow_v2 governance | pull_request(main) + workflow_dispatch(auto_fix_pr) | auto+manual（latest_run:22546764942; conclusion:success; evidence:internal/development/reviews/2026-03-01-v2.1.0-guide-parity-gate-run-evidence.md） |
| 2026-03-01 | operate_maintain_workflow_v2 | AAA 4-Step Version Development Workflow | 定義 Step1~Step4 的唯一權威流程與 evidence gate。 | 確保版本治理可追溯、可審計、可被繼承專案匯入。 | AAA core + inherited projects | version development lifecycle | manual+automation |
| 2026-01-29 | governance:legacy_trust_boundary_archive | Legacy Trust-Boundary Archive Workflow | 將既有 v2.0.1 Trust Boundary 以歷史軌方式納入現行 registry/detail。 | 讓 legacy 版本可在同一治理介面中可視、可追溯、可比對。 | legacy_trust_boundary historical records | historical backfill / index sync | manual(backfill)+read-only |
| 2026-01-18 | governance:legacy_milestone_archive | Legacy Milestone Archive Workflow | 將 v0.1~v2.0.5 既有 milestone 資產回填到版本清單與版本儀表板。 | 補齊歷史版本可追溯性，避免僅有新流程版本可查。 | legacy_milestone historical records | historical backfill / index sync | manual(backfill)+read-only |
