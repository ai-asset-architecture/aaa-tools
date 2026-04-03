import json
from pathlib import Path
from typing import Any


ALLOWED_ORCHESTRATION_MODES = {
    "interactive_session",
    "headless_session",
    "operator_review_session",
}

ALLOWED_QUERY_STATE_STORES = {
    "session_memory",
    "transcript_store",
    "readiness_snapshot",
}

ALLOWED_READINESS_SURFACES = {
    "operator_summary",
    "gate_status_surface",
    "readiness_panel",
}

REQUIRED_READINESS_CHECKS = {
    "context_loaded",
    "authority_resolved",
    "preflight_passed",
    "evidence_path_bound",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    orchestration_mode = str(bundle.get("orchestration_mode", "")).strip()
    query_state_store = str(bundle.get("query_state_store", "")).strip()
    readiness_surface = str(bundle.get("readiness_surface", "")).strip()
    readiness_checks = [str(item).strip() for item in bundle.get("readiness_checks", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})

    if orchestration_mode not in ALLOWED_ORCHESTRATION_MODES:
        errors.append({"code": "orchestration_mode", "message": "invalid orchestration_mode"})

    if query_state_store not in ALLOWED_QUERY_STATE_STORES:
        errors.append({"code": "query_state_store", "message": "invalid query_state_store"})

    if readiness_surface not in ALLOWED_READINESS_SURFACES:
        errors.append({"code": "readiness_surface", "message": "invalid readiness_surface"})

    unknown_checks = [item for item in readiness_checks if item not in REQUIRED_READINESS_CHECKS]
    if unknown_checks:
        errors.append(
            {
                "code": "readiness_checks",
                "message": f"unknown readiness checks: {', '.join(sorted(unknown_checks))}",
            }
        )

    missing_checks = [item for item in REQUIRED_READINESS_CHECKS if item not in readiness_checks]
    if missing_checks:
        errors.append(
            {
                "code": "readiness_checks",
                "message": f"missing required readiness checks: {', '.join(sorted(missing_checks))}",
            }
        )

    if readiness_surface == "readiness_panel" and query_state_store != "readiness_snapshot":
        errors.append(
            {
                "code": "surface_store_binding",
                "message": "readiness_panel requires query_state_store=readiness_snapshot",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_orchestration_mode": orchestration_mode,
        "resolved_query_state_store": query_state_store,
        "resolved_readiness_surface": readiness_surface,
        "resolved_readiness_checks": readiness_checks,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    bundle = load_bundle(bundle_path)
    result = validate_bundle(bundle)
    result["bundle_path"] = str(Path(bundle_path))
    return result
