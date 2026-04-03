# AAA Command Registry Adapter v0.1

- status: `active`
- adapter_role: `implementation-facing mirror`
- canonical_contract_ref: `aaa-tpl-docs/internal/development/contracts/ops/command-registry-contract.v0.1.md`
- governing_law_ref: `aaa-tpl-docs/internal/development/contracts/ops/governance-source-precedence-and-change-law.v0.1.md`

## Purpose

This adapter translates canonical command-registry law into implementation-facing binding requirements for `aaa-tools`. Commands are treated as governance-intent entrypoints whose dependencies must remain machine-parseable and canonically bound.

## Mirror Rules

- this adapter may not replace or weaken canonical dependency binding rules
- free-text explanations are supplemental only
- `tool_chain_refs[]`, `context_bundle_refs[]`, `artifact_contract_refs[]`, and `governance_dependency_refs[]` remain mandatory at canonical layer even if tooling support lands incrementally

## Canonical-to-Implementation Binding

| Canonical Field | Implementation Binding Expectation |
| --- | --- |
| `command_id` | Stable command registry key |
| `intent_class` | Control-plane routing / policy grouping |
| `target_scope` | Preflight legality check |
| `required_context_bundle` | Context loader requirement |
| `allowed_authority` | Maximum allowed tool authority for command chain |
| `default_tool_chain` | Default execution order |
| `expected_output_artifact` | Artifact emission / update contract |
| `failure_escalation_path` | Error-class to escalation mapping |
| `*_refs[]` | Machine-parseable dependency linkage |

## Initial AAA Implementation Guidance

- CLI command descriptors should expose explicit dependency refs, not just prose docs
- control-plane commands should fail closed if required dependency refs are unresolved
- command implementations must not silently widen authority beyond referenced tools
