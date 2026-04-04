import json
from pathlib import Path
from typing import Any


ALLOWED_PACKAGE_LEVEL = {"lite", "core", "full"}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    package_level = str(bundle.get("package_level", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "offering_package_selection":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be offering_package_selection",
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
    if bundle.get("topology_contract_ref") != "v2.1.30":
        errors.append(
            {
                "code": "topology_contract_ref",
                "message": "topology_contract_ref must be v2.1.30",
            }
        )
    if package_level not in ALLOWED_PACKAGE_LEVEL:
        errors.append(
            {
                "code": "package_level",
                "message": "package_level must be one of lite/core/full",
            }
        )
    if bundle.get("selection_artifact_mode") != "explicit_selection_artifact":
        errors.append(
            {
                "code": "selection_artifact_mode",
                "message": "selection_artifact_mode must be explicit_selection_artifact",
            }
        )
    if bundle.get("free_text_alias_allowed") is not False:
        errors.append(
            {
                "code": "free_text_alias_allowed",
                "message": "free_text_alias_allowed must be false",
            }
        )
    if bundle.get("package_level_alias_forbidden") is not True:
        errors.append(
            {
                "code": "package_level_alias_forbidden",
                "message": "package_level_alias_forbidden must be true",
            }
        )
    if bundle.get("definition_resolution_included") is not False:
        errors.append(
            {
                "code": "definition_resolution_included",
                "message": "definition_resolution_included must be false",
            }
        )
    if bundle.get("prerequisite_judgment_included") is not False:
        errors.append(
            {
                "code": "prerequisite_judgment_included",
                "message": "prerequisite_judgment_included must be false",
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
        "resolved_runtime_plane_mode": "offering_package_selection",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "package_level": package_level,
            "selection_artifact_mode": bundle.get("selection_artifact_mode"),
            "post_topology_consumption_required": bundle.get("post_topology_consumption_required"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
