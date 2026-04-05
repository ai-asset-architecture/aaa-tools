import json
from pathlib import Path
from typing import Any

from .package_commands import PACKAGE_LEVELS, TOPOLOGY_LEVELS

PROFILE_NAMES = {"local_sandbox"}


def _artifact(
    artifact_id: str,
    artifact_role: str,
    artifact_origin: str,
    artifact_required_for_step: bool,
    artifact_not_auto_generated_in_v2_1_41: bool,
    artifact_consumed_by_next_step: bool,
    artifact_classification: str,
    truth_boundary_note: str,
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "artifact_role": artifact_role,
        "artifact_origin": artifact_origin,
        "artifact_required_for_step": artifact_required_for_step,
        "artifact_not_auto_generated_in_v2_1_41": artifact_not_auto_generated_in_v2_1_41,
        "artifact_consumed_by_next_step": artifact_consumed_by_next_step,
        "artifact_classification": artifact_classification,
        "truth_boundary_note": truth_boundary_note,
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


def _assert_profile_name(profile: str) -> str:
    profile_name = str(profile).strip()
    if profile_name not in PROFILE_NAMES:
        raise ValueError("profile must be local_sandbox")
    return profile_name


def supported_path(level: str, topology_mode: str) -> dict[str, Any]:
    package_level = _assert_package_level(level)
    resolved_topology = _assert_topology_mode(topology_mode)
    plan_artifact = _artifact(
        artifact_id="plan_json",
        artifact_role="canonical_path_input",
        artifact_origin="client_authored",
        artifact_required_for_step=True,
        artifact_not_auto_generated_in_v2_1_41=True,
        artifact_consumed_by_next_step=False,
        artifact_classification="canonical_public_artifact",
        truth_boundary_note="client-authored canonical path input; not emitted by AAA in v2.1.41",
    )
    prerequisite_bundle_artifact = _artifact(
        artifact_id="topology_aware_prerequisite_bundle",
        artifact_role="canonical_path_input",
        artifact_origin="client_authored",
        artifact_required_for_step=True,
        artifact_not_auto_generated_in_v2_1_41=True,
        artifact_consumed_by_next_step=False,
        artifact_classification="canonical_public_artifact",
        truth_boundary_note="client-authored prerequisite bundle remains required; supported path is not fully automated",
    )
    return {
        "command": "bootstrap_supported_path",
        "runtime_plane_mode": "supported_bootstrap_gate_chain",
        "line_class": "outside_in_follow_up_line",
        "package_level": package_level,
        "topology_mode": resolved_topology,
        "canonical_supported_path_count": 1,
        "path_semantics": "publicly_documented_sequence",
        "supported_path_fully_automated": False,
        "client_authored_artifacts_present": True,
        "runtime_generation_coverage_complete": False,
        "automation_boundary": "client_authored_inputs_still_required",
        "readiness_scope": "onboarding_support_surface",
        "full_execution_readiness_certified": False,
        "full_orchestration_provided": False,
        "truth_boundary": "support_truth_not_full_readiness",
        "environment_profile_counted_as_supported_path": False,
        "local_sandbox_is_supported_path_alias": False,
        "canonical_bootstrap_steps": [
            {
                "sequence_index": 1,
                "step_id": "package_select",
                "classification": "canonical_supported",
                "command_template": f"aaa package select --level {package_level} --format json",
                "input_artifacts": [],
                "output_artifacts": [
                    _artifact(
                        artifact_id="package_selection_payload",
                        artifact_role="selection_artifact",
                        artifact_origin="command_emitted",
                        artifact_required_for_step=False,
                        artifact_not_auto_generated_in_v2_1_41=False,
                        artifact_consumed_by_next_step=True,
                        artifact_classification="canonical_public_artifact",
                        truth_boundary_note="selection artifact is emitted by aaa package select",
                    )
                ],
                "artifact_examples": ["package_selection.package_level=core"],
                "canonical_public_artifacts": ["package_selection_payload"],
                "diagnostic_or_internal_only_artifacts": [],
            },
            {
                "sequence_index": 2,
                "step_id": "package_resolve",
                "classification": "canonical_supported",
                "command_template": (
                    f"aaa package resolve --level {package_level} --topology-mode {resolved_topology} --format json"
                ),
                "input_artifacts": [
                    _artifact(
                        artifact_id="package_selection_payload",
                        artifact_role="selection_context",
                        artifact_origin="command_emitted",
                        artifact_required_for_step=False,
                        artifact_not_auto_generated_in_v2_1_41=False,
                        artifact_consumed_by_next_step=False,
                        artifact_classification="canonical_public_artifact",
                        truth_boundary_note="selection context is re-derived by resolve and need not be manually carried",
                    )
                ],
                "output_artifacts": [
                    _artifact(
                        artifact_id="resolved_definition_payload",
                        artifact_role="resolved_definition",
                        artifact_origin="command_emitted",
                        artifact_required_for_step=False,
                        artifact_not_auto_generated_in_v2_1_41=False,
                        artifact_consumed_by_next_step=False,
                        artifact_classification="canonical_public_artifact",
                        truth_boundary_note="resolved definition is emitted, but does not auto-generate downstream bundles",
                    )
                ],
                "artifact_examples": ["resolved_definition.topology_mode=repo_local"],
                "canonical_public_artifacts": ["resolved_definition_payload"],
                "diagnostic_or_internal_only_artifacts": [],
            },
            {
                "sequence_index": 3,
                "step_id": "init_validate_plan",
                "classification": "canonical_supported",
                "command_template": "aaa init validate-plan --plan <plan_path> --schema specs/plan.schema.json --jsonl",
                "input_artifacts": [plan_artifact],
                "output_artifacts": [
                    _artifact(
                        artifact_id="validated_plan_boundary_signal",
                        artifact_role="plan_boundary_result",
                        artifact_origin="command_emitted",
                        artifact_required_for_step=False,
                        artifact_not_auto_generated_in_v2_1_41=False,
                        artifact_consumed_by_next_step=False,
                        artifact_classification="canonical_public_artifact",
                        truth_boundary_note="validates schema/boundary only; does not certify downstream bundle readiness",
                    )
                ],
                "artifact_examples": ["jsonl event result with truth_boundary=plan_boundary_only"],
                "canonical_public_artifacts": ["plan_json", "validated_plan_boundary_signal"],
                "diagnostic_or_internal_only_artifacts": [],
            },
            {
                "sequence_index": 4,
                "step_id": "prerequisite_gate",
                "classification": "canonical_supported",
                "command_template": (
                    "aaa governance topology-aware-prerequisite-gate --bundle <prerequisite_bundle_path> --format json"
                ),
                "input_artifacts": [prerequisite_bundle_artifact],
                "output_artifacts": [
                    _artifact(
                        artifact_id="prerequisite_gate_result",
                        artifact_role="gate_result",
                        artifact_origin="command_emitted",
                        artifact_required_for_step=False,
                        artifact_not_auto_generated_in_v2_1_41=False,
                        artifact_consumed_by_next_step=False,
                        artifact_classification="canonical_public_artifact",
                        truth_boundary_note="gate validates bundle truth; v2.1.41 does not auto-generate the bundle itself",
                    )
                ],
                "artifact_examples": ["derived_results.topology_compliance_verdict=pass"],
                "canonical_public_artifacts": ["topology_aware_prerequisite_bundle", "prerequisite_gate_result"],
                "diagnostic_or_internal_only_artifacts": [],
            },
            {
                "sequence_index": 5,
                "step_id": "topology_status_check",
                "classification": "canonical_supported",
                "command_template": (
                    f"aaa package status --level {package_level} --topology-mode {resolved_topology} "
                    "--workspace <workspace_root> --format json"
                ),
                "input_artifacts": [
                    _artifact(
                        artifact_id="workspace_topology_inventory",
                        artifact_role="workspace_input",
                        artifact_origin="external_preexisting",
                        artifact_required_for_step=True,
                        artifact_not_auto_generated_in_v2_1_41=True,
                        artifact_consumed_by_next_step=False,
                        artifact_classification="canonical_public_artifact",
                        truth_boundary_note="status inspects an existing workspace; it does not materialize one",
                    )
                ],
                "output_artifacts": [
                    _artifact(
                        artifact_id="package_status_payload",
                        artifact_role="support_status_result",
                        artifact_origin="command_emitted",
                        artifact_required_for_step=False,
                        artifact_not_auto_generated_in_v2_1_41=False,
                        artifact_consumed_by_next_step=False,
                        artifact_classification="canonical_public_artifact",
                        truth_boundary_note="support truth output only; not a full readiness certification",
                    )
                ],
                "artifact_examples": ["topology_status.topology_compliance_status=compliant_with_gap"],
                "canonical_public_artifacts": ["workspace_topology_inventory", "package_status_payload"],
                "diagnostic_or_internal_only_artifacts": [],
            },
        ],
        "alternate_sequences": [
            {
                "sequence_id": "diagnostic_raw_governance_chain",
                "classification": "diagnostic_or_internal_only",
                "diagnostic_or_internal_only_artifacts": [
                    _artifact(
                        artifact_id="diagnostic_raw_bundle_chain",
                        artifact_role="debug_carrier",
                        artifact_origin="client_authored",
                        artifact_required_for_step=False,
                        artifact_not_auto_generated_in_v2_1_41=True,
                        artifact_consumed_by_next_step=False,
                        artifact_classification="diagnostic_or_internal_only_artifact",
                        truth_boundary_note="diagnostic carrier only; not part of the canonical public handoff set",
                    )
                ],
            },
            {
                "sequence_id": "local_sandbox_profile_overlay",
                "classification": "environment_profile_overlay_only",
                "diagnostic_or_internal_only_artifacts": [
                    _artifact(
                        artifact_id="local_sandbox_candidate_evidence_bundle",
                        artifact_role="profile_overlay_output",
                        artifact_origin="command_emitted",
                        artifact_required_for_step=False,
                        artifact_not_auto_generated_in_v2_1_41=False,
                        artifact_consumed_by_next_step=False,
                        artifact_classification="diagnostic_or_internal_only_artifact",
                        truth_boundary_note="supported execution profile overlay; not a second canonical public path",
                    )
                ],
            },
        ],
        "public_docs_must_expose_only_this_chain": True,
        "prose_fallback_allowed": False,
    }


def profile(profile: str, level: str, topology_mode: str, workspace: Path) -> dict[str, Any]:
    profile_name = _assert_profile_name(profile)
    package_level = _assert_package_level(level)
    resolved_topology = _assert_topology_mode(topology_mode)
    workspace_root = Path(workspace).resolve()
    return {
        "command": "bootstrap_profile",
        "runtime_plane_mode": "local_sandbox_bootstrap_profile",
        "line_class": "outside_in_follow_up_line",
        "profile_name": profile_name,
        "profile_class": "supported_bootstrap_environment",
        "package_level": package_level,
        "topology_mode": resolved_topology,
        "workspace_root": str(workspace_root),
        "dry_run_alias": False,
        "requires_github_side_effects": False,
        "requires_org_repo_creation": False,
        "produces_bootstrap_report": True,
        "produces_candidate_evidence_bundle": True,
        "supported_path_count_changed": False,
        "profile_is_public_supported_path": False,
        "prose_fallback_allowed": False,
    }


def render_payload(payload: dict[str, Any], output_format: str) -> str:
    if output_format in {"json", "llm"}:
        return json.dumps(payload, indent=2, ensure_ascii=True)

    if payload.get("command") == "bootstrap_profile":
        lines = [
            f"command={payload['command']}",
            f"profile_name={payload['profile_name']}",
            f"package_level={payload['package_level']}",
            f"topology_mode={payload['topology_mode']}",
            f"workspace_root={payload['workspace_root']}",
            f"dry_run_alias={str(payload['dry_run_alias']).lower()}",
            f"supported_path_count_changed={str(payload['supported_path_count_changed']).lower()}",
        ]
        return "\n".join(lines)

    lines = [
        f"command={payload['command']}",
        f"package_level={payload['package_level']}",
        f"topology_mode={payload['topology_mode']}",
        f"canonical_supported_path_count={payload['canonical_supported_path_count']}",
        f"supported_path_fully_automated={str(payload['supported_path_fully_automated']).lower()}",
    ]
    for step in payload["canonical_bootstrap_steps"]:
        lines.append(f"{step['sequence_index']}.{step['step_id']} -> {step['command_template']}")
    lines.append("alternate_sequences=diagnostic_or_internal_only")
    return "\n".join(lines)
