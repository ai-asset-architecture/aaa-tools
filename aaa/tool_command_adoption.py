import json
from pathlib import Path
from typing import Any


TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    "ops.registry.inspect": {
        "tool_scope": "repo_level",
        "applicability_target": ["registry_snapshot"],
        "authority_class": ["analysis_only"],
        "evidence_class": ["artifact_report"],
    },
    "ops.registry.rebuild": {
        "tool_scope": "repo_level",
        "applicability_target": ["registry_snapshot"],
        "authority_class": ["mutation_repo"],
        "evidence_class": ["registry_update", "artifact_report"],
    },
    "governance.validate-tool-command-adoption": {
        "tool_scope": "repo_level",
        "applicability_target": ["canonical_repo_root", "legal_worktree_instance"],
        "authority_class": ["read_only", "analysis_only"],
        "evidence_class": ["audit_evidence", "completion_evidence"],
    },
    "governance.validate-multi-repo-worktree-identity": {
        "tool_scope": "worktree_level",
        "applicability_target": ["canonical_repo_root", "legal_worktree_instance"],
        "authority_class": ["read_only", "analysis_only"],
        "evidence_class": ["audit_evidence", "completion_evidence"],
    },
    "governance.validate-context-runtime-preflight": {
        "tool_scope": "artifact_level",
        "applicability_target": ["docs_artifact", "registry_snapshot"],
        "authority_class": ["read_only", "analysis_only"],
        "evidence_class": ["audit_evidence", "completion_evidence"],
    },
    "governance.validate-session-readiness-state": {
        "tool_scope": "artifact_level",
        "applicability_target": ["completion_report", "audit_bundle"],
        "authority_class": ["read_only", "analysis_only"],
        "evidence_class": ["audit_evidence", "completion_evidence"],
    },
}


COMMAND_REGISTRY: dict[str, dict[str, Any]] = {
    "aaa.ops.registry.rebuild": {
        "tool_chain_refs": ["ops.registry.inspect", "ops.registry.rebuild"],
        "allowed_authority": ["analysis_only", "mutation_repo"],
        "expected_output_artifact": ["registry_snapshot", "artifact_report"],
        "governance_dependency_refs": [
            "aaa-tpl-docs/internal/development/contracts/ops/tool-contract.v0.1.md",
            "aaa-tpl-docs/internal/development/contracts/ops/command-registry-contract.v0.1.md",
        ],
    },
    "readiness-inspect": {
        "tool_chain_refs": [
            "governance.validate-tool-command-adoption",
            "governance.validate-multi-repo-worktree-identity",
            "governance.validate-context-runtime-preflight",
            "governance.validate-session-readiness-state",
        ],
        "allowed_authority": ["read_only", "analysis_only"],
        "expected_output_artifact": ["readiness_state_report"],
        "governance_dependency_refs": [
            "aaa-tpl-docs/internal/development/contracts/ops/tool-contract.v0.1.md",
            "aaa-tpl-docs/internal/development/contracts/ops/command-registry-contract.v0.1.md",
            "aaa-tpl-docs/internal/development/contracts/ops/context-assembly-contract.v0.1.md",
            "aaa-tpl-docs/internal/development/contracts/ops/governance-source-precedence-and-change-law.v0.1.md",
        ],
    }
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    tool_refs = bundle.get("tool_refs", [])
    command_refs = bundle.get("command_refs", [])
    binding_mode = bundle.get("binding_mode")
    allowed_authority_map = bundle.get("allowed_authority_map", {})
    evidence_targets = bundle.get("evidence_targets", [])

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})

    if binding_mode != "machine_parseable":
        errors.append({"code": "binding_mode", "message": "binding_mode must be machine_parseable"})

    unresolved_tools = [tool_id for tool_id in tool_refs if tool_id not in TOOL_REGISTRY]
    if unresolved_tools:
        errors.append({"code": "tool_refs", "message": f"unresolved tools: {', '.join(unresolved_tools)}"})

    unresolved_commands = [command_id for command_id in command_refs if command_id not in COMMAND_REGISTRY]
    if unresolved_commands:
        errors.append({"code": "command_refs", "message": f"unresolved commands: {', '.join(unresolved_commands)}"})

    for command_id in command_refs:
        if command_id not in COMMAND_REGISTRY:
            continue
        command_spec = COMMAND_REGISTRY[command_id]
        required_tools = command_spec["tool_chain_refs"]
        missing_tools = [tool_id for tool_id in required_tools if tool_id not in tool_refs]
        if missing_tools:
            errors.append(
                {
                    "code": "tool_chain_refs",
                    "message": f"{command_id} missing required tool refs: {', '.join(missing_tools)}",
                }
            )

        declared_authorities = allowed_authority_map.get(command_id)
        if not declared_authorities:
            errors.append(
                {
                    "code": "allowed_authority_map",
                    "message": f"{command_id} missing allowed authority mapping",
                }
            )
            continue

        tool_authorities = {
            authority
            for tool_id in required_tools
            for authority in TOOL_REGISTRY.get(tool_id, {}).get("authority_class", [])
        }
        illegal_authorities = [item for item in declared_authorities if item not in tool_authorities]
        if illegal_authorities:
            errors.append(
                {
                    "code": "allowed_authority_map",
                    "message": f"{command_id} authority exceeds tool chain: {', '.join(illegal_authorities)}",
                }
            )

        unsupported_command_authorities = [
            item for item in declared_authorities if item not in command_spec["allowed_authority"]
        ]
        if unsupported_command_authorities:
            errors.append(
                {
                    "code": "allowed_authority_map",
                    "message": f"{command_id} authority exceeds command contract: {', '.join(unsupported_command_authorities)}",
                }
            )

        missing_evidence = [
            target for target in command_spec["expected_output_artifact"] if target not in evidence_targets
        ]
        if missing_evidence:
            errors.append(
                {
                    "code": "evidence_targets",
                    "message": f"{command_id} missing evidence targets: {', '.join(missing_evidence)}",
                }
            )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_tools": tool_refs,
        "resolved_commands": command_refs,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "registry_snapshot": {
            "tools": sorted(TOOL_REGISTRY.keys()),
            "commands": sorted(COMMAND_REGISTRY.keys()),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    bundle = load_bundle(bundle_path)
    result = validate_bundle(bundle)
    result["bundle_path"] = str(Path(bundle_path))
    return result
