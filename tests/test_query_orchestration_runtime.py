import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import query_orchestration_runtime
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "orchestration_runtime_id": "query_orchestration",
    "runtime_plane_mode": "orchestration_loop",
    "dispatch_runtime_ref": "internal/development/contracts/ops/shared-command-dispatch-runtime-bundle.v0.1.schema.json",
    "result_gate_ref": "internal/development/contracts/ops/result-artifact-eligibility-and-evidence-promotion-gate.v0.1.schema.json",
    "snapshot_runtime_ref": "internal/development/contracts/ops/session-context-snapshot-runtime-bundle.v0.1.schema.json",
    "supported_command_ids": [
        "readiness-inspect",
        "repo-check",
    ],
    "turn_lifecycle": [
        "request_received",
        "snapshot_loaded",
        "dispatch_resolved",
        "execution_completed",
        "evidence_gate_applied",
        "readiness_evaluated",
    ],
    "write_back_destination_classes": [
        "runtime_artifact_only",
        "evidence_candidate_only",
        "promotion_gated_only",
        "forbidden_canonical_writeback",
    ],
    "promotion_gate_bypass_allowed": False,
    "snapshot_boundary_bypass_allowed": False,
    "primary_law_creation_allowed": False,
    "family_expansion_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "orchestration_runtime_id": "query_orchestration",
    "runtime_plane_mode": "orchestration_loop",
    "dispatch_runtime_ref": "internal/development/contracts/ops/shared-command-dispatch-runtime-bundle.v0.1.schema.json",
    "result_gate_ref": "internal/development/contracts/ops/result-artifact-eligibility-and-evidence-promotion-gate.v0.1.schema.json",
    "snapshot_runtime_ref": "internal/development/contracts/ops/session-context-snapshot-runtime-bundle.v0.1.schema.json",
    "supported_command_ids": [
        "readiness-inspect",
        "orchestration-debug",
    ],
    "turn_lifecycle": [
        "request_received",
        "dispatch_resolved",
    ],
    "write_back_destination_classes": [
        "runtime_artifact_only",
        "evidence_candidate_only",
        "promotion_gated_only",
        "forbidden_canonical_writeback",
    ],
    "promotion_gate_bypass_allowed": True,
    "snapshot_boundary_bypass_allowed": True,
    "primary_law_creation_allowed": True,
    "family_expansion_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_minimal_orchestration_loop():
    result = query_orchestration_runtime.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_orchestration_runtime_id"] == "query_orchestration"


def test_validate_bundle_rejects_bypass_and_family_expansion():
    result = query_orchestration_runtime.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "supported_command_ids" in result["error_codes"]
    assert "turn_lifecycle" in result["error_codes"]
    assert "promotion_gate_bypass_allowed" in result["error_codes"]
    assert "snapshot_boundary_bypass_allowed" in result["error_codes"]
    assert "primary_law_creation_allowed" in result["error_codes"]
    assert "family_expansion_allowed" in result["error_codes"]


def test_cli_query_orchestration_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "query-orchestration", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_query_orchestration_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "query-orchestration", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "promotion_gate_bypass_allowed" in payload["error_codes"]
