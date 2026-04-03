import json
from pathlib import Path

from typer.testing import CliRunner

from aaa.cli import app
from aaa import multi_repo_worktree_identity


PASS_BUNDLE = {
    "version": "v0.1",
    "canonical_repo_root": "/repo/aaa-tpl-docs",
    "worktree_instances": ["/repo/aaa-tpl-docs/.worktrees/v2-1-2"],
    "validator_rules": [
        "require_canonical_repo_root",
        "reject_workspace_root_as_repo_target",
    ],
    "runtime_guards": [
        "canonical_root_guard",
        "worktree_target_guard",
    ],
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "canonical_repo_root": "",
    "worktree_instances": ["/repo/aaa-workspace"],
    "validator_rules": [
        "reject_unknown_worktree_target",
    ],
    "runtime_guards": [
        "target_scope_guard",
    ],
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_canonical_root_and_worktree_instance():
    result = multi_repo_worktree_identity.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_validator_rules"] == PASS_BUNDLE["validator_rules"]
    assert result["resolved_runtime_guards"] == PASS_BUNDLE["runtime_guards"]


def test_validate_bundle_rejects_missing_root_and_unknown_worktree_target():
    result = multi_repo_worktree_identity.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "canonical_repo_root" in result["error_codes"]
    assert "worktree_instances" in result["error_codes"]


def test_cli_validate_multi_repo_worktree_identity_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "validate-multi-repo-worktree-identity", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_validate_multi_repo_worktree_identity_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "validate-multi-repo-worktree-identity", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "canonical_repo_root" in payload["error_codes"]
