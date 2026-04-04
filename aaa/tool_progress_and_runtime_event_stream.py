import json
from pathlib import Path
from typing import Any


ALLOWED_SIGNAL_CLASS = {
    "progress_signal",
    "result_signal",
    "evidence_signal",
}
ALLOWED_EVENT_PHASE = {
    "started",
    "running",
    "waiting",
    "completed",
    "failed",
}
ALLOWED_EVIDENCE_SOURCE_ROLE = {
    "not_evidence_source",
    "evidence_generation_source",
    "evidence_reference_source",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    signal_class = str(bundle.get("signal_class", "")).strip()
    event_phase = str(bundle.get("event_phase", "")).strip()
    evidence_source_role = str(bundle.get("evidence_source_role", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "event_stream":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be event_stream"})
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be mandatory_core_absorption_line",
            }
        )
    if bundle.get("event_stream_id") != "shared_runtime_event_stream":
        errors.append(
            {
                "code": "event_stream_id",
                "message": "event_stream_id must be shared_runtime_event_stream",
            }
        )
    if signal_class not in ALLOWED_SIGNAL_CLASS:
        errors.append({"code": "signal_class", "message": "signal_class is not allowed"})
    if event_phase not in ALLOWED_EVENT_PHASE:
        errors.append({"code": "event_phase", "message": "event_phase is not allowed"})
    if evidence_source_role not in ALLOWED_EVIDENCE_SOURCE_ROLE:
        errors.append(
            {
                "code": "evidence_source_role",
                "message": "evidence_source_role is not allowed",
            }
        )
    if bundle.get("formal_evidence_artifact") is not False:
        errors.append(
            {
                "code": "formal_evidence_artifact",
                "message": "event stream record may not directly equal a formal evidence artifact",
            }
        )
    if bundle.get("canonical_truth_promotion_allowed") is not False:
        errors.append(
            {
                "code": "canonical_truth_promotion_allowed",
                "message": "event stream may not promote to canonical truth",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append(
            {
                "code": "prose_fallback_allowed",
                "message": "prose_fallback_allowed must be false",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "event_stream",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "signal_class": signal_class,
            "event_phase": event_phase,
            "evidence_source_role": evidence_source_role,
            "result_promotion_allowed": bool(bundle.get("result_promotion_allowed")),
            "evidence_promotion_allowed": bool(bundle.get("evidence_promotion_allowed")),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
