import json
from pathlib import Path
from typing import Any, Callable

from . import repo_check_runtime_adoption
from . import runtime_adoption_readiness_inspect


COMMAND_ENTRY_MAP = {
    "readiness-inspect": "governance.readiness-inspect",
    "repo-check": "governance.repo-check",
}
REQUIRED_OUTPUT_FIELDS = {
    "status",
    "valid",
    "errors",
    "result_artifact",
}
VALIDATORS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "readiness-inspect": runtime_adoption_readiness_inspect.validate_bundle,
    "repo-check": repo_check_runtime_adoption.validate_bundle,
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_dispatch_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    command_id = str(bundle.get("command_id", "")).strip()
    dispatch_entry_ref = str(bundle.get("dispatch_entry_ref", "")).strip()
    output_envelope = [str(item).strip() for item in bundle.get("common_output_envelope", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("dispatch_runtime_id") != "shared_command_dispatch":
        errors.append({"code": "dispatch_runtime_id", "message": "dispatch_runtime_id must be shared_command_dispatch"})
    if bundle.get("runtime_plane_mode") != "command_dispatch":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be command_dispatch"})
    if bundle.get("consumed_command_registry_ref") != "internal/development/contracts/ops/command-registry-contract.v0.1.md":
        errors.append(
            {
                "code": "consumed_command_registry_ref",
                "message": "consumed_command_registry_ref must point to command-registry-contract.v0.1.md",
            }
        )
    if command_id not in COMMAND_ENTRY_MAP:
        errors.append(
            {
                "code": "command_id",
                "message": "command_id must be readiness-inspect or repo-check",
            }
        )
    expected_entry = COMMAND_ENTRY_MAP.get(command_id)
    if expected_entry and dispatch_entry_ref != expected_entry:
        errors.append(
            {
                "code": "dispatch_entry_ref",
                "message": f"dispatch_entry_ref must be {expected_entry} for {command_id}",
            }
        )
    if bundle.get("target_resolution_ref") != "governance.validate-multi-repo-worktree-identity":
        errors.append(
            {
                "code": "target_resolution_ref",
                "message": "target_resolution_ref must be governance.validate-multi-repo-worktree-identity",
            }
        )
    if bundle.get("context_preflight_ref") != "governance.validate-context-runtime-preflight":
        errors.append(
            {
                "code": "context_preflight_ref",
                "message": "context_preflight_ref must be governance.validate-context-runtime-preflight",
            }
        )
    if set(output_envelope) != REQUIRED_OUTPUT_FIELDS:
        errors.append(
            {
                "code": "common_output_envelope",
                "message": "common_output_envelope must contain status, valid, errors, result_artifact",
            }
        )
    if bundle.get("exit_semantics") != "fail_closed":
        errors.append({"code": "exit_semantics", "message": "exit_semantics must be fail_closed"})
    if bundle.get("primary_command_law_mode") != "referenced_only":
        errors.append(
            {
                "code": "primary_command_law_mode",
                "message": "primary_command_law_mode must be referenced_only",
            }
        )
    if bundle.get("family_expansion_allowed") is not False:
        errors.append(
            {
                "code": "family_expansion_allowed",
                "message": "family expansion is not allowed in shared dispatch runtime",
            }
        )
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose fallback is not allowed"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_command_id": command_id,
        "resolved_dispatch_entry_ref": dispatch_entry_ref,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def dispatch_bundle(dispatch_bundle: dict[str, Any], command_bundle: dict[str, Any]) -> dict[str, Any]:
    dispatch_result = validate_dispatch_bundle(dispatch_bundle)
    errors = list(dispatch_result["errors"])

    command_result: dict[str, Any] | None = None
    command_id = dispatch_result["resolved_command_id"]
    validator = VALIDATORS.get(command_id)
    if validator and dispatch_result["valid"]:
        command_result = validator(command_bundle)
        if not command_result["valid"]:
            errors.extend(command_result["errors"])

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "errors": errors,
        "error_codes": [item["code"] for item in errors],
        "result_artifact": {
            "command_id": command_id,
            "dispatch_entry_ref": dispatch_result["resolved_dispatch_entry_ref"],
            "command_result": command_result,
        },
    }


def dispatch_bundle_file(dispatch_bundle_path: str | Path, command_bundle_path: str | Path) -> dict[str, Any]:
    dispatch_bundle_payload = load_bundle(dispatch_bundle_path)
    command_bundle_payload = load_bundle(command_bundle_path)
    result = dispatch_bundle(dispatch_bundle_payload, command_bundle_payload)
    result["dispatch_bundle_path"] = str(Path(dispatch_bundle_path))
    result["command_bundle_path"] = str(Path(command_bundle_path))
    return result
