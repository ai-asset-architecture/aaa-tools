import json
from pathlib import Path

from typer.testing import CliRunner

from aaa.cli import app
from aaa import session_readiness_state


PASS_BUNDLE = {
    "version": "v0.1",
    "orchestration_mode": "operator_review_session",
    "query_state_store": "readiness_snapshot",
    "readiness_surface": "readiness_panel",
    "readiness_checks": [
        "context_loaded",
        "authority_resolved",
        "preflight_passed",
        "evidence_path_bound",
    ],
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "orchestration_mode": "interactive_session",
    "query_state_store": "session_memory",
    "readiness_surface": "invalid_surface",
    "readiness_checks": [
        "context_loaded",
    ],
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_readiness_panel_with_snapshot_store():
    result = session_readiness_state.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_readiness_surface"] == PASS_BUNDLE["readiness_surface"]
    assert result["resolved_query_state_store"] == PASS_BUNDLE["query_state_store"]


def test_validate_bundle_rejects_invalid_surface_and_missing_checks():
    result = session_readiness_state.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "readiness_surface" in result["error_codes"]
    assert "readiness_checks" in result["error_codes"]


def test_cli_validate_session_readiness_state_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "validate-session-readiness-state", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_validate_session_readiness_state_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "validate-session-readiness-state", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "readiness_surface" in payload["error_codes"]
