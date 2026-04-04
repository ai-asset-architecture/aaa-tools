import json
from pathlib import Path
from typing import Any


REQUIRED_PAYLOADS = {
    "package_selection",
    "resolved_definition",
    "prerequisite_verdict",
    "package_status",
    "package_evidence_refs",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    exposed_payloads = bundle.get("exposed_payloads", [])

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "package_machine_interface_read_boundary":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be package_machine_interface_read_boundary",
            }
        )
    if bundle.get("line_class") != "offering_package_runtime_enablement_line":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be offering_package_runtime_enablement_line",
            }
        )
    if bundle.get("baseline_scope") != "pre_topology_baseline":
        errors.append(
            {
                "code": "baseline_scope",
                "message": "baseline_scope must be pre_topology_baseline",
            }
        )
    if bundle.get("post_topology_consumption_required") is not True:
        errors.append(
            {
                "code": "post_topology_consumption_required",
                "message": "post_topology_consumption_required must be true",
            }
        )
    if bundle.get("topology_read_boundary_precedence_ref") != "v2.1.35":
        errors.append(
            {
                "code": "topology_read_boundary_precedence_ref",
                "message": "topology_read_boundary_precedence_ref must be v2.1.35",
            }
        )
    if bundle.get("interface_scope") != "machine_read_boundary_only":
        errors.append(
            {
                "code": "interface_scope",
                "message": "interface_scope must be machine_read_boundary_only",
            }
        )
    if not isinstance(exposed_payloads, list):
        errors.append({"code": "exposed_payloads", "message": "exposed_payloads must be an array"})
    else:
        payload_set = {str(item).strip() for item in exposed_payloads}
        if payload_set != REQUIRED_PAYLOADS:
            errors.append(
                {
                    "code": "exposed_payloads",
                    "message": "exposed_payloads must exactly match the canonical package read payload set",
                }
            )
    if bundle.get("cli_output_mapping_mode") != "isomorphic_human_json_mapping":
        errors.append(
            {
                "code": "cli_output_mapping_mode",
                "message": "cli_output_mapping_mode must be isomorphic_human_json_mapping",
            }
        )
    if bundle.get("read_only_boundary") is not True:
        errors.append({"code": "read_only_boundary", "message": "read_only_boundary must be true"})
    if bundle.get("ai_orchestration_claimed") is not False:
        errors.append(
            {
                "code": "ai_orchestration_claimed",
                "message": "ai_orchestration_claimed must be false",
            }
        )
    if bundle.get("remote_session_semantics_included") is not False:
        errors.append(
            {
                "code": "remote_session_semantics_included",
                "message": "remote_session_semantics_included must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "package_machine_interface_read_boundary",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "interface_scope": bundle.get("interface_scope"),
            "exposed_payloads": exposed_payloads,
            "cli_output_mapping_mode": bundle.get("cli_output_mapping_mode"),
            "read_only_boundary": bundle.get("read_only_boundary"),
            "topology_read_boundary_precedence_ref": bundle.get("topology_read_boundary_precedence_ref"),
            "post_topology_consumption_required": bundle.get("post_topology_consumption_required"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
