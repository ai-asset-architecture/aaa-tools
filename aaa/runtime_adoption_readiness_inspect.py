import json
from pathlib import Path, PurePosixPath
from typing import Any

from . import context_runtime_preflight
from . import multi_repo_worktree_identity
from . import session_readiness_state
from . import tool_command_adoption


ALLOWED_TARGET_SCOPE = "repo_or_worktree"
ALLOWED_TARGET_KINDS = {
    "canonical_repo_root",
    "legal_worktree_instance",
}
ALLOWED_AUTHORITIES = {
    "read_only",
    "analysis_only",
}
REQUIRED_TOOL_CHAIN = [
    "governance.validate-tool-command-adoption",
    "governance.validate-multi-repo-worktree-identity",
    "governance.validate-context-runtime-preflight",
    "governance.validate-session-readiness-state",
]


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


def _derive_tool_command_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": "v0.1",
        "tool_refs": bundle.get("tool_chain_refs", []),
        "command_refs": [bundle.get("command_id")],
        "binding_mode": bundle.get("binding_mode"),
        "allowed_authority_map": {
            str(bundle.get("command_id", "")).strip(): bundle.get("allowed_authority", []),
        },
        "evidence_targets": [bundle.get("expected_output_artifact")],
    }


def _derive_identity_bundle(target_kind: str, target_path: str) -> dict[str, Any]:
    canonical_repo_root = _derive_canonical_repo_root(target_kind, target_path)
    worktree_instances = (
        [_normalize_worktree_path(target_path)]
        if target_kind == "legal_worktree_instance"
        else [f"{canonical_repo_root}/.worktrees/readiness-inspect-shadow"]
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


def _derive_readiness_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    readiness_surface = str(bundle.get("readiness_surface", "")).strip()
    query_state_store = "readiness_snapshot" if readiness_surface == "readiness_panel" else "transcript_store"
    return {
        "version": "v0.1",
        "orchestration_mode": "operator_review_session",
        "query_state_store": query_state_store,
        "readiness_surface": readiness_surface,
        "readiness_checks": bundle.get("readiness_checks", []),
    }


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    command_id = str(bundle.get("command_id", "")).strip()
    binding_mode = str(bundle.get("binding_mode", "")).strip()
    target_scope = str(bundle.get("target_scope", "")).strip()
    target_kind = str(bundle.get("target_kind", "")).strip()
    target_path = str(bundle.get("target_path", "")).strip()
    expected_output_artifact = str(bundle.get("expected_output_artifact", "")).strip()
    prose_fallback_allowed = bundle.get("prose_fallback_allowed")
    allowed_authority = [str(item).strip() for item in bundle.get("allowed_authority", [])]
    tool_chain_refs = [str(item).strip() for item in bundle.get("tool_chain_refs", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if command_id != "readiness-inspect":
        errors.append({"code": "command_id", "message": "command_id must be readiness-inspect"})
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
    if expected_output_artifact != "readiness_state_report":
        errors.append(
            {
                "code": "expected_output_artifact",
                "message": "expected_output_artifact must be readiness_state_report",
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

    missing_tool_chain = [item for item in REQUIRED_TOOL_CHAIN if item not in tool_chain_refs]
    if missing_tool_chain:
        errors.append(
            {
                "code": "tool_chain_refs",
                "message": f"missing required tool chain refs: {', '.join(missing_tool_chain)}",
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
                "message": "workspace_root cannot be used as runtime adoption target",
            }
        )

    derived_results: dict[str, Any] = {}
    tool_result = tool_command_adoption.validate_bundle(_derive_tool_command_bundle(bundle))
    identity_result = multi_repo_worktree_identity.validate_bundle(_derive_identity_bundle(target_kind, target_path))
    preflight_result = context_runtime_preflight.validate_bundle(
        {
            "version": "v0.1",
            "bundle_id": "runtime-adoption.readiness-inspect.preflight.v0.1",
            "current_truth_sources": bundle.get("current_truth_sources", []),
            "supporting_sources": bundle.get("supporting_sources", []),
            "preflight_checks": bundle.get("preflight_checks", []),
        }
    )
    readiness_result = session_readiness_state.validate_bundle(_derive_readiness_bundle(bundle))

    derived_results["tool_command_adoption"] = tool_result
    derived_results["multi_repo_worktree_identity"] = identity_result
    derived_results["context_runtime_preflight"] = preflight_result
    derived_results["session_readiness_state"] = readiness_result

    for result in derived_results.values():
        if result["valid"]:
            continue
        for item in result["errors"]:
            errors.append(item)

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_command_id": command_id,
        "resolved_target_kind": target_kind,
        "resolved_target_path": target_path,
        "resolved_tool_chain_refs": tool_chain_refs,
        "derived_results": derived_results,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    bundle = load_bundle(bundle_path)
    result = validate_bundle(bundle)
    result["bundle_path"] = str(Path(bundle_path))
    return result
