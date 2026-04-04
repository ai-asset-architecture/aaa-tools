import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import tool_progress_and_runtime_event_stream
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "event_stream",
    "line_class": "mandatory_core_absorption_line",
    "event_stream_id": "shared_runtime_event_stream",
    "signal_class": "progress_signal",
    "event_phase": "running",
    "evidence_source_role": "evidence_reference_source",
    "formal_evidence_artifact": False,
    "canonical_truth_promotion_allowed": False,
    "result_promotion_allowed": False,
    "evidence_promotion_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "event_stream",
    "line_class": "mandatory_core_absorption_line",
    "event_stream_id": "shared_runtime_event_stream",
    "signal_class": "progress_signal",
    "event_phase": "completed",
    "evidence_source_role": "evidence_generation_source",
    "formal_evidence_artifact": True,
    "canonical_truth_promotion_allowed": True,
    "result_promotion_allowed": True,
    "evidence_promotion_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_event_stream_boundary():
    result = tool_progress_and_runtime_event_stream.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "event_stream"


def test_validate_bundle_rejects_event_stream_as_formal_evidence():
    result = tool_progress_and_runtime_event_stream.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "formal_evidence_artifact" in result["error_codes"]
    assert "canonical_truth_promotion_allowed" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_event_stream_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "event-stream", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_event_stream_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "event-stream", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "formal_evidence_artifact" in payload["error_codes"]
