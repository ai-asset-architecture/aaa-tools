import json
from pathlib import Path
from typing import Any


ALLOWED_MANIFEST_CLASS = {
    "skill_manifest",
    "plugin_manifest",
}
ALLOWED_LOAD_MODE = {
    "local_load",
    "registered_load",
}
ALLOWED_REGISTER_BOUNDARY = {
    "command_injection",
    "tool_injection",
}
ALLOWED_TRUST_BOUNDARY = {
    "trusted",
    "restricted",
}
ALLOWED_INJECTION_TARGET = {
    "command_registry_slot",
    "tool_registry_slot",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    manifest_class = str(bundle.get("manifest_class", "")).strip()
    load_mode = str(bundle.get("load_mode", "")).strip()
    register_boundary = str(bundle.get("register_boundary", "")).strip()
    trust_boundary = str(bundle.get("trust_boundary", "")).strip()
    injection_target = str(bundle.get("injection_target", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "extension_plane":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be extension_plane"})
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append({"code": "line_class", "message": "line_class must be mandatory_core_absorption_line"})
    if not str(bundle.get("extension_id", "")).strip():
        errors.append({"code": "extension_id", "message": "extension_id is required"})
    if manifest_class not in ALLOWED_MANIFEST_CLASS:
        errors.append({"code": "manifest_class", "message": "manifest_class is not allowed"})
    if load_mode not in ALLOWED_LOAD_MODE:
        errors.append({"code": "load_mode", "message": "load_mode is not allowed"})
    if register_boundary not in ALLOWED_REGISTER_BOUNDARY:
        errors.append({"code": "register_boundary", "message": "register_boundary is not allowed"})
    if trust_boundary not in ALLOWED_TRUST_BOUNDARY:
        errors.append({"code": "trust_boundary", "message": "trust_boundary is not allowed"})
    if injection_target not in ALLOWED_INJECTION_TARGET:
        errors.append({"code": "injection_target", "message": "injection_target must use governed target taxonomy"})
    if bundle.get("canonical_override_allowed") is not False:
        errors.append(
            {
                "code": "canonical_override_allowed",
                "message": "extension runtime may not override canonical law",
            }
        )
    if bundle.get("task_lifecycle_definition_allowed") is not False:
        errors.append(
            {
                "code": "task_lifecycle_definition_allowed",
                "message": "extension runtime may not define task lifecycle semantics",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append(
            {
                "code": "prose_fallback_allowed",
                "message": "prose_fallback_allowed must be false",
            }
        )

    if trust_boundary != "trusted":
        errors.append(
            {
                "code": "trust_boundary",
                "message": "extension runtime requires trusted boundary before injection",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "extension_plane",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "extension_id": str(bundle.get("extension_id", "")).strip(),
            "manifest_class": manifest_class,
            "load_mode": load_mode,
            "register_boundary": register_boundary,
            "trust_boundary": trust_boundary,
            "injection_target": injection_target,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
