import json
from pathlib import Path
from typing import Any


ALLOWED_PACKAGE_LEVELS = {"lite", "core", "full"}
ALLOWED_PACKAGE_STAGES = {"selected", "resolved", "gated", "materialized"}
ALLOWED_COMPLIANCE = {"compliant", "non_compliant", "compliant_with_gap"}
ALLOWED_RUNTIME_ACTIVITY = {"active", "inactive"}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    package_level = str(bundle.get("package_level", "")).strip()
    package_stage = str(bundle.get("package_stage", "")).strip()
    package_compliance_status = str(bundle.get("package_compliance_status", "")).strip()
    package_runtime_activity = str(bundle.get("package_runtime_activity", "")).strip()
    evidence_refs = bundle.get("evidence_refs", [])

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "offering_package_status_evidence":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be offering_package_status_evidence",
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
    if bundle.get("topology_status_precedence_ref") != "v2.1.35":
        errors.append(
            {
                "code": "topology_status_precedence_ref",
                "message": "topology_status_precedence_ref must be v2.1.35",
            }
        )
    if package_level not in ALLOWED_PACKAGE_LEVELS:
        errors.append({"code": "package_level", "message": "package_level is not allowed"})
    if package_stage not in ALLOWED_PACKAGE_STAGES:
        errors.append({"code": "package_stage", "message": "package_stage is not allowed"})
    if package_compliance_status not in ALLOWED_COMPLIANCE:
        errors.append(
            {
                "code": "package_compliance_status",
                "message": "package_compliance_status is not allowed",
            }
        )
    if package_runtime_activity not in ALLOWED_RUNTIME_ACTIVITY:
        errors.append(
            {
                "code": "package_runtime_activity",
                "message": "package_runtime_activity is not allowed",
            }
        )
    if not isinstance(evidence_refs, list):
        errors.append({"code": "evidence_refs", "message": "evidence_refs must be an array"})
    if bundle.get("runtime_activity_requires_minimum_evidence_refs") is not True:
        errors.append(
            {
                "code": "runtime_activity_requires_minimum_evidence_refs",
                "message": "runtime_activity_requires_minimum_evidence_refs must be true",
            }
        )
    if bundle.get("prerequisite_verdict_used_as_activation") is not False:
        errors.append(
            {
                "code": "prerequisite_verdict_used_as_activation",
                "message": "prerequisite_verdict_used_as_activation must be false",
            }
        )
    if bundle.get("narrative_only_status_allowed") is not False:
        errors.append(
            {
                "code": "narrative_only_status_allowed",
                "message": "narrative_only_status_allowed must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    if package_runtime_activity == "active" and (not isinstance(evidence_refs, list) or len(evidence_refs) < 1):
        errors.append(
            {
                "code": "evidence_refs",
                "message": "active runtime activity requires at least one evidence ref",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "offering_package_status_evidence",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "package_level": package_level,
            "package_stage": package_stage,
            "package_compliance_status": package_compliance_status,
            "package_runtime_activity": package_runtime_activity,
            "evidence_ref_count": len(evidence_refs) if isinstance(evidence_refs, list) else 0,
            "topology_status_precedence_ref": bundle.get("topology_status_precedence_ref"),
            "post_topology_consumption_required": bundle.get("post_topology_consumption_required"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
