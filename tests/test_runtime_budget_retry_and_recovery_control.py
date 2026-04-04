import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import runtime_budget_retry_and_recovery_control
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "runtime_control",
    "line_class": "mandatory_core_absorption_line",
    "budget_scope": "per_turn",
    "failure_class": "retryable",
    "retry_mode": "limited_retry",
    "fallback_mode": "same_path_recovery",
    "fallback_retry_recursion_allowed": False,
    "stop_condition": "retry_limit_reached",
    "provider_business_layer_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "runtime_control",
    "line_class": "mandatory_core_absorption_line",
    "budget_scope": "per_session",
    "failure_class": "terminal",
    "retry_mode": "limited_retry",
    "fallback_mode": "fallback_path",
    "fallback_retry_recursion_allowed": True,
    "stop_condition": "budget_exhausted",
    "provider_business_layer_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_runtime_control_boundary():
    result = runtime_budget_retry_and_recovery_control.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "runtime_control"


def test_validate_bundle_rejects_recursive_fallback_and_provider_expansion():
    result = runtime_budget_retry_and_recovery_control.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "fallback_retry_recursion_allowed" in result["error_codes"]
    assert "provider_business_layer_allowed" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_runtime_control_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "runtime-control", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_runtime_control_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "runtime-control", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "fallback_retry_recursion_allowed" in payload["error_codes"]
