import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import permission_and_authorization_runtime_gate
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "permission_gate",
    "line_class": "mandatory_core_absorption_line",
    "permission_context_ref": "internal/development/contracts/ops/tool-contract.v0.1.md",
    "command_id": "readiness-inspect",
    "allowed_authority": ["read_only", "analysis_only"],
    "decision_mode": "allow",
    "interactive_mode": "prompt_not_required",
    "non_interactive_mode": "preauthorized_only",
    "primary_law_creation_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "permission_gate",
    "line_class": "mandatory_core_absorption_line",
    "permission_context_ref": "internal/development/contracts/ops/tool-contract.v0.1.md",
    "command_id": "repo-check",
    "allowed_authority": ["governance_gate"],
    "decision_mode": "allow",
    "interactive_mode": "prompt_allowed",
    "non_interactive_mode": "auto_deny",
    "primary_law_creation_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_permission_gate_bundle():
    result = permission_and_authorization_runtime_gate.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "permission_gate"


def test_validate_bundle_rejects_authority_and_non_interactive_conflicts():
    result = permission_and_authorization_runtime_gate.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "authority_decision_conflict" in result["error_codes"]
    assert "non_interactive_prompt_conflict" in result["error_codes"]
    assert "primary_law_creation_allowed" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_permission_gate_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "permission-gate", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_permission_gate_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "permission-gate", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "authority_decision_conflict" in payload["error_codes"]
