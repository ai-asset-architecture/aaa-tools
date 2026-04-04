import json
from pathlib import Path
from typing import Any


ALLOWED_OUTPUT_CLASSES = {
    "machine_safe",
    "human_safe",
    "operator_safe",
}
ALLOWED_STATUS = {
    "ok",
    "error",
    "warning",
}
ALLOWED_ARTIFACT_REF_ROLES = {
    "supporting_artifact",
    "evidence_candidate",
    "path_specific_artifact",
}
ALLOWED_NORMALIZED_PAYLOAD_CLASSES = {
    "structured_result",
    "structured_error",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    output_class = str(bundle.get("output_class", "")).strip()
    status = str(bundle.get("status", "")).strip()
    artifact_refs_role = str(bundle.get("artifact_refs_role", "")).strip()
    normalized_payload_class = str(bundle.get("normalized_payload_class", "")).strip()
    normalized_payload_precedence = str(bundle.get("normalized_payload_precedence", "")).strip()
    artifact_refs = [str(item).strip() for item in bundle.get("artifact_refs", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "result_normalization":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be result_normalization",
            }
        )
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be mandatory_core_absorption_line",
            }
        )
    if output_class not in ALLOWED_OUTPUT_CLASSES:
        errors.append({"code": "output_class", "message": "output_class is not allowed"})
    if status not in ALLOWED_STATUS:
        errors.append({"code": "status", "message": "status is not allowed"})
    if not isinstance(bundle.get("errors"), list):
        errors.append({"code": "errors", "message": "errors must be an array"})
    if not isinstance(bundle.get("warnings"), list):
        errors.append({"code": "warnings", "message": "warnings must be an array"})
    if not artifact_refs:
        errors.append({"code": "artifact_refs", "message": "artifact_refs must contain at least one reference"})
    if artifact_refs_role not in ALLOWED_ARTIFACT_REF_ROLES:
        errors.append({"code": "artifact_refs_role", "message": "artifact_refs_role is not allowed"})
    if normalized_payload_class not in ALLOWED_NORMALIZED_PAYLOAD_CLASSES:
        errors.append(
            {
                "code": "normalized_payload_class",
                "message": "normalized_payload_class is not allowed",
            }
        )
    if normalized_payload_precedence != "normalized_payload_primary":
        errors.append(
            {
                "code": "normalized_payload_precedence",
                "message": "normalized_payload_precedence must be normalized_payload_primary",
            }
        )
    if bundle.get("prose_only_result_allowed") is not False:
        errors.append(
            {
                "code": "prose_only_result_allowed",
                "message": "prose_only_result_allowed must be false",
            }
        )
    if artifact_refs_role == "path_specific_artifact":
        errors.append(
            {
                "code": "artifact_refs_role",
                "message": "path_specific_artifact may not be used as the shared normalized result source",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "result_normalization",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "output_class": output_class,
            "status": status,
            "artifact_refs": artifact_refs,
            "artifact_refs_role": artifact_refs_role,
            "normalized_payload_class": normalized_payload_class,
            "normalized_payload_precedence": normalized_payload_precedence,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
