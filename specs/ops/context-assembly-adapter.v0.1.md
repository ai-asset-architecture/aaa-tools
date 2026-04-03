# AAA Context Assembly Adapter v0.1

- status: `active`
- adapter_role: `implementation-facing mirror`
- canonical_contract_ref: `aaa-tpl-docs/internal/development/contracts/ops/context-assembly-contract.v0.1.md`
- governing_law_ref: `aaa-tpl-docs/internal/development/contracts/ops/governance-source-precedence-and-change-law.v0.1.md`

## Purpose

This adapter translates canonical context-assembly law into implementation-facing rules for context loaders, session/runtime helpers, and validators in `aaa-tools`.

## Mirror Rules

- local operation logs must remain non-canonical inside implementation code
- runtime summaries may assist operators, but may not override canonical source precedence
- adapter code must preserve the canonical distinction between current truth and supporting evidence

## Canonical-to-Implementation Binding

| Canonical Concept | Implementation Binding Expectation |
| --- | --- |
| `source_class` | Typed source bucket or equivalent validation class |
| `allowed_as_current_truth` | Promotion gate |
| `allowed_as_supporting_evidence` | Supplemental-input gate |
| `promotion_allowed` | Explicit promotion check |
| `precedence_rank` | Resolution order |
| `contamination_rules_ref` | Hard anti-contamination guard |

## Initial AAA Implementation Guidance

- session/runtime helpers must not load root local logs as canonical repo truth
- generated summaries should be tagged as derived material, not canonical source
- context bundle builders should validate source precedence before command execution
