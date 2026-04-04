import json
from pathlib import Path
from typing import Any


ALLOWED_COMMAND_IDS = {
    "readiness-inspect",
    "repo-check",
}
ALLOWED_TURN_LIFECYCLE = {
    "request_received",
    "snapshot_loaded",
    "dispatch_resolved",
    "execution_completed",
    "evidence_gate_applied",
    "readiness_evaluated",
}
ALLOWED_WRITEBACK_DESTINATIONS = {
    "runtime_artifact_only",
    "evidence_candidate_only",
    "promotion_gated_only",
    "forbidden_canonical_writeback",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    supported_command_ids = [str(item).strip() for item in bundle.get("supported_command_ids", [])]
    turn_lifecycle = [str(item).strip() for item in bundle.get("turn_lifecycle", [])]
    write_back_destination_classes = [
        str(item).strip() for item in bundle.get("write_back_destination_classes", [])
    ]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("orchestration_runtime_id") != "query_orchestration":
        errors.append(
            {
                "code": "orchestration_runtime_id",
                "message": "orchestration_runtime_id must be query_orchestration",
            }
        )
    if bundle.get("runtime_plane_mode") != "orchestration_loop":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be orchestration_loop"})
    if bundle.get("dispatch_runtime_ref") != "internal/development/contracts/ops/shared-command-dispatch-runtime-bundle.v0.1.schema.json":
        errors.append(
            {
                "code": "dispatch_runtime_ref",
                "message": "dispatch_runtime_ref must point to shared-command-dispatch-runtime-bundle.v0.1.schema.json",
            }
        )
    if bundle.get("result_gate_ref") != "internal/development/contracts/ops/result-artifact-eligibility-and-evidence-promotion-gate.v0.1.schema.json":
        errors.append(
            {
                "code": "result_gate_ref",
                "message": "result_gate_ref must point to result-artifact-eligibility-and-evidence-promotion-gate.v0.1.schema.json",
            }
        )
    if bundle.get("snapshot_runtime_ref") != "internal/development/contracts/ops/session-context-snapshot-runtime-bundle.v0.1.schema.json":
        errors.append(
            {
                "code": "snapshot_runtime_ref",
                "message": "snapshot_runtime_ref must point to session-context-snapshot-runtime-bundle.v0.1.schema.json",
            }
        )

    invalid_command_ids = [item for item in supported_command_ids if item not in ALLOWED_COMMAND_IDS]
    if invalid_command_ids or set(supported_command_ids) != ALLOWED_COMMAND_IDS:
        errors.append(
            {
                "code": "supported_command_ids",
                "message": "supported_command_ids must contain exactly readiness-inspect and repo-check",
            }
        )

    invalid_turn_lifecycle = [item for item in turn_lifecycle if item not in ALLOWED_TURN_LIFECYCLE]
    if invalid_turn_lifecycle or set(turn_lifecycle) != ALLOWED_TURN_LIFECYCLE:
        errors.append(
            {
                "code": "turn_lifecycle",
                "message": "turn_lifecycle must contain the fixed request/turn lifecycle set",
            }
        )

    invalid_writeback = [item for item in write_back_destination_classes if item not in ALLOWED_WRITEBACK_DESTINATIONS]
    if invalid_writeback or set(write_back_destination_classes) != ALLOWED_WRITEBACK_DESTINATIONS:
        errors.append(
            {
                "code": "write_back_destination_classes",
                "message": "write_back_destination_classes must contain the fixed 4-class write-back boundary set",
            }
        )

    if bundle.get("promotion_gate_bypass_allowed") is not False:
        errors.append(
            {
                "code": "promotion_gate_bypass_allowed",
                "message": "promotion_gate_bypass_allowed must be false",
            }
        )
    if bundle.get("snapshot_boundary_bypass_allowed") is not False:
        errors.append(
            {
                "code": "snapshot_boundary_bypass_allowed",
                "message": "snapshot_boundary_bypass_allowed must be false",
            }
        )
    if bundle.get("primary_law_creation_allowed") is not False:
        errors.append(
            {
                "code": "primary_law_creation_allowed",
                "message": "primary_law_creation_allowed must be false",
            }
        )
    if bundle.get("family_expansion_allowed") is not False:
        errors.append(
            {
                "code": "family_expansion_allowed",
                "message": "family_expansion_allowed must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_orchestration_runtime_id": "query_orchestration",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "supported_command_ids": supported_command_ids,
            "turn_lifecycle": turn_lifecycle,
            "write_back_destination_classes": write_back_destination_classes,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
