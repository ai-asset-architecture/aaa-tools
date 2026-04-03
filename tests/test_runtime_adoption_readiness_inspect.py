import json
from pathlib import Path

from typer.testing import CliRunner

from aaa.cli import app
from aaa import runtime_adoption_readiness_inspect


PASS_BUNDLE = {
    "version": "v0.1",
    "command_id": "readiness-inspect",
    "binding_mode": "machine_parseable",
    "target_scope": "repo_or_worktree",
    "target_kind": "legal_worktree_instance",
    "target_path": "/repo/aaa-tpl-docs/.worktrees/v2-1-5-readiness",
    "allowed_authority": [
        "read_only",
        "analysis_only",
    ],
    "tool_chain_refs": [
        "governance.validate-tool-command-adoption",
        "governance.validate-multi-repo-worktree-identity",
        "governance.validate-context-runtime-preflight",
        "governance.validate-session-readiness-state",
    ],
    "current_truth_sources": [
        "canonical_contract_docs",
        "canonical_registries_indexes",
        "repo_tracked_files",
    ],
    "supporting_sources": [
        "external_execution_outputs",
        "generated_runtime_summaries",
    ],
    "preflight_checks": [
        "current_truth_source_check",
        "supporting_source_check",
        "anti_contamination_check",
        "promotion_block_check",
    ],
    "readiness_surface": "gate_status_surface",
    "readiness_checks": [
        "context_loaded",
        "authority_resolved",
        "preflight_passed",
        "evidence_path_bound",
    ],
    "expected_output_artifact": "readiness_state_report",
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "command_id": "readiness-inspect",
    "binding_mode": "machine_parseable",
    "target_scope": "repo_or_worktree",
    "target_kind": "workspace_root",
    "target_path": "/repo/AAA_WORKSPACE",
    "allowed_authority": [
        "analysis_only",
    ],
    "tool_chain_refs": [
        "governance.validate-tool-command-adoption",
        "governance.validate-multi-repo-worktree-identity",
        "governance.validate-context-runtime-preflight",
        "governance.validate-session-readiness-state",
    ],
    "current_truth_sources": [
        "canonical_contract_docs",
        "local_operation_logs",
    ],
    "supporting_sources": [
        "local_operation_logs",
    ],
    "preflight_checks": [
        "anti_contamination_check",
    ],
    "readiness_surface": "readiness_panel",
    "readiness_checks": [
        "context_loaded",
    ],
    "expected_output_artifact": "readiness_state_report",
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_machine_parseable_readiness_inspect_chain():
    result = runtime_adoption_readiness_inspect.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_command_id"] == "readiness-inspect"
    assert result["resolved_target_kind"] == "legal_worktree_instance"
    assert result["derived_results"]["tool_command_adoption"]["valid"] is True
    assert result["derived_results"]["multi_repo_worktree_identity"]["valid"] is True
    assert result["derived_results"]["context_runtime_preflight"]["valid"] is True
    assert result["derived_results"]["session_readiness_state"]["valid"] is True


def test_validate_bundle_rejects_workspace_target_local_truth_promotion_and_prose_fallback():
    result = runtime_adoption_readiness_inspect.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "target_kind" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]
    assert "current_truth_sources" in result["error_codes"]
    assert "readiness_checks" in result["error_codes"]


def test_cli_readiness_inspect_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "readiness-inspect", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_readiness_inspect_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "readiness-inspect", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "target_kind" in payload["error_codes"]
