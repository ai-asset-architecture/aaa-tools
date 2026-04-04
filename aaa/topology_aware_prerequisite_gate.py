import json
from pathlib import Path
from typing import Any


ALLOWED_TOPOLOGY_EXPECTED = {"dedicated_repo", "repo_local", "hybrid"}
ALLOWED_TOPOLOGY_DETECTED = {"dedicated_repo", "repo_local", "hybrid", "unknown"}
ALLOWED_COMPLIANCE_VERDICT = {"pass", "fail", "degraded", "not_evaluable"}
ALLOWED_EVIDENCE_SUFFICIENCY = {"sufficient", "insufficient", "partially_sufficient"}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    topology_expected = str(bundle.get("topology_expected", "")).strip()
    topology_detected = str(bundle.get("topology_detected", "")).strip()
    topology_compliance_verdict = str(bundle.get("topology_compliance_verdict", "")).strip()
    evidence_sufficiency_verdict = str(bundle.get("evidence_sufficiency_verdict", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "topology_aware_prerequisite_gate":
        errors.append(
            {
                "code": "runtime_plane_mode",
                "message": "runtime_plane_mode must be topology_aware_prerequisite_gate",
            }
        )
    if bundle.get("line_class") != "github_governance_topology_support_program":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be github_governance_topology_support_program",
            }
        )
    if topology_expected not in ALLOWED_TOPOLOGY_EXPECTED:
        errors.append({"code": "topology_expected", "message": "topology_expected is not allowed"})
    if topology_detected not in ALLOWED_TOPOLOGY_DETECTED:
        errors.append({"code": "topology_detected", "message": "topology_detected is not allowed"})
    if topology_compliance_verdict not in ALLOWED_COMPLIANCE_VERDICT:
        errors.append(
            {
                "code": "topology_compliance_verdict",
                "message": "topology_compliance_verdict is not allowed",
            }
        )
    if evidence_sufficiency_verdict not in ALLOWED_EVIDENCE_SUFFICIENCY:
        errors.append(
            {
                "code": "evidence_sufficiency_verdict",
                "message": "evidence_sufficiency_verdict is not allowed",
            }
        )
    if bundle.get("gate_verdict_is_activation") is not False:
        errors.append(
            {
                "code": "gate_verdict_is_activation",
                "message": "gate_verdict_is_activation must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append(
            {
                "code": "prose_fallback_allowed",
                "message": "prose_fallback_allowed must be false",
            }
        )

    if topology_expected != topology_detected and topology_compliance_verdict == "pass":
        errors.append(
            {
                "code": "topology_compliance_verdict",
                "message": "topology mismatch may not resolve to pass",
            }
        )
    if topology_detected == "unknown" and evidence_sufficiency_verdict == "sufficient":
        errors.append(
            {
                "code": "evidence_sufficiency_verdict",
                "message": "unknown detected topology may not claim sufficient evidence",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "topology_aware_prerequisite_gate",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "topology_expected": topology_expected,
            "topology_detected": topology_detected,
            "topology_compliance_verdict": topology_compliance_verdict,
            "evidence_sufficiency_verdict": evidence_sufficiency_verdict,
            "topology_mismatch": topology_expected != topology_detected,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
