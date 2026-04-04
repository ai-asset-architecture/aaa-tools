import json
from pathlib import Path
from typing import Any


ALLOWED_COMMAND_IDS = {
    "readiness-inspect",
    "repo-check",
}
ALLOWED_AUTHORITY = {
    "read_only",
    "analysis_only",
    "governance_gate",
}
ALLOWED_DECISION_MODES = {
    "allow",
    "deny",
    "ask",
    "auto_deny",
}
ALLOWED_INTERACTIVE_MODES = {
    "prompt_allowed",
    "prompt_not_required",
}
ALLOWED_NON_INTERACTIVE_MODES = {
    "auto_deny",
    "preauthorized_only",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    command_id = str(bundle.get("command_id", "")).strip()
    allowed_authority = [str(item).strip() for item in bundle.get("allowed_authority", [])]
    decision_mode = str(bundle.get("decision_mode", "")).strip()
    interactive_mode = str(bundle.get("interactive_mode", "")).strip()
    non_interactive_mode = str(bundle.get("non_interactive_mode", "")).strip()

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("runtime_plane_mode") != "permission_gate":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be permission_gate"})
    if bundle.get("line_class") != "mandatory_core_absorption_line":
        errors.append(
            {
                "code": "line_class",
                "message": "line_class must be mandatory_core_absorption_line",
            }
        )
    if bundle.get("permission_context_ref") != "internal/development/contracts/ops/tool-contract.v0.1.md":
        errors.append(
            {
                "code": "permission_context_ref",
                "message": "permission_context_ref must point to tool-contract.v0.1.md",
            }
        )
    if command_id not in ALLOWED_COMMAND_IDS:
        errors.append(
            {
                "code": "command_id",
                "message": "command_id must be readiness-inspect or repo-check",
            }
        )

    invalid_authority = [item for item in allowed_authority if item not in ALLOWED_AUTHORITY]
    if invalid_authority or not allowed_authority:
        errors.append(
            {
                "code": "allowed_authority",
                "message": "allowed_authority must contain one or more supported authority classes",
            }
        )
    if decision_mode not in ALLOWED_DECISION_MODES:
        errors.append({"code": "decision_mode", "message": "decision_mode is not allowed"})
    if interactive_mode not in ALLOWED_INTERACTIVE_MODES:
        errors.append({"code": "interactive_mode", "message": "interactive_mode is not allowed"})
    if non_interactive_mode not in ALLOWED_NON_INTERACTIVE_MODES:
        errors.append(
            {
                "code": "non_interactive_mode",
                "message": "non_interactive_mode is not allowed",
            }
        )

    if decision_mode == "allow" and "governance_gate" in allowed_authority:
        errors.append(
            {
                "code": "authority_decision_conflict",
                "message": "governance_gate authority may not resolve directly to allow",
            }
        )
    if non_interactive_mode == "auto_deny" and interactive_mode == "prompt_allowed":
        errors.append(
            {
                "code": "non_interactive_prompt_conflict",
                "message": "non-interactive mode may not require prompt interaction",
            }
        )
    if bundle.get("primary_law_creation_allowed") is not False:
        errors.append(
            {
                "code": "primary_law_creation_allowed",
                "message": "primary_law_creation_allowed must be false",
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
        "resolved_runtime_plane_mode": "permission_gate",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
        "derived_results": {
            "command_id": command_id,
            "decision_mode": decision_mode,
            "interactive_mode": interactive_mode,
            "non_interactive_mode": non_interactive_mode,
            "allowed_authority": allowed_authority,
        },
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
