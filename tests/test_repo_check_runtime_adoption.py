import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import repo_check_runtime_adoption
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "command_id": "repo-check",
    "binding_mode": "machine_parseable",
    "target_scope": "repo_or_worktree",
    "target_kind": "canonical_repo_root",
    "target_path": "aaa-tools",
    "allowed_authority": [
        "analysis_only",
        "governance_gate",
    ],
    "tool_contract_ref": "internal/development/contracts/ops/tool-contract.v0.1.md",
    "command_contract_ref": "internal/development/contracts/ops/command-registry-contract.v0.1.md",
    "identity_contract_ref": "internal/development/contracts/ops/multi-repo-worktree-identity-guard.v0.1.schema.json",
    "context_contract_ref": "internal/development/contracts/ops/context-assembly-contract.v0.1.md",
    "readiness_contract_ref": "internal/development/contracts/ops/session-readiness-state.v0.1.schema.json",
    "result_shape_contract": {
        "result_kind": "repo_check_result_bundle",
        "required_fields": [
            "repo_id",
            "suite_id",
            "check_results",
            "overall_status",
            "evidence_refs",
        ],
        "machine_checkable": True,
    },
    "readiness_consumer_relation": {
        "relation_mode": "consumable_by_readiness_surface",
        "consumer_surface": "gate_status_surface",
        "machine_checkable": True,
    },
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
    "required_check_results": [
        "repo_identity_resolved",
        "suite_resolved",
        "checks_executed",
        "overall_status_computed",
        "evidence_refs_bound",
    ],
    "expected_output_artifact": "repo_check_result_bundle",
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "command_id": "repo-check",
    "binding_mode": "machine_parseable",
    "target_scope": "repo_or_worktree",
    "target_kind": "workspace_root",
    "target_path": "/repo/AAA_WORKSPACE",
    "allowed_authority": [
        "analysis_only",
    ],
    "tool_contract_ref": "internal/development/contracts/ops/tool-contract.v0.1.md",
    "command_contract_ref": "internal/development/contracts/ops/command-registry-contract.v0.1.md",
    "identity_contract_ref": "internal/development/contracts/ops/multi-repo-worktree-identity-guard.v0.1.schema.json",
    "context_contract_ref": "internal/development/contracts/ops/context-assembly-contract.v0.1.md",
    "readiness_contract_ref": "internal/development/contracts/ops/session-readiness-state.v0.1.schema.json",
    "result_shape_contract": {
        "result_kind": "repo_check_result_bundle",
        "required_fields": [
            "repo_id",
            "suite_id",
            "check_results",
        ],
        "machine_checkable": True,
    },
    "readiness_consumer_relation": {
        "relation_mode": "consumable_by_readiness_surface",
        "consumer_surface": "readiness_panel",
        "machine_checkable": False,
    },
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
    "required_check_results": [
        "repo_identity_resolved",
    ],
    "expected_output_artifact": "repo_check_result_bundle",
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_repo_check_runtime_adoption_bundle():
    result = repo_check_runtime_adoption.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_command_id"] == "repo-check"
    assert result["derived_results"]["multi_repo_worktree_identity"]["valid"] is True
    assert result["derived_results"]["context_runtime_preflight"]["valid"] is True


def test_validate_bundle_rejects_workspace_target_truth_contamination_and_prose_fallback():
    result = repo_check_runtime_adoption.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "target_kind" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]
    assert "current_truth_sources" in result["error_codes"]
    assert "required_check_results" in result["error_codes"]


def test_cli_repo_check_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "repo-check", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_repo_check_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "repo-check", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "target_kind" in payload["error_codes"]
