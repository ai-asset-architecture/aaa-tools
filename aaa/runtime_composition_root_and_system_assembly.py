import json
from pathlib import Path
from typing import Any


REQUIRED_RUNTIME_PLANES = [
    "permission_gate",
    "event_stream",
    "session_persistence",
    "runtime_control",
    "result_normalization",
    "workflow_runtime",
    "delegation_lifecycle",
    "extension_plane",
]


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    bootstrap_order = [str(item).strip() for item in bundle.get("bootstrap_order", [])]
    consumed_runtime_planes = [str(item).strip() for item in bundle.get("consumed_runtime_planes", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "composition_root":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be composition_root"})
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append({"code": "line_class", "message": "line_class must be mandatory_core_absorption_line"})
    if bundle.get("closeout_role") != "core_line_closeout":
        errors.append({"code": "closeout_role", "message": "closeout_role must be core_line_closeout"})
    if bootstrap_order != REQUIRED_RUNTIME_PLANES:
        errors.append(
            {
                "code": "bootstrap_order",
                "message": "bootstrap_order must enumerate the fixed mandatory core runtime plane order",
            }
        )
    if consumed_runtime_planes != REQUIRED_RUNTIME_PLANES:
        errors.append(
            {
                "code": "consumed_runtime_planes",
                "message": "consumed_runtime_planes must explicitly enumerate all mandatory core runtime planes",
            }
        )
    if bundle.get("consumed_runtime_plane_set_mode") != "explicit_enumeration":
        errors.append(
            {
                "code": "consumed_runtime_plane_set_mode",
                "message": "consumed_runtime_plane_set_mode must be explicit_enumeration",
            }
        )
    if bundle.get("startup_boundary") != "core_line_only":
        errors.append({"code": "startup_boundary", "message": "startup_boundary must be core_line_only"})
    if bundle.get("assembly_outcome") != "assembled":
        errors.append({"code": "assembly_outcome", "message": "assembly_outcome must be assembled"})
    if bundle.get("consumed_plane_semantics_rejudgment_allowed") is not False:
        errors.append(
            {
                "code": "consumed_plane_semantics_rejudgment_allowed",
                "message": "composition root may not rejudge consumed plane semantics",
            }
        )
    if bundle.get("new_primary_law_allowed") is not False:
        errors.append(
            {
                "code": "new_primary_law_allowed",
                "message": "composition root may not create new primary law",
            }
        )
    if bundle.get("conditional_expansion_enabled") is not False:
        errors.append(
            {
                "code": "conditional_expansion_enabled",
                "message": "conditional expansion may not be enabled in mandatory core closeout",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "composition_root",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "bootstrap_order": bootstrap_order,
            "consumed_runtime_planes": consumed_runtime_planes,
            "consumed_plane_count": len(consumed_runtime_planes),
            "closeout_role": "core_line_closeout",
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
