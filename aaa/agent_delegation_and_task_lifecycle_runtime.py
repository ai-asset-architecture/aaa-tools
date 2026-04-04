import json
from pathlib import Path
from typing import Any


ALLOWED_TASK_STATE = {
    "queued",
    "running",
    "completed",
    "failed",
    "blocked",
}
ALLOWED_OWNERSHIP_SCOPE = {
    "bounded_write_scope",
    "read_only_scope",
}
ALLOWED_HANDOFF_EVIDENCE_CLASS = {
    "task_result",
    "verification_record",
}
ALLOWED_VERIFICATION_CLOSURE_STATE = {
    "not_required",
    "pending_verification",
    "verified",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    task_state = str(bundle.get("task_state", "")).strip()
    ownership_scope = str(bundle.get("ownership_scope", "")).strip()
    handoff_evidence_class = str(bundle.get("handoff_evidence_class", "")).strip()
    verification_required = bundle.get("verification_required")
    verification_closure_state = str(bundle.get("verification_closure_state", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "delegation_lifecycle":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be delegation_lifecycle"})
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append({"code": "line_class", "message": "line_class must be mandatory_core_absorption_line"})
    if not str(bundle.get("task_id", "")).strip():
        errors.append({"code": "task_id", "message": "task_id is required"})
    if task_state not in ALLOWED_TASK_STATE:
        errors.append({"code": "task_state", "message": "task_state is not allowed"})
    if ownership_scope not in ALLOWED_OWNERSHIP_SCOPE:
        errors.append({"code": "ownership_scope", "message": "ownership_scope is not allowed"})
    if handoff_evidence_class not in ALLOWED_HANDOFF_EVIDENCE_CLASS:
        errors.append({"code": "handoff_evidence_class", "message": "handoff_evidence_class is not allowed"})
    if verification_closure_state not in ALLOWED_VERIFICATION_CLOSURE_STATE:
        errors.append({"code": "verification_closure_state", "message": "verification_closure_state is not allowed"})
    if bundle.get("handoff_completion_before_verification_allowed") is not False:
        errors.append(
            {
                "code": "handoff_completion_before_verification_allowed",
                "message": "handoff completion may not precede verification closure",
            }
        )
    if bundle.get("extension_loading_allowed") is not False:
        errors.append(
            {
                "code": "extension_loading_allowed",
                "message": "extension loading is outside delegation lifecycle scope",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append(
            {
                "code": "prose_fallback_allowed",
                "message": "prose_fallback_allowed must be false",
            }
        )

    if verification_required is True and verification_closure_state != "verified":
        errors.append(
            {
                "code": "verification_closure_state",
                "message": "verification-required task may not complete handoff before verification closure",
            }
        )
    if verification_required is False and verification_closure_state not in {"not_required", "verified"}:
        errors.append(
            {
                "code": "verification_closure_state",
                "message": "verification_closure_state conflicts with verification_required=false",
            }
        )
    if verification_required is True and handoff_evidence_class != "verification_record":
        errors.append(
            {
                "code": "handoff_evidence_class",
                "message": "verification-required task must hand off a verification_record",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "delegation_lifecycle",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "task_id": str(bundle.get("task_id", "")).strip(),
            "task_state": task_state,
            "ownership_scope": ownership_scope,
            "handoff_evidence_class": handoff_evidence_class,
            "verification_required": bool(verification_required),
            "verification_closure_state": verification_closure_state,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
