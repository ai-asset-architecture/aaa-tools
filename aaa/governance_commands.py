from pathlib import Path
from typing import Any

from . import context_runtime_preflight
from . import governance_index
from . import multi_repo_worktree_identity
from . import permission_and_authorization_runtime_gate
from . import repo_check_runtime_adoption
from . import query_orchestration_runtime
from . import result_artifact_eligibility_and_evidence_promotion_gate
from . import runtime_adoption_readiness_inspect
from . import runtime_budget_retry_and_recovery_control
from . import session_context_snapshot_runtime
from . import session_persistence_and_transcript_compaction
from . import session_readiness_state
from . import shared_command_dispatch_runtime
from . import structured_output_and_result_normalization_plane
from . import tool_command_adoption
from . import tool_progress_and_runtime_event_stream
from . import workflow_and_runbook_orchestration_runtime


def update_index_cli(
    *,
    target_dir: str,
    pattern: str,
    readme_template: str,
    index_output: str = "index.json",
    metadata_fields: list[str] | None = None,
    include_frontmatter: bool = True,
    sort_by: str = "filename",
    hash_algo: str = "sha256",
    dry_run: bool = False,
) -> dict[str, Any]:
    return governance_index.update_index(
        target_dir=Path(target_dir),
        pattern=pattern,
        readme_template=readme_template,
        index_output=index_output,
        metadata_fields=metadata_fields,
        include_frontmatter=include_frontmatter,
        sort_by=sort_by,
        hash_algo=hash_algo,
        dry_run=dry_run,
    )


def validate_tool_command_adoption_cli(*, bundle: str) -> dict[str, Any]:
    return tool_command_adoption.validate_bundle_file(bundle)


def validate_multi_repo_worktree_identity_cli(*, bundle: str) -> dict[str, Any]:
    return multi_repo_worktree_identity.validate_bundle_file(bundle)


def validate_context_runtime_preflight_cli(*, bundle: str) -> dict[str, Any]:
    return context_runtime_preflight.validate_bundle_file(bundle)


def validate_session_readiness_state_cli(*, bundle: str) -> dict[str, Any]:
    return session_readiness_state.validate_bundle_file(bundle)


def readiness_inspect_cli(*, bundle: str) -> dict[str, Any]:
    return runtime_adoption_readiness_inspect.validate_bundle_file(bundle)


def repo_check_cli(*, bundle: str) -> dict[str, Any]:
    return repo_check_runtime_adoption.validate_bundle_file(bundle)


def shared_command_dispatch_cli(*, dispatch_bundle: str, command_bundle: str) -> dict[str, Any]:
    return shared_command_dispatch_runtime.dispatch_bundle_file(dispatch_bundle, command_bundle)


def result_evidence_promotion_gate_cli(*, bundle: str) -> dict[str, Any]:
    return result_artifact_eligibility_and_evidence_promotion_gate.validate_bundle_file(bundle)


def session_context_snapshot_cli(*, bundle: str) -> dict[str, Any]:
    return session_context_snapshot_runtime.validate_bundle_file(bundle)


def query_orchestration_cli(*, bundle: str) -> dict[str, Any]:
    return query_orchestration_runtime.validate_bundle_file(bundle)


def permission_gate_cli(*, bundle: str) -> dict[str, Any]:
    return permission_and_authorization_runtime_gate.validate_bundle_file(bundle)


def event_stream_cli(*, bundle: str) -> dict[str, Any]:
    return tool_progress_and_runtime_event_stream.validate_bundle_file(bundle)


def session_persistence_cli(*, bundle: str) -> dict[str, Any]:
    return session_persistence_and_transcript_compaction.validate_bundle_file(bundle)


def runtime_control_cli(*, bundle: str) -> dict[str, Any]:
    return runtime_budget_retry_and_recovery_control.validate_bundle_file(bundle)


def result_normalization_cli(*, bundle: str) -> dict[str, Any]:
    return structured_output_and_result_normalization_plane.validate_bundle_file(bundle)


def workflow_runtime_cli(*, bundle: str) -> dict[str, Any]:
    return workflow_and_runbook_orchestration_runtime.validate_bundle_file(bundle)
