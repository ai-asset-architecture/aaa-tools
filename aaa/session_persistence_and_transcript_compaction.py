import json
from pathlib import Path
from typing import Any


ALLOWED_SESSION_STORE_MODE = {
    "persistent_store",
    "ephemeral_store",
}
ALLOWED_TRANSCRIPT_CLASS = {
    "raw_transcript",
    "compacted_transcript",
}
ALLOWED_COMPACTION_MODE = {
    "lossless_boundary",
    "summarized_boundary",
}
ALLOWED_REPLAY_INPUT_ELIGIBILITY = {
    "allowed",
    "disallowed",
    "allowed_with_boundary",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    session_store_mode = str(bundle.get("session_store_mode", "")).strip()
    transcript_class = str(bundle.get("transcript_class", "")).strip()
    compaction_mode = str(bundle.get("compaction_mode", "")).strip()
    replay_input_eligibility = str(bundle.get("replay_input_eligibility", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "session_persistence":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be session_persistence"})
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append({"code": "line_class", "message": "line_class must be mandatory_core_absorption_line"})
    if session_store_mode not in ALLOWED_SESSION_STORE_MODE:
        errors.append({"code": "session_store_mode", "message": "session_store_mode is not allowed"})
    if transcript_class not in ALLOWED_TRANSCRIPT_CLASS:
        errors.append({"code": "transcript_class", "message": "transcript_class is not allowed"})
    if compaction_mode not in ALLOWED_COMPACTION_MODE:
        errors.append({"code": "compaction_mode", "message": "compaction_mode is not allowed"})
    if replay_input_eligibility not in ALLOWED_REPLAY_INPUT_ELIGIBILITY:
        errors.append(
            {
                "code": "replay_input_eligibility",
                "message": "replay_input_eligibility must use the fixed machine-checkable enum",
            }
        )
    if bundle.get("canonical_truth_promotion_allowed") is not False:
        errors.append(
            {
                "code": "canonical_truth_promotion_allowed",
                "message": "transcript may not promote to canonical truth",
            }
        )
    if bundle.get("audit_reproducibility_required") is not True:
        errors.append(
            {
                "code": "audit_reproducibility_required",
                "message": "audit_reproducibility_required must be true",
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
        "resolved_runtime_plane_mode": "session_persistence",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "session_store_mode": session_store_mode,
            "transcript_class": transcript_class,
            "compaction_mode": compaction_mode,
            "replay_input_eligibility": replay_input_eligibility,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
