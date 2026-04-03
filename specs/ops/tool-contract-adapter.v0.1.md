# AAA Tool Contract Adapter v0.1

- status: `active`
- adapter_role: `implementation-facing mirror`
- canonical_contract_ref: `aaa-tpl-docs/internal/development/contracts/ops/tool-contract.v0.1.md`
- governing_law_ref: `aaa-tpl-docs/internal/development/contracts/ops/governance-source-precedence-and-change-law.v0.1.md`

## Purpose

This adapter translates canonical AAA tool contract law into implementation-facing binding expectations for `aaa-tools`. It does not define governance meaning; it binds runtime code, validators, and future CLI surfaces back to canonical tool law.

## Mirror Rules

- If this adapter conflicts with canonical contract, canonical contract prevails.
- This adapter may add implementation notes, but may not alter canonical authority, scope, applicability, or evidence law.
- Adapter consumers must treat canonical fields as required even if the runtime has not yet implemented them all.

## Canonical-to-Implementation Binding

| Canonical Field | Implementation Binding Expectation |
| --- | --- |
| `tool_id` | Stable runtime id or registry key |
| `tool_scope` | Enforced target boundary check before execution |
| `applicability_target[]` | Runtime target validation gate |
| `permission_requirements` | Approval/permission policy integration |
| `authority_class` | Runtime legality guard |
| `execution_class` | Scheduler/executor posture hint |
| `evidence_class` | Artifact/evidence emission requirement |

## Initial AAA Implementation Guidance

- repo-check / validator style tools should bind to `analysis_only` or `governance_gate`
- registry rebuild style tools should bind to `mutation_repo` with `registry_update`
- audit export / completion closeout tools should bind to explicit `evidence_class` rather than stdout-only assumptions
- multi-repo tools must validate `tool_scope` and `applicability_target[]` before mutating any target
