import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import agent_delegation_and_task_lifecycle_runtime
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "delegation_lifecycle",
    "line_class": "mandatory_core_absorption_line",
    "task_id": "task-001",
    "task_state": "completed",
    "ownership_scope": "bounded_write_scope",
    "handoff_evidence_class": "verification_record",
    "verification_required": True,
    "verification_closure_state": "verified",
    "handoff_completion_before_verification_allowed": False,
    "extension_loading_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "delegation_lifecycle",
    "line_class": "mandatory_core_absorption_line",
    "task_id": "task-002",
    "task_state": "completed",
    "ownership_scope": "bounded_write_scope",
    "handoff_evidence_class": "task_result",
    "verification_required": True,
    "verification_closure_state": "pending_verification",
    "handoff_completion_before_verification_allowed": False,
    "extension_loading_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_verified_handoff_closure():
    result = agent_delegation_and_task_lifecycle_runtime.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "delegation_lifecycle"


def test_validate_bundle_rejects_unverified_handoff_completion():
    result = agent_delegation_and_task_lifecycle_runtime.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "verification_closure_state" in result["error_codes"]
    assert "handoff_evidence_class" in result["error_codes"]
    assert "extension_loading_allowed" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_delegation_lifecycle_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "delegation-lifecycle", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_delegation_lifecycle_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "delegation-lifecycle", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "verification_closure_state" in payload["error_codes"]
