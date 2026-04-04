import json
from pathlib import Path
from typing import Any


ALLOWED_DEPENDENCY_MODE = {
    "strict_prerequisite",
    "independent_step",
}
ALLOWED_HANDOFF_ARTIFACT_CLASS = {
    "result_artifact",
    "evidence_candidate",
    "readiness_snapshot",
}
ALLOWED_STEP_OUTCOME = {
    "pending",
    "passed",
    "failed",
    "blocked",
}
ALLOWED_WORKFLOW_GATE_MODE = {
    "fail_closed",
    "explicit_continue",
}
ALLOWED_WORKFLOW_GATE_DECISION = {
    "gate_passed",
    "gate_failed",
    "gate_blocked",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    dependency_mode = str(bundle.get("dependency_mode", "")).strip()
    handoff_artifact_class = str(bundle.get("handoff_artifact_class", "")).strip()
    step_outcome = str(bundle.get("step_outcome", "")).strip()
    workflow_gate_mode = str(bundle.get("workflow_gate_mode", "")).strip()
    workflow_gate_decision = str(bundle.get("workflow_gate_decision", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "workflow_runtime":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be workflow_runtime"})
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append({"code": "line_class", "message": "line_class must be mandatory_core_absorption_line"})
    if not str(bundle.get("workflow_id", "")).strip():
        errors.append({"code": "workflow_id", "message": "workflow_id is required"})
    if not str(bundle.get("step_id", "")).strip():
        errors.append({"code": "step_id", "message": "step_id is required"})
    if dependency_mode not in ALLOWED_DEPENDENCY_MODE:
        errors.append({"code": "dependency_mode", "message": "dependency_mode is not allowed"})
    if handoff_artifact_class not in ALLOWED_HANDOFF_ARTIFACT_CLASS:
        errors.append({"code": "handoff_artifact_class", "message": "handoff_artifact_class is not allowed"})
    if step_outcome not in ALLOWED_STEP_OUTCOME:
        errors.append({"code": "step_outcome", "message": "step_outcome is not allowed"})
    if workflow_gate_mode not in ALLOWED_WORKFLOW_GATE_MODE:
        errors.append({"code": "workflow_gate_mode", "message": "workflow_gate_mode is not allowed"})
    if workflow_gate_decision not in ALLOWED_WORKFLOW_GATE_DECISION:
        errors.append({"code": "workflow_gate_decision", "message": "workflow_gate_decision is not allowed"})
    if bundle.get("bpm_platform_expansion_allowed") is not False:
        errors.append(
            {
                "code": "bpm_platform_expansion_allowed",
                "message": "bpm_platform_expansion_allowed must be false",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append(
            {
                "code": "prose_fallback_allowed",
                "message": "prose_fallback_allowed must be false",
            }
        )

    if step_outcome == "passed" and workflow_gate_decision != "gate_passed":
        errors.append(
            {
                "code": "workflow_gate_decision",
                "message": "workflow gate must stay explicit and may not contradict a passed step outcome",
            }
        )
    if dependency_mode == "independent_step" and handoff_artifact_class == "readiness_snapshot":
        errors.append(
            {
                "code": "handoff_artifact_class",
                "message": "readiness_snapshot may not bypass governed workflow handoff dependency",
            }
        )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_runtime_plane_mode": "workflow_runtime",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "workflow_id": str(bundle.get("workflow_id", "")).strip(),
            "step_id": str(bundle.get("step_id", "")).strip(),
            "dependency_mode": dependency_mode,
            "handoff_artifact_class": handoff_artifact_class,
            "step_outcome": step_outcome,
            "workflow_gate_mode": workflow_gate_mode,
            "workflow_gate_decision": workflow_gate_decision,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
