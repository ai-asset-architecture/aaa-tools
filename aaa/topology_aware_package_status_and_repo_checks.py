import json
from pathlib import Path
from typing import Any


ALLOWED_EXPECTED = {"dedicated_repo", "repo_local", "hybrid"}
ALLOWED_DETECTED = {"dedicated_repo", "repo_local", "hybrid", "unknown"}
ALLOWED_RESOLVED = {"dedicated_repo", "repo_local", "hybrid", "degraded", "not_evaluable"}
ALLOWED_COMPLIANCE = {"compliant", "non_compliant", "compliant_with_gap"}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    topology_mode_expected = str(bundle.get("topology_mode_expected", "")).strip()
    topology_mode_detected = str(bundle.get("topology_mode_detected", "")).strip()
    topology_mode_resolved = str(bundle.get("topology_mode_resolved", "")).strip()
    topology_compliance_status = str(bundle.get("topology_compliance_status", "")).strip()
    missing_governance_assets = bundle.get("missing_governance_assets", [])
    misplaced_governance_assets = bundle.get("misplaced_governance_assets", [])

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "topology_aware_package_status_and_repo_checks":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be topology_aware_package_status_and_repo_checks",
            }
        )
    if bundle.get("line_class") != "github_governance_topology_support_program":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be github_governance_topology_support_program",
            }
        )
    if topology_mode_expected not in ALLOWED_EXPECTED:
        errors.append({"code": "topology_mode_expected", "message": "topology_mode_expected is not allowed"})
    if topology_mode_detected not in ALLOWED_DETECTED:
        errors.append({"code": "topology_mode_detected", "message": "topology_mode_detected is not allowed"})
    if topology_mode_resolved not in ALLOWED_RESOLVED:
        errors.append({"code": "topology_mode_resolved", "message": "topology_mode_resolved is not allowed"})
    if topology_compliance_status not in ALLOWED_COMPLIANCE:
        errors.append(
            {
                "code": "topology_compliance_status",
                "message": "topology_compliance_status is not allowed",
            }
        )
    if not isinstance(missing_governance_assets, list):
        errors.append(
            {
                "code": "missing_governance_assets",
                "message": "missing_governance_assets must be an array",
            }
        )
    if not isinstance(misplaced_governance_assets, list):
        errors.append(
            {
                "code": "misplaced_governance_assets",
                "message": "misplaced_governance_assets must be an array",
            }
        )
    if bundle.get("narrative_only_compliance_allowed") is not False:
        errors.append(
            {
                "code": "narrative_only_compliance_allowed",
                "message": "narrative_only_compliance_allowed must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append(
            {
                "code": "prose_fallback_allowed",
                "message": "prose_fallback_allowed must be false",
            }
        )

    if topology_mode_expected == "repo_local" and ".github repo" in [str(item).strip() for item in missing_governance_assets]:
        errors.append(
            {
                "code": "missing_governance_assets",
                "message": "repo_local may not report missing .github repo as a required governance asset",
            }
        )
    if topology_mode_resolved in {"degraded", "not_evaluable"} and topology_compliance_status == "compliant":
        errors.append(
            {
                "code": "topology_mode_resolved",
                "message": "degraded or not_evaluable resolved topology may not claim compliant status",
            }
        )
    if topology_mode_detected == "unknown" and topology_mode_resolved in {"dedicated_repo", "repo_local", "hybrid"}:
        errors.append(
            {
                "code": "topology_mode_resolved",
                "message": "unknown detected topology may not resolve directly to a concrete topology mode",
            }
        )
    if topology_mode_detected != "unknown" and topology_mode_resolved == "not_evaluable":
        errors.append(
            {
                "code": "topology_mode_resolved",
                "message": "detected topology with evidence may not resolve to not_evaluable",
            }
        )

    structure_acceptance_status = "structure_accepted"
    if topology_mode_detected == "unknown":
        structure_acceptance_status = "structure_not_detected"
    elif topology_mode_expected != topology_mode_detected:
        structure_acceptance_status = "structure_mismatch"

    if topology_compliance_status == "compliant" and topology_mode_resolved in {"dedicated_repo", "repo_local", "hybrid"}:
        topology_completion_status = "topology_compliant"
    elif topology_compliance_status == "non_compliant":
        topology_completion_status = "topology_non_compliant"
    else:
        topology_completion_status = "topology_evidence_incomplete"

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "topology_aware_package_status_and_repo_checks",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "topology_mode_expected": topology_mode_expected,
            "topology_mode_detected": topology_mode_detected,
            "topology_mode_resolved": topology_mode_resolved,
            "topology_compliance_status": topology_compliance_status,
            "structure_acceptance_status": structure_acceptance_status,
            "topology_completion_status": topology_completion_status,
            "downstream_topology_adjudication_point": "topology_aware_package_status_and_repo_checks",
            "missing_governance_assets": missing_governance_assets,
            "misplaced_governance_assets": misplaced_governance_assets,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
