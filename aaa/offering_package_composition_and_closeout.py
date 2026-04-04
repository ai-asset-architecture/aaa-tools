import json
from pathlib import Path
from typing import Any


REQUIRED_STAGES = [
    "package_selection",
    "definition_resolution",
    "prerequisite_gate",
    "materialization_mapping",
    "status_evidence_runtime",
    "machine_read_boundary",
]


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    consumed_package_runtime_stages = [
        str(item).strip() for item in bundle.get("consumed_package_runtime_stages", [])
    ]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "offering_package_composition_closeout":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be offering_package_composition_closeout",
            }
        )
    if bundle.get("line_class") != "offering_package_runtime_enablement_line":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be offering_package_runtime_enablement_line",
            }
        )
    if bundle.get("baseline_scope") != "pre_topology_closeout_baseline":
        errors.append(
            {
                "code": "baseline_scope",
                "message": "baseline_scope must be pre_topology_closeout_baseline",
            }
        )
    if bundle.get("post_topology_consumption_required") is not True:
        errors.append(
            {
                "code": "post_topology_consumption_required",
                "message": "post_topology_consumption_required must be true",
            }
        )
    if bundle.get("topology_closeout_precedence_ref") != "v2.1.36":
        errors.append(
            {
                "code": "topology_closeout_precedence_ref",
                "message": "topology_closeout_precedence_ref must be v2.1.36",
            }
        )
    if bundle.get("closeout_role") != "package_runtime_core_closeout":
        errors.append(
            {
                "code": "closeout_role",
                "message": "closeout_role must be package_runtime_core_closeout",
            }
        )
    if consumed_package_runtime_stages != REQUIRED_STAGES:
        errors.append(
            {
                "code": "consumed_package_runtime_stages",
                "message": "consumed_package_runtime_stages must explicitly enumerate the full package runtime core stage set",
            }
        )
    if bundle.get("consumed_stage_set_mode") != "explicit_enumeration":
        errors.append(
            {
                "code": "consumed_stage_set_mode",
                "message": "consumed_stage_set_mode must be explicit_enumeration",
            }
        )
    consumed_stage_set_hash = str(bundle.get("consumed_stage_set_hash", "")).strip()
    if not consumed_stage_set_hash.startswith("sha256:"):
        errors.append(
            {
                "code": "consumed_stage_set_hash",
                "message": "consumed_stage_set_hash must be a sha256-prefixed fingerprint",
            }
        )
    if bundle.get("closeout_scope") != "package_runtime_core_only":
        errors.append(
            {
                "code": "closeout_scope",
                "message": "closeout_scope must be package_runtime_core_only",
            }
        )
    if bundle.get("offering_semantics_rejudgment_allowed") is not False:
        errors.append(
            {
                "code": "offering_semantics_rejudgment_allowed",
                "message": "closeout may not rejudge offering semantics",
            }
        )
    if bundle.get("conditional_expansion_triggered") is not False:
        errors.append(
            {
                "code": "conditional_expansion_triggered",
                "message": "closeout may not trigger conditional expansion",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "offering_package_composition_closeout",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "consumed_package_runtime_stages": consumed_package_runtime_stages,
            "consumed_stage_count": len(consumed_package_runtime_stages),
            "closeout_role": "package_runtime_core_closeout",
            "topology_closeout_precedence_ref": bundle.get("topology_closeout_precedence_ref"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
