import json
from pathlib import Path
from typing import Any


ALLOWED_TOPOLOGY_MODE = {
    "dedicated_repo",
    "repo_local",
    "hybrid",
}
ALLOWED_REQUIRED_STRUCTURE = {
    "dedicated_dot_github_repo",
    "repo_local_dot_github",
    "hybrid_dual_presence",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    topology_mode = str(bundle.get("topology_mode", "")).strip()
    required_structure = bundle.get("required_structure_by_topology", [])
    validation_scope = str(bundle.get("validation_scope", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "topology_aware_init_plan_validation":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be topology_aware_init_plan_validation",
            }
        )
    if bundle.get("line_class") != "github_governance_topology_support_program":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be github_governance_topology_support_program",
            }
        )
    if topology_mode not in ALLOWED_TOPOLOGY_MODE:
        errors.append({"code": "topology_mode", "message": "topology_mode is not allowed"})
    if validation_scope != "declared_planned_structure_compatibility":
        errors.append(
            {
                "code": "validation_scope",
                "message": "validation_scope must stay at declared/planned structure compatibility",
            }
        )
    if not isinstance(required_structure, list) or not required_structure:
        errors.append(
            {
                "code": "required_structure_by_topology",
                "message": "required_structure_by_topology must be a non-empty array",
            }
        )
    else:
        for item in required_structure:
            if str(item).strip() not in ALLOWED_REQUIRED_STRUCTURE:
                errors.append(
                    {
                        "code": "required_structure_by_topology",
                        "message": "required_structure_by_topology includes an unsupported structure marker",
                    }
                )
                break
    if topology_mode == "repo_local" and bundle.get("github_repo_existence_required") is not False:
        errors.append(
            {
                "code": "github_repo_existence_required",
                "message": "repo_local may not require dedicated .github repo existence",
            }
        )
    if topology_mode == "hybrid" and bundle.get("dual_side_evidence_required") is not True:
        errors.append(
            {
                "code": "dual_side_evidence_required",
                "message": "hybrid must require dual-side evidence",
            }
        )
    if bundle.get("runtime_detected_topology_verdict_emitted") is not False:
        errors.append(
            {
                "code": "runtime_detected_topology_verdict_emitted",
                "message": "init validation may not emit runtime detected topology verdicts",
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
        "resolved_runtime_plane_mode": "topology_aware_init_plan_validation",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "topology_mode": topology_mode,
            "validation_scope": validation_scope,
            "required_structure_by_topology": required_structure,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
