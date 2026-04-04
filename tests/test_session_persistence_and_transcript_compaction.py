import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import session_persistence_and_transcript_compaction
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "session_persistence",
    "line_class": "mandatory_core_absorption_line",
    "session_store_mode": "persistent_store",
    "transcript_class": "raw_transcript",
    "compaction_mode": "lossless_boundary",
    "replay_input_eligibility": "disallowed",
    "canonical_truth_promotion_allowed": False,
    "audit_reproducibility_required": True,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "session_persistence",
    "line_class": "mandatory_core_absorption_line",
    "session_store_mode": "persistent_store",
    "transcript_class": "compacted_transcript",
    "compaction_mode": "summarized_boundary",
    "replay_input_eligibility": "allowed",
    "canonical_truth_promotion_allowed": True,
    "audit_reproducibility_required": False,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_session_persistence_boundary():
    result = session_persistence_and_transcript_compaction.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "session_persistence"


def test_validate_bundle_rejects_truth_promotion_and_audit_break():
    result = session_persistence_and_transcript_compaction.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "canonical_truth_promotion_allowed" in result["error_codes"]
    assert "audit_reproducibility_required" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_session_persistence_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "session-persistence", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_session_persistence_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "session-persistence", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "canonical_truth_promotion_allowed" in payload["error_codes"]
