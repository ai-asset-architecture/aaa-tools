import json
from pathlib import Path
from typing import Any

from . import offering_package_selection_runtime_baseline
from . import topology_aware_offering_package_definition_resolution
from . import offering_package_status_and_evidence_runtime
from . import topology_aware_package_status_and_repo_checks


PACKAGE_LEVELS = ("lite", "core", "full")
TOPOLOGY_LEVELS = ("dedicated_repo", "repo_local", "hybrid")
MOTHER_DRAFT_REF = "aaa-docs/bootstrap/offering_definition_skeleton.md"

PACKAGE_BASELINES: dict[str, dict[str, Any]] = {
    "lite": {
        "workflow_inclusion_level": "reduced",
        "minimum_repo_set_by_topology": {
            "dedicated_repo": [".github", "aaa-actions", "aaa-tools", "aaa-tpl-docs", "aaa-tpl-service"],
            "repo_local": ["aaa-actions", "aaa-tools", "aaa-tpl-docs", "aaa-tpl-service"],
            "hybrid": [".github", "aaa-actions", "aaa-tools", "aaa-tpl-docs", "aaa-tpl-service"],
        },
        "governance_asset_placement_rules": {
            "dedicated_repo": ["org_repo_only"],
            "repo_local": ["repo_local_only"],
            "hybrid": ["hybrid_split"],
        },
    },
    "core": {
        "workflow_inclusion_level": "core",
        "minimum_repo_set_by_topology": {
            "dedicated_repo": [".github", "aaa-actions", "aaa-evals", "aaa-tools", "aaa-prompts", "aaa-tpl-docs", "aaa-tpl-service", "aaa-tpl-frontend"],
            "repo_local": ["aaa-actions", "aaa-evals", "aaa-tools", "aaa-prompts", "aaa-tpl-docs", "aaa-tpl-service", "aaa-tpl-frontend"],
            "hybrid": [".github", "aaa-actions", "aaa-evals", "aaa-tools", "aaa-prompts", "aaa-tpl-docs", "aaa-tpl-service", "aaa-tpl-frontend"],
        },
        "governance_asset_placement_rules": {
            "dedicated_repo": ["org_repo_only"],
            "repo_local": ["repo_local_only"],
            "hybrid": ["hybrid_split"],
        },
    },
    "full": {
        "workflow_inclusion_level": "full",
        "minimum_repo_set_by_topology": {
            "dedicated_repo": [".github", "aaa-actions", "aaa-evals", "aaa-tools", "aaa-prompts", "aaa-tpl-docs", "aaa-tpl-service", "aaa-tpl-frontend"],
            "repo_local": ["aaa-actions", "aaa-evals", "aaa-tools", "aaa-prompts", "aaa-tpl-docs", "aaa-tpl-service", "aaa-tpl-frontend"],
            "hybrid": [".github", "aaa-actions", "aaa-evals", "aaa-tools", "aaa-prompts", "aaa-tpl-docs", "aaa-tpl-service", "aaa-tpl-frontend"],
        },
        "governance_asset_placement_rules": {
            "dedicated_repo": ["org_repo_only"],
            "repo_local": ["repo_local_only"],
            "hybrid": ["hybrid_split"],
        },
    },
}


def _assert_package_level(level: str) -> str:
    package_level = str(level).strip()
    if package_level not in PACKAGE_LEVELS:
        raise ValueError("package level must be one of lite/core/full")
    return package_level


def _assert_topology_mode(mode: str) -> str:
    topology_mode = str(mode).strip()
    if topology_mode not in TOPOLOGY_LEVELS:
        raise ValueError("topology mode must be one of dedicated_repo/repo_local/hybrid")
    return topology_mode


def build_selection_payload(level: str) -> dict[str, Any]:
    package_level = _assert_package_level(level)
    return {
        "version": "v0.1",
        "runtime_plane_mode": "offering_package_selection",
        "line_class": "offering_package_runtime_enablement_line",
        "baseline_scope": "pre_topology_baseline",
        "post_topology_consumption_required": True,
        "topology_contract_ref": "v2.1.30",
        "package_level": package_level,
        "selection_artifact_mode": "explicit_selection_artifact",
        "free_text_alias_allowed": False,
        "package_level_alias_forbidden": True,
        "definition_resolution_included": False,
        "prerequisite_judgment_included": False,
        "prose_fallback_allowed": False,
    }


def build_resolve_payload(level: str, topology_mode: str) -> dict[str, Any]:
    package_level = _assert_package_level(level)
    resolved_topology = _assert_topology_mode(topology_mode)
    package_baseline = PACKAGE_BASELINES[package_level]
    return {
        "version": "v0.1",
        "runtime_plane_mode": "topology_aware_offering_package_definition_resolution",
        "line_class": "github_governance_topology_support_program",
        "package_level": package_level,
        "topology_mode": resolved_topology,
        "source_definition_artifact_ref": MOTHER_DRAFT_REF,
        "minimum_repo_set_by_topology": package_baseline["minimum_repo_set_by_topology"][resolved_topology],
        "workflow_inclusion_level_by_topology": package_baseline["workflow_inclusion_level"],
        "governance_asset_placement_rules": package_baseline["governance_asset_placement_rules"][resolved_topology],
        "back_write_allowed": False,
        "reinterpretation_allowed": False,
        "prose_fallback_allowed": False,
    }


def detect_topology_mode(workspace: str | Path) -> dict[str, Any]:
    root = Path(workspace)
    if not root.exists():
        raise FileNotFoundError(f"workspace does not exist: {root}")

    child_dirs = [item for item in root.iterdir() if item.is_dir()]
    dedicated_repo_present = any(item.name == ".github" for item in child_dirs)
    repo_local_github_paths = sorted(
        str(item.relative_to(root) / ".github")
        for item in child_dirs
        if item.name != ".github" and (item / ".github").exists()
    )

    if dedicated_repo_present and repo_local_github_paths:
        detected = "hybrid"
    elif dedicated_repo_present:
        detected = "dedicated_repo"
    elif repo_local_github_paths:
        detected = "repo_local"
    else:
        detected = "unknown"

    return {
        "workspace_root": str(root),
        "dedicated_repo_present": dedicated_repo_present,
        "repo_local_github_paths": repo_local_github_paths,
        "detected_topology_mode": detected,
    }


def build_status_payload(level: str, topology_mode: str, workspace: str | Path) -> dict[str, Any]:
    package_level = _assert_package_level(level)
    expected_topology = _assert_topology_mode(topology_mode)
    detected = detect_topology_mode(workspace)
    detected_mode = detected["detected_topology_mode"]

    if detected_mode == "unknown":
        resolved_mode = "not_evaluable"
        compliance_status = "compliant_with_gap"
    elif detected_mode == expected_topology:
        resolved_mode = detected_mode
        compliance_status = "compliant"
    else:
        resolved_mode = "degraded"
        compliance_status = "compliant_with_gap"

    pre_topology_status_payload = {
        "version": "v0.1",
        "runtime_plane_mode": "offering_package_status_evidence",
        "line_class": "offering_package_runtime_enablement_line",
        "baseline_scope": "pre_topology_baseline",
        "post_topology_consumption_required": True,
        "topology_status_precedence_ref": "v2.1.35",
        "package_level": package_level,
        "package_stage": "resolved",
        "package_compliance_status": "compliant_with_gap",
        "package_runtime_activity": "inactive",
        "evidence_refs": [],
        "runtime_activity_requires_minimum_evidence_refs": True,
        "prerequisite_verdict_used_as_activation": False,
        "narrative_only_status_allowed": False,
        "prose_fallback_allowed": False,
    }

    topology_payload = {
        "version": "v0.1",
        "runtime_plane_mode": "topology_aware_package_status_and_repo_checks",
        "line_class": "github_governance_topology_support_program",
        "topology_mode_expected": expected_topology,
        "topology_mode_detected": detected_mode,
        "topology_mode_resolved": resolved_mode,
        "topology_compliance_status": compliance_status,
        "missing_governance_assets": [],
        "misplaced_governance_assets": [],
        "narrative_only_compliance_allowed": False,
        "prose_fallback_allowed": False,
    }

    return {
        "pre_topology_status_payload": pre_topology_status_payload,
        "topology_status_payload": topology_payload,
        "workspace_detection": detected,
    }


def select(level: str) -> dict[str, Any]:
    payload = build_selection_payload(level)
    result = offering_package_selection_runtime_baseline.validate_bundle(payload)
    return {
        "command": "package_select",
        "package_selection": payload,
        "validation": result,
    }


def resolve(level: str, topology_mode: str) -> dict[str, Any]:
    selection_payload = build_selection_payload(level)
    selection_result = offering_package_selection_runtime_baseline.validate_bundle(selection_payload)
    resolved_payload = build_resolve_payload(level, topology_mode)
    resolved_result = topology_aware_offering_package_definition_resolution.validate_bundle(resolved_payload)
    return {
        "command": "package_resolve",
        "package_selection": selection_payload,
        "selection_validation": selection_result,
        "resolved_definition": resolved_payload,
        "validation": resolved_result,
    }


def status(level: str, topology_mode: str, workspace: str | Path) -> dict[str, Any]:
    selection_payload = build_selection_payload(level)
    selection_result = offering_package_selection_runtime_baseline.validate_bundle(selection_payload)
    resolved_payload = build_resolve_payload(level, topology_mode)
    resolved_result = topology_aware_offering_package_definition_resolution.validate_bundle(resolved_payload)
    status_payloads = build_status_payload(level, topology_mode, workspace)
    package_status_result = offering_package_status_and_evidence_runtime.validate_bundle(
        status_payloads["pre_topology_status_payload"]
    )
    topology_status_result = topology_aware_package_status_and_repo_checks.validate_bundle(
        status_payloads["topology_status_payload"]
    )
    return {
        "command": "package_status",
        "package_selection": selection_payload,
        "selection_validation": selection_result,
        "resolved_definition": resolved_payload,
        "resolution_validation": resolved_result,
        "package_status": {
            **status_payloads["pre_topology_status_payload"],
            **package_status_result.get("derived_results", {}),
        },
        "package_evidence_refs": status_payloads["pre_topology_status_payload"]["evidence_refs"],
        "topology_status": {
            **status_payloads["topology_status_payload"],
            **topology_status_result.get("derived_results", {}),
        },
        "workspace_detection": status_payloads["workspace_detection"],
        "validation": {
            "package_status": package_status_result,
            "topology_status": topology_status_result,
        },
    }


def render_payload(payload: dict[str, Any], output_format: str) -> str:
    if output_format in {"json", "llm"}:
        return json.dumps(payload, indent=2, ensure_ascii=True)

    command = payload.get("command", "package")
    lines = [f"command={command}"]
    if "package_selection" in payload:
        lines.append(f"package_level={payload['package_selection']['package_level']}")
    if command == "package_resolve":
        lines.append(f"topology_mode={payload['resolved_definition']['topology_mode']}")
        lines.append(
            "minimum_repo_set="
            + ",".join(payload["resolved_definition"]["minimum_repo_set_by_topology"])
        )
    if command == "package_status":
        lines.append(f"topology_expected={payload['topology_status']['topology_mode_expected']}")
        lines.append(f"topology_detected={payload['topology_status']['topology_mode_detected']}")
        lines.append(f"topology_resolved={payload['topology_status']['topology_mode_resolved']}")
        lines.append(f"structure_acceptance_status={payload['topology_status']['structure_acceptance_status']}")
        lines.append(f"topology_completion_status={payload['topology_status']['topology_completion_status']}")
    return "\n".join(lines)
