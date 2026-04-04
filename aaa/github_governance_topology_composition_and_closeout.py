import json
from pathlib import Path
from typing import Any


REQUIRED_STAGES = [
    "topology_contract_baseline",
    "topology_aware_init_validation",
    "topology_aware_definition_resolution",
    "topology_aware_prerequisite_gate",
    "topology_aware_materialization_mapping",
    "topology_aware_status_repo_checks",
]


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    consumed_topology_stages = [str(item).strip() for item in bundle.get("consumed_topology_stages", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "github_governance_topology_composition_and_closeout":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be github_governance_topology_composition_and_closeout",
            }
        )
    if bundle.get("line_class") != "github_governance_topology_support_program":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be github_governance_topology_support_program",
            }
        )
    if bundle.get("closeout_role") != "topology_support_closeout":
        errors.append({"code": "closeout_role", "message": "closeout_role must be topology_support_closeout"})
    if consumed_topology_stages != REQUIRED_STAGES:
        errors.append(
            {
                "code": "consumed_topology_stages",
                "message": "consumed_topology_stages must explicitly enumerate the full topology support stage set",
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
    if bundle.get("semantics_rejudgment_allowed") is not False:
        errors.append(
            {
                "code": "semantics_rejudgment_allowed",
                "message": "closeout may not rejudge consumed topology semantics",
            }
        )
    if bundle.get("primary_semantics_backfill_allowed") is not False:
        errors.append(
            {
                "code": "primary_semantics_backfill_allowed",
                "message": "closeout may not backfill undefined primary semantics",
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
        "resolved_runtime_plane_mode": "github_governance_topology_composition_and_closeout",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "consumed_topology_stages": consumed_topology_stages,
            "consumed_stage_count": len(consumed_topology_stages),
            "closeout_role": "topology_support_closeout",
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
