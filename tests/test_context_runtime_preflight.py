import json
from pathlib import Path

from typer.testing import CliRunner

from aaa.cli import app
from aaa import context_runtime_preflight


PASS_BUNDLE = {
    "version": "v0.1",
    "bundle_id": "context.bundle.ops.step2.preflight.v0.1",
    "current_truth_sources": [
        "canonical_contract_docs",
        "canonical_registries_indexes",
    ],
    "supporting_sources": [
        "external_execution_outputs",
        "local_operation_logs",
    ],
    "preflight_checks": [
        "current_truth_source_check",
        "supporting_source_check",
        "anti_contamination_check",
        "promotion_block_check",
    ],
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "bundle_id": "context.bundle.ops.step2.preflight.v0.1",
    "current_truth_sources": [
        "canonical_contract_docs",
        "local_operation_logs",
    ],
    "supporting_sources": [
        "generated_runtime_summaries",
    ],
    "preflight_checks": [
        "anti_contamination_check",
    ],
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_canonical_truth_with_local_logs_as_supporting_only():
    result = context_runtime_preflight.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_current_truth_sources"] == PASS_BUNDLE["current_truth_sources"]
    assert result["resolved_supporting_sources"] == PASS_BUNDLE["supporting_sources"]


def test_validate_bundle_rejects_local_logs_promoted_to_current_truth():
    result = context_runtime_preflight.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "current_truth_sources" in result["error_codes"]
    assert "preflight_checks" in result["error_codes"]


def test_cli_validate_context_runtime_preflight_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "validate-context-runtime-preflight", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_validate_context_runtime_preflight_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "validate-context-runtime-preflight", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "current_truth_sources" in payload["error_codes"]
