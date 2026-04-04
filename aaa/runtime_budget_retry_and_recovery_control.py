import json
from pathlib import Path
from typing import Any


ALLOWED_BUDGET_SCOPE = {
    "per_turn",
    "per_session",
    "per_workflow",
}
ALLOWED_FAILURE_CLASS = {
    "retryable",
    "terminal",
}
ALLOWED_RETRY_MODE = {
    "limited_retry",
    "no_retry",
}
ALLOWED_FALLBACK_MODE = {
    "same_path_recovery",
    "fallback_path",
    "none",
}
ALLOWED_STOP_CONDITION = {
    "budget_exhausted",
    "terminal_failure",
    "retry_limit_reached",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    budget_scope = str(bundle.get("budget_scope", "")).strip()
    failure_class = str(bundle.get("failure_class", "")).strip()
    retry_mode = str(bundle.get("retry_mode", "")).strip()
    fallback_mode = str(bundle.get("fallback_mode", "")).strip()
    stop_condition = str(bundle.get("stop_condition", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "runtime_control":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be runtime_control"})
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append({"code": "line_class", "message": "line_class must be mandatory_core_absorption_line"})
    if budget_scope not in ALLOWED_BUDGET_SCOPE:
        errors.append({"code": "budget_scope", "message": "budget_scope is not allowed"})
    if failure_class not in ALLOWED_FAILURE_CLASS:
        errors.append({"code": "failure_class", "message": "failure_class is not allowed"})
    if retry_mode not in ALLOWED_RETRY_MODE:
        errors.append({"code": "retry_mode", "message": "retry_mode is not allowed"})
    if fallback_mode not in ALLOWED_FALLBACK_MODE:
        errors.append({"code": "fallback_mode", "message": "fallback_mode is not allowed"})
    if stop_condition not in ALLOWED_STOP_CONDITION:
        errors.append({"code": "stop_condition", "message": "stop_condition is not allowed"})
    if bundle.get("fallback_retry_recursion_allowed") is not False:
        errors.append(
            {
                "code": "fallback_retry_recursion_allowed",
                "message": "fallback path may not recurse into unbounded retry",
            }
        )
    if bundle.get("provider_business_layer_allowed") is not False:
        errors.append(
            {
                "code": "provider_business_layer_allowed",
                "message": "provider business layer expansion is not allowed",
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
        "resolved_runtime_plane_mode": "runtime_control",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "budget_scope": budget_scope,
            "failure_class": failure_class,
            "retry_mode": retry_mode,
            "fallback_mode": fallback_mode,
            "stop_condition": stop_condition,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
