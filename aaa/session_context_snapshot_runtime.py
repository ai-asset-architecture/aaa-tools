import json
from pathlib import Path
from typing import Any


STATIC_CONTEXT_REFS = {
    "canonical_contract_docs",
    "canonical_registries_indexes",
    "preserved_completion_audit_artifacts",
}
DYNAMIC_CONTEXT_REFS = {
    "repo_tracked_files",
    "worktree_state",
}
DISALLOWED_INPUT_SOURCES = {
    "local_operation_logs",
    "generated_runtime_summaries",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    static_context_refs = [str(item).strip() for item in bundle.get("static_context_refs", [])]
    dynamic_context_refs = [str(item).strip() for item in bundle.get("dynamic_context_refs", [])]
    disallowed_input_sources = [str(item).strip() for item in bundle.get("disallowed_input_sources", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})
    if bundle.get("snapshot_runtime_id") != "session_context_snapshot":
        errors.append({"code": "snapshot_runtime_id", "message": "snapshot_runtime_id must be session_context_snapshot"})
    if bundle.get("runtime_plane_mode") != "context_snapshot":
        errors.append({"code": "runtime_plane_mode", "message": "runtime_plane_mode must be context_snapshot"})
    if bundle.get("context_assembly_ref") != "internal/development/contracts/ops/context-assembly-contract.v0.1.md":
        errors.append({"code": "context_assembly_ref", "message": "context_assembly_ref must point to context-assembly-contract.v0.1.md"})

    invalid_static = [item for item in static_context_refs if item not in STATIC_CONTEXT_REFS]
    if invalid_static or len(static_context_refs) < 2:
        errors.append({"code": "static_context_refs", "message": "static_context_refs must contain only canonical static sources with at least two items"})
    invalid_dynamic = [item for item in dynamic_context_refs if item not in DYNAMIC_CONTEXT_REFS]
    if invalid_dynamic or len(dynamic_context_refs) < 1:
        errors.append({"code": "dynamic_context_refs", "message": "dynamic_context_refs must contain only repo_tracked_files/worktree_state"})
    if set(disallowed_input_sources) != DISALLOWED_INPUT_SOURCES:
        errors.append({"code": "disallowed_input_sources", "message": "disallowed_input_sources must contain local_operation_logs and generated_runtime_summaries"})
    if bundle.get("snapshot_persistence_mode") not in {"session_snapshot_store", "ephemeral_cache"}:
        errors.append({"code": "snapshot_persistence_mode", "message": "snapshot_persistence_mode must be session_snapshot_store or ephemeral_cache"})
    if bundle.get("reload_semantics") != "explicit_reload_only":
        errors.append({"code": "reload_semantics", "message": "reload_semantics must be explicit_reload_only"})
    if bundle.get("replay_semantics") != "canonical_recheck_before_replay":
        errors.append({"code": "replay_semantics", "message": "replay_semantics must be canonical_recheck_before_replay"})
    if bundle.get("canonical_writeback_allowed") is not False:
        errors.append({"code": "canonical_writeback_allowed", "message": "canonical_writeback_allowed must be false"})
    if bundle.get("canonical_truth_promotion_allowed") is not False:
        errors.append({"code": "canonical_truth_promotion_allowed", "message": "canonical_truth_promotion_allowed must be false"})
    if bundle.get("prose_fallback_allowed") is not False:
        errors.append({"code": "prose_fallback_allowed", "message": "prose_fallback_allowed must be false"})

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "resolved_snapshot_runtime_id": "session_context_snapshot",
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    payload = load_bundle(bundle_path)
    result = validate_bundle(payload)
    result["bundle_path"] = str(Path(bundle_path))
    return result
