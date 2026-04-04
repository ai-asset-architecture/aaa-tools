import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import shared_command_dispatch_runtime
from aaa.cli import app


DISPATCH_PASS_BUNDLE = {
    "version": "v0.1",
    "dispatch_runtime_id": "shared_command_dispatch",
    "runtime_plane_mode": "command_dispatch",
    "consumed_command_registry_ref": "internal/development/contracts/ops/command-registry-contract.v0.1.md",
    "command_id": "repo-check",
    "dispatch_entry_ref": "governance.repo-check",
    "target_resolution_ref": "governance.validate-multi-repo-worktree-identity",
    "context_preflight_ref": "governance.validate-context-runtime-preflight",
    "common_output_envelope": [
        "status",
        "valid",
        "errors",
        "result_artifact",
    ],
    "exit_semantics": "fail_closed",
    "primary_command_law_mode": "referenced_only",
    "family_expansion_allowed": False,
    "prose_fallback_allowed": False,
}

REPO_CHECK_PASS_BUNDLE = {
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


DISPATCH_FAIL_BUNDLE = {
    "version": "v0.1",
    "dispatch_runtime_id": "shared_command_dispatch",
    "runtime_plane_mode": "command_dispatch",
    "consumed_command_registry_ref": "internal/development/contracts/ops/command-registry-contract.v0.1.md",
    "command_id": "orchestration-debug",
    "dispatch_entry_ref": "governance.repo-check",
    "target_resolution_ref": "governance.validate-multi-repo-worktree-identity",
    "context_preflight_ref": "governance.validate-context-runtime-preflight",
    "common_output_envelope": [
        "status",
        "valid",
        "errors",
        "result_artifact",
    ],
    "exit_semantics": "fail_open",
    "primary_command_law_mode": "rewritten_locally",
    "family_expansion_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_dispatch_bundle_routes_repo_check_through_shared_dispatch_runtime():
    result = shared_command_dispatch_runtime.dispatch_bundle(
        DISPATCH_PASS_BUNDLE,
        REPO_CHECK_PASS_BUNDLE,
    )

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["result_artifact"]["command_id"] == "repo-check"
    assert result["result_artifact"]["dispatch_entry_ref"] == "governance.repo-check"
    assert result["result_artifact"]["command_result"]["valid"] is True


def test_dispatch_bundle_rejects_unregistered_command_family_expansion_and_fail_open():
    result = shared_command_dispatch_runtime.dispatch_bundle(
        DISPATCH_FAIL_BUNDLE,
        REPO_CHECK_PASS_BUNDLE,
    )

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "command_id" in result["error_codes"]
    assert "family_expansion_allowed" in result["error_codes"]
    assert "exit_semantics" in result["error_codes"]


def test_cli_shared_command_dispatch_json_success(tmp_path: Path):
    dispatch_bundle = tmp_path / "dispatch.pass.json"
    command_bundle = tmp_path / "repo-check.pass.json"
    _write_json(dispatch_bundle, DISPATCH_PASS_BUNDLE)
    _write_json(command_bundle, REPO_CHECK_PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "governance",
            "shared-command-dispatch",
            "--dispatch-bundle",
            str(dispatch_bundle),
            "--command-bundle",
            str(command_bundle),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_shared_command_dispatch_json_failure(tmp_path: Path):
    dispatch_bundle = tmp_path / "dispatch.fail.json"
    command_bundle = tmp_path / "repo-check.pass.json"
    _write_json(dispatch_bundle, DISPATCH_FAIL_BUNDLE)
    _write_json(command_bundle, REPO_CHECK_PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "governance",
            "shared-command-dispatch",
            "--dispatch-bundle",
            str(dispatch_bundle),
            "--command-bundle",
            str(command_bundle),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "command_id" in payload["error_codes"]
