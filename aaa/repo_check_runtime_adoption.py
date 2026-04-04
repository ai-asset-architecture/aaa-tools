import json
from pathlib import Path, PurePosixPath
from typing import Any

from . import context_runtime_preflight
from . import multi_repo_worktree_identity


ALLOWED_TARGET_SCOPE = "repo_or_worktree"
ALLOWED_TARGET_KINDS = {
    "canonical_repo_root",
    "legal_worktree_instance",
}
ALLOWED_AUTHORITIES = {
    "analysis_only",
    "governance_gate",
}
ALLOWED_CONSUMER_SURFACES = {
    "operator_summary",
    "gate_status_surface",
    "readiness_panel",
}
REQUIRED_CHECK_RESULTS = {
    "repo_identity_resolved",
    "suite_resolved",
    "checks_executed",
    "overall_status_computed",
    "evidence_refs_bound",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def _looks_like_workspace_root(path: str) -> bool:
    lowered = PurePosixPath(path).name.lower()
    return "workspace" in lowered


def _derive_canonical_repo_root(target_kind: str, target_path: str) -> str:
    if target_kind == "canonical_repo_root":
        return target_path.rstrip("/")
    if target_path.startswith(".worktrees/"):
        return "."
    return target_path.split("/.worktrees/")[0].rstrip("/")


def _normalize_worktree_path(target_path: str) -> str:
    if target_path.startswith(".worktrees/"):
        return f"./{target_path}"
    return target_path


def _derive_identity_bundle(target_kind: str, target_path: str) -> dict[str, Any]:
    canonical_repo_root = _derive_canonical_repo_root(target_kind, target_path)
    worktree_instances = (
        [_normalize_worktree_path(target_path)]
        if target_kind == "legal_worktree_instance"
        else [f"{canonical_repo_root}/.worktrees/repo-check-shadow"]
    )
    return {
        "version": "v0.1",
        "canonical_repo_root": canonical_repo_root,
        "worktree_instances": worktree_instances,
        "validator_rules": [
            "require_canonical_repo_root",
            "reject_workspace_root_as_repo_target",
            "reject_unknown_worktree_target",
        ],
        "runtime_guards": [
            "canonical_root_guard",
            "worktree_target_guard",
            "target_scope_guard",
        ],
    }


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    command_id = str(bundle.get("command_id", "")).strip()
    binding_mode = str(bundle.get("binding_mode", "")).strip()
    target_scope = str(bundle.get("target_scope", "")).strip()
    target_kind = str(bundle.get("target_kind", "")).strip()
    target_path = str(bundle.get("target_path", "")).strip()
    prose_fallback_allowed = bundle.get("prose_fallback_allowed")
    expected_output_artifact = str(bundle.get("expected_output_artifact", "")).strip()
    allowed_authority = [str(item).strip() for item in bundle.get("allowed_authority", [])]
    current_truth_sources = bundle.get("current_truth_sources", [])
    supporting_sources = bundle.get("supporting_sources", [])
    preflight_checks = bundle.get("preflight_checks", [])
    required_check_results = [str(item).strip() for item in bundle.get("required_check_results", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if command_id != "repo-check":
        errors.append({"code": "command_id", "message": "command_id must be repo-check"})
    if binding_mode != "machine_parseable":
        errors.append({"code": "binding_mode", "message": "binding_mode must be machine_parseable"})
    if target_scope != ALLOWED_TARGET_SCOPE:
        errors.append({"code": "target_scope", "message": "target_scope must be repo_or_worktree"})
    if target_kind not in ALLOWED_TARGET_KINDS:
        errors.append(
            {
                "code": "target_kind",
                "message": "target_kind must be canonical_repo_root or legal_worktree_instance",
            }
        )
    if not target_path:
        errors.append({"code": "target_path", "message": "target_path is required"})
    if prose_fallback_allowed is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose fallback is not allowed"})
    if expected_output_artifact != "repo_check_result_bundle":
        errors.append(
            {
                "code": "expected_output_artifact",
                "message": "expected_output_artifact must be repo_check_result_bundle",
            }
        )

    invalid_authority = [item for item in allowed_authority if item not in ALLOWED_AUTHORITIES]
    if invalid_authority:
        errors.append(
            {
                "code": "allowed_authority",
                "message": f"illegal authority values: {', '.join(sorted(invalid_authority))}",
            }
        )

    if target_kind == "legal_worktree_instance" and "/.worktrees/" not in target_path and not target_path.startswith(
        ".worktrees/"
    ):
        errors.append(
            {
                "code": "target_path",
                "message": "legal_worktree_instance target_path must live under /.worktrees/",
            }
        )
    if target_kind == "canonical_repo_root" and "/.worktrees/" in target_path:
        errors.append(
            {
                "code": "target_path",
                "message": "canonical_repo_root target_path cannot point to a worktree instance",
            }
        )
    if target_path and _looks_like_workspace_root(target_path):
        errors.append(
            {
                "code": "target_kind",
                "message": "workspace_root cannot be used as repo-check runtime target",
            }
        )

    result_shape_contract = bundle.get("result_shape_contract", {})
    required_fields = [str(item).strip() for item in result_shape_contract.get("required_fields", [])]
    if result_shape_contract.get("result_kind") != "repo_check_result_bundle":
        errors.append({"code": "result_shape_contract", "message": "result_kind must be repo_check_result_bundle"})
    if result_shape_contract.get("machine_checkable") is not True:
        errors.append({"code": "result_shape_contract", "message": "result shape must be machine checkable"})
    if "overall_status" not in required_fields or "evidence_refs" not in required_fields:
        errors.append(
            {
                "code": "result_shape_contract",
                "message": "required_fields must include overall_status and evidence_refs",
            }
        )

    readiness_consumer_relation = bundle.get("readiness_consumer_relation", {})
    if readiness_consumer_relation.get("relation_mode") != "consumable_by_readiness_surface":
        errors.append(
            {
                "code": "readiness_consumer_relation",
                "message": "relation_mode must be consumable_by_readiness_surface",
            }
        )
    consumer_surface = str(readiness_consumer_relation.get("consumer_surface", "")).strip()
    if consumer_surface not in ALLOWED_CONSUMER_SURFACES:
        errors.append(
            {
                "code": "readiness_consumer_relation",
                "message": "consumer_surface must be operator_summary, gate_status_surface, or readiness_panel",
            }
        )
    if readiness_consumer_relation.get("machine_checkable") is not True:
        errors.append(
            {
                "code": "readiness_consumer_relation",
                "message": "readiness consumer relation must be machine checkable",
            }
        )

    missing_required_results = [item for item in REQUIRED_CHECK_RESULTS if item not in required_check_results]
    if missing_required_results:
        errors.append(
            {
                "code": "required_check_results",
                "message": f"missing required check results: {', '.join(sorted(missing_required_results))}",
            }
        )

    identity_result = multi_repo_worktree_identity.validate_bundle(_derive_identity_bundle(target_kind, target_path))
    preflight_result = context_runtime_preflight.validate_bundle(
        {
            "version": "v0.1",
            "bundle_id": "runtime-adoption.repo-check.preflight.v0.1",
            "current_truth_sources": current_truth_sources,
            "supporting_sources": supporting_sources,
            "preflight_checks": preflight_checks,
        }
    )

    derived_results = {
        "multi_repo_worktree_identity": identity_result,
        "context_runtime_preflight": preflight_result,
    }
    for result in derived_results.values():
        if result["valid"]:
            continue
        errors.extend(result["errors"])

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_command_id": command_id,
        "resolved_target_kind": target_kind,
        "resolved_target_path": target_path,
        "resolved_required_check_results": required_check_results,
        "derived_results": derived_results,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    bundle = load_bundle(bundle_path)
    result = validate_bundle(bundle)
    result["bundle_path"] = str(Path(bundle_path))
    return result
