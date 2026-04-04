import json
from pathlib import Path
from typing import Any


ALLOWED_ARTIFACT_KINDS = {
    "dispatch_result_envelope",
    "readiness_state_report",
    "repo_check_report",
}
ALLOWED_EVIDENCE_CLASSES = {
    "artifact_report",
    "completion_evidence",
    "audit_evidence",
}
ALLOWED_EVIDENCE_SOURCES = {
    "eligible_result_artifact",
    "promotion_gated_evidence_bundle",
}
ALLOWED_SUPPORTING_REVIEW_SOURCES = {
    "operator_narrative",
    "manual_review_note",
    "completion_report",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    result_artifact_kind = str(bundle.get("result_artifact_kind", "")).strip()
    evidence_class = str(bundle.get("evidence_class", "")).strip()
    promotion_decision_source = str(bundle.get("promotion_decision_source", "")).strip()
    evidence_source = str(bundle.get("evidence_source", "")).strip()
    supporting_review_sources = [str(item).strip() for item in bundle.get("supporting_review_sources", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("promotion_gate_id") != "result_artifact_evidence_promotion_gate":
        errors.append(
            {
                "code": "promotion_gate_id",
                "message": "promotion_gate_id must be result_artifact_evidence_promotion_gate",
            }
        )
    if bundle.get("runtime_plane_mode") != "result_evidence_gate":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be result_evidence_gate"})
    if result_artifact_kind not in ALLOWED_ARTIFACT_KINDS:
        errors.append({"code": "result_artifact_kind", "message": "result_artifact_kind is not allowed"})
    if str(bundle.get("artifact_eligibility", "")).strip() not in {"eligible", "ineligible"}:
        errors.append({"code": "artifact_eligibility", "message": "artifact_eligibility must be eligible or ineligible"})
    if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
        errors.append({"code": "evidence_class", "message": "evidence_class is not allowed"})
    if str(bundle.get("promotion_eligibility", "")).strip() not in {"promotable", "blocked"}:
        errors.append({"code": "promotion_eligibility", "message": "promotion_eligibility must be promotable or blocked"})
    if promotion_decision_source != "machine_checkable_gate":
        errors.append(
            {
                "code": "promotion_decision_source",
                "message": "promotion_decision_source must be machine_checkable_gate",
            }
        )
    if evidence_source not in ALLOWED_EVIDENCE_SOURCES:
        errors.append(
            {
                "code": "evidence_source",
                "message": "evidence_source must be eligible_result_artifact or promotion_gated_evidence_bundle",
            }
        )
    invalid_supporting_sources = [item for item in supporting_review_sources if item not in ALLOWED_SUPPORTING_REVIEW_SOURCES]
    if invalid_supporting_sources:
        errors.append(
            {
                "code": "supporting_review_sources",
                "message": f"unsupported supporting_review_sources: {', '.join(invalid_supporting_sources)}",
            }
        )
    if bundle.get("sole_manual_decision_allowed") is not False:
        errors.append(
            {
                "code": "sole_manual_decision_allowed",
                "message": "sole_manual_decision_allowed must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_gate_id": "result_artifact_evidence_promotion_gate",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "promotion_decision_source": promotion_decision_source,
            "evidence_source": evidence_source,
            "artifact_eligibility": bundle.get("artifact_eligibility"),
            "promotion_eligibility": bundle.get("promotion_eligibility"),
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
