import json
from pathlib import Path
from typing import Any


ALLOWED_PACKAGE_LEVEL = {"lite", "core", "full"}
ALLOWED_PREREQUISITES = {
    "basic_ci",
    "ci_discipline",
    "contract_first",
    "mock_first",
    "review_evidence_discipline",
    "asset_feedback_loop",
    "ai_governance",
    "minimum_repo_presence",
}
ALLOWED_VERDICTS = {"pass", "fail", "pass_with_gap"}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    package_level = str(bundle.get("package_level", "")).strip()
    gate_scope = str(bundle.get("gate_scope", "")).strip()
    checked_prerequisites = bundle.get("checked_prerequisites", [])
    prerequisite_verdict = str(bundle.get("prerequisite_verdict", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "offering_package_prerequisite_gate":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be offering_package_prerequisite_gate",
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
    if bundle.get("topology_prerequisite_precedence_ref") != "v2.1.33":
        errors.append(
            {
                "code": "topology_prerequisite_precedence_ref",
                "message": "topology_prerequisite_precedence_ref must be v2.1.33",
            }
        )
    if package_level not in ALLOWED_PACKAGE_LEVEL:
        errors.append({"code": "package_level", "message": "package_level is not allowed"})
    if gate_scope != "pre_adoption_only":
        errors.append({"code": "gate_scope", "message": "gate_scope must be pre_adoption_only"})
    if not isinstance(checked_prerequisites, list) or not checked_prerequisites:
        errors.append(
            {
                "code": "checked_prerequisites",
                "message": "checked_prerequisites must be a non-empty array",
            }
        )
    else:
        unsupported = [item for item in checked_prerequisites if str(item).strip() not in ALLOWED_PREREQUISITES]
        if unsupported:
            errors.append(
                {
                    "code": "checked_prerequisites",
                    "message": "checked_prerequisites includes unsupported prerequisite identifiers",
                }
            )
    if prerequisite_verdict not in ALLOWED_VERDICTS:
        errors.append(
            {
                "code": "prerequisite_verdict",
                "message": "prerequisite_verdict must be pass/fail/pass_with_gap",
            }
        )
    if bundle.get("activation_implied") is not False:
        errors.append({"code": "activation_implied", "message": "activation_implied must be false"})
    if bundle.get("readiness_implied") is not False:
        errors.append({"code": "readiness_implied", "message": "readiness_implied must be false"})
    if bundle.get("completion_implied") is not False:
        errors.append({"code": "completion_implied", "message": "completion_implied must be false"})
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "offering_package_prerequisite_gate",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "package_level": package_level,
            "gate_scope": gate_scope,
            "checked_prerequisites": checked_prerequisites,
            "prerequisite_verdict": prerequisite_verdict,
            "topology_prerequisite_precedence_ref": bundle.get("topology_prerequisite_precedence_ref"),
            "post_topology_consumption_required": bundle.get("post_topology_consumption_required"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
