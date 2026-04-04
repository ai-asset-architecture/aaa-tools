import json
from typing import Any

from .package_commands import PACKAGE_LEVELS, TOPOLOGY_LEVELS


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


def supported_path(level: str, topology_mode: str) -> dict[str, Any]:
    package_level = _assert_package_level(level)
    resolved_topology = _assert_topology_mode(topology_mode)
    return {
        "command": "bootstrap_supported_path",
        "runtime_plane_mode": "supported_bootstrap_gate_chain",
        "line_class": "outside_in_follow_up_line",
        "package_level": package_level,
        "topology_mode": resolved_topology,
        "canonical_supported_path_count": 1,
        "path_semantics": "publicly_documented_sequence",
        "environment_profile_counted_as_supported_path": False,
        "local_sandbox_is_supported_path_alias": False,
        "canonical_bootstrap_steps": [
            {
                "sequence_index": 1,
                "step_id": "package_select",
                "classification": "canonical_supported",
                "command_template": f"aaa package select --level {package_level} --format json",
            },
            {
                "sequence_index": 2,
                "step_id": "package_resolve",
                "classification": "canonical_supported",
                "command_template": (
                    f"aaa package resolve --level {package_level} --topology-mode {resolved_topology} --format json"
                ),
            },
            {
                "sequence_index": 3,
                "step_id": "init_validate_plan",
                "classification": "canonical_supported",
                "command_template": "aaa init validate-plan --plan <plan_path> --schema specs/plan.schema.json --jsonl",
            },
            {
                "sequence_index": 4,
                "step_id": "prerequisite_gate",
                "classification": "canonical_supported",
                "command_template": (
                    "aaa governance topology-aware-prerequisite-gate --bundle <prerequisite_bundle_path> --format json"
                ),
            },
            {
                "sequence_index": 5,
                "step_id": "topology_status_check",
                "classification": "canonical_supported",
                "command_template": (
                    f"aaa package status --level {package_level} --topology-mode {resolved_topology} "
                    "--workspace <workspace_root> --format json"
                ),
            },
        ],
        "alternate_sequences": [
            {
                "sequence_id": "diagnostic_raw_governance_chain",
                "classification": "diagnostic_or_internal_only",
            },
            {
                "sequence_id": "local_sandbox_profile_overlay",
                "classification": "environment_profile_overlay_only",
            },
        ],
        "public_docs_must_expose_only_this_chain": True,
        "prose_fallback_allowed": False,
    }


def render_payload(payload: dict[str, Any], output_format: str) -> str:
    if output_format in {"json", "llm"}:
        return json.dumps(payload, indent=2, ensure_ascii=True)

    lines = [
        f"command={payload['command']}",
        f"package_level={payload['package_level']}",
        f"topology_mode={payload['topology_mode']}",
        f"canonical_supported_path_count={payload['canonical_supported_path_count']}",
    ]
    for step in payload["canonical_bootstrap_steps"]:
        lines.append(f"{step['sequence_index']}.{step['step_id']} -> {step['command_template']}")
    lines.append("alternate_sequences=diagnostic_or_internal_only")
    return "\n".join(lines)
