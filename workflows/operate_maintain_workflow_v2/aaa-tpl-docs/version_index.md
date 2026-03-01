# Version Index (Canonical Source)

- updated_at_taipei: 2026-03-01T22:20:00+08:00
- source_of_truth: raw rows for `/ops-registry?tab=versions` and `/ops-version/<version>`
- maintenance_rule: new version development MUST append/update in Step1

| 日期 | 版本 | 名稱 | 意義 | 為何要做 | 版本落地處 | 狀態 | 可用性驗證 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-03-01 | v2.0.1 | Guide Parity Gate (Core vs Template) | 建立兩份 workflow law guide 的 CI parity gate，確保 canonical sections 長期一致。 | 避免 `aaa-docs` 與 `aaa-tpl-docs` guide 長期漂移，導致繼承專案與核心治理語義分叉。 | governance:operate_maintain_workflow_v2 | COMPLETED_STEP1 | run_ref=N/A (step2-pending); evidence=operate_maintain_guide.md,workflow_index.md,scripts/gates/verify_operate_maintain_guides.py,.github/workflows/v2-0-1-guide-parity-gate.yml; note=PR-gate+workflow_dispatch-autofix-pr |
| 2026-03-01 | v2.0.0 | AAA Operate-Maintain Workflow Law Adoption | 將 AAA 版本開發流程統一為 4-Step v2.0.0 並定義可匯入能力。 | 讓 AAA 本體與繼承專案共享 machine-checkable 版本治理，避免流程語意漂移。 | governance:operate_maintain_workflow_v2 | COMPLETED_STEP1 | run_ref=N/A (step2-pending); evidence=operate_maintain_guide.md,workflow_index.md,version_index.md; note=bootstrap row |
