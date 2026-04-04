import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import structured_output_and_result_normalization_plane
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "result_normalization",
    "line_class": "mandatory_core_absorption_line",
    "output_class": "machine_safe",
    "status": "ok",
    "errors": [],
    "warnings": [],
    "artifact_refs": ["result.json"],
    "artifact_refs_role": "supporting_artifact",
    "normalized_payload_class": "structured_result",
    "normalized_payload_precedence": "normalized_payload_primary",
    "prose_only_result_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "result_normalization",
    "line_class": "mandatory_core_absorption_line",
    "output_class": "human_safe",
    "status": "ok",
    "errors": [],
    "warnings": [],
    "artifact_refs": ["path-specific-result.json"],
    "artifact_refs_role": "path_specific_artifact",
    "normalized_payload_class": "structured_result",
    "normalized_payload_precedence": "artifact_ref_primary",
    "prose_only_result_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_normalized_result_envelope():
    result = structured_output_and_result_normalization_plane.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "result_normalization"


def test_validate_bundle_rejects_prose_only_and_artifact_precedence_grab():
    result = structured_output_and_result_normalization_plane.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "normalized_payload_precedence" in result["error_codes"]
    assert "prose_only_result_allowed" in result["error_codes"]


def test_cli_result_normalization_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "result-normalization", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_result_normalization_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "result-normalization", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "normalized_payload_precedence" in payload["error_codes"]
