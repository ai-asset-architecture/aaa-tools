import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import session_context_snapshot_runtime
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "snapshot_runtime_id": "session_context_snapshot",
    "runtime_plane_mode": "context_snapshot",
    "context_assembly_ref": "internal/development/contracts/ops/context-assembly-contract.v0.1.md",
    "static_context_refs": [
        "canonical_contract_docs",
        "canonical_registries_indexes",
    ],
    "dynamic_context_refs": [
        "repo_tracked_files",
        "worktree_state",
    ],
    "disallowed_input_sources": [
        "local_operation_logs",
        "generated_runtime_summaries",
    ],
    "snapshot_persistence_mode": "session_snapshot_store",
    "reload_semantics": "explicit_reload_only",
    "replay_semantics": "canonical_recheck_before_replay",
    "canonical_writeback_allowed": False,
    "canonical_truth_promotion_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "snapshot_runtime_id": "session_context_snapshot",
    "runtime_plane_mode": "context_snapshot",
    "context_assembly_ref": "internal/development/contracts/ops/context-assembly-contract.v0.1.md",
    "static_context_refs": [
        "canonical_contract_docs",
        "local_operation_logs",
    ],
    "dynamic_context_refs": [
        "repo_tracked_files",
    ],
    "disallowed_input_sources": [
        "generated_runtime_summaries",
    ],
    "snapshot_persistence_mode": "ephemeral_cache",
    "reload_semantics": "implicit_auto_reload",
    "replay_semantics": "replay_without_recheck",
    "canonical_writeback_allowed": True,
    "canonical_truth_promotion_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_snapshot_runtime_plane():
    result = session_context_snapshot_runtime.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_snapshot_runtime_id"] == "session_context_snapshot"


def test_validate_bundle_rejects_truth_promotion_and_implicit_reload_replay():
    result = session_context_snapshot_runtime.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "static_context_refs" in result["error_codes"]
    assert "disallowed_input_sources" in result["error_codes"]
    assert "reload_semantics" in result["error_codes"]
    assert "replay_semantics" in result["error_codes"]
    assert "canonical_writeback_allowed" in result["error_codes"]
    assert "canonical_truth_promotion_allowed" in result["error_codes"]


def test_cli_session_context_snapshot_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "session-context-snapshot", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_session_context_snapshot_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "session-context-snapshot", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "canonical_truth_promotion_allowed" in payload["error_codes"]
