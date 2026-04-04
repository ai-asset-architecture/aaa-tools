import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import workflow_and_runbook_orchestration_runtime
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "workflow_runtime",
    "line_class": "mandatory_core_absorption_line",
    "workflow_id": "governance-closeout",
    "step_id": "step2-run",
    "dependency_mode": "strict_prerequisite",
    "handoff_artifact_class": "result_artifact",
    "step_outcome": "passed",
    "workflow_gate_mode": "fail_closed",
    "workflow_gate_decision": "gate_passed",
    "bpm_platform_expansion_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "workflow_runtime",
    "line_class": "mandatory_core_absorption_line",
    "workflow_id": "governance-closeout",
    "step_id": "step3-closeout",
    "dependency_mode": "independent_step",
    "handoff_artifact_class": "readiness_snapshot",
    "step_outcome": "passed",
    "workflow_gate_mode": "explicit_continue",
    "workflow_gate_decision": "gate_failed",
    "bpm_platform_expansion_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_governed_workflow_runtime():
    result = workflow_and_runbook_orchestration_runtime.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "workflow_runtime"


def test_validate_bundle_rejects_gate_substitution_and_ungoverned_handoff():
    result = workflow_and_runbook_orchestration_runtime.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "workflow_gate_decision" in result["error_codes"]
    assert "handoff_artifact_class" in result["error_codes"]
    assert "bpm_platform_expansion_allowed" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_workflow_runtime_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "workflow-runtime", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_workflow_runtime_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "workflow-runtime", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "workflow_gate_decision" in payload["error_codes"]
