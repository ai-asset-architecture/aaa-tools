import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import result_artifact_eligibility_and_evidence_promotion_gate
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "promotion_gate_id": "result_artifact_evidence_promotion_gate",
    "runtime_plane_mode": "result_evidence_gate",
    "result_artifact_kind": "repo_check_report",
    "artifact_eligibility": "eligible",
    "evidence_class": "audit_evidence",
    "promotion_eligibility": "promotable",
    "promotion_decision_source": "machine_checkable_gate",
    "evidence_source": "promotion_gated_evidence_bundle",
    "supporting_review_sources": [
        "manual_review_note",
        "completion_report",
    ],
    "sole_manual_decision_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "promotion_gate_id": "result_artifact_evidence_promotion_gate",
    "runtime_plane_mode": "result_evidence_gate",
    "result_artifact_kind": "dispatch_result_envelope",
    "artifact_eligibility": "eligible",
    "evidence_class": "completion_evidence",
    "promotion_eligibility": "promotable",
    "promotion_decision_source": "completion_report",
    "evidence_source": "operator_narrative",
    "supporting_review_sources": [
        "operator_narrative",
    ],
    "sole_manual_decision_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_machine_checkable_promotion_gate():
    result = result_artifact_eligibility_and_evidence_promotion_gate.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_gate_id"] == "result_artifact_evidence_promotion_gate"
    assert result["derived_results"]["promotion_decision_source"] == "machine_checkable_gate"


def test_validate_bundle_rejects_manual_promotion_decision_and_eventual_artifact_confusion():
    result = result_artifact_eligibility_and_evidence_promotion_gate.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "promotion_decision_source" in result["error_codes"]
    assert "evidence_source" in result["error_codes"]
    assert "sole_manual_decision_allowed" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_result_evidence_promotion_gate_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "result-evidence-promotion-gate", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_result_evidence_promotion_gate_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "result-evidence-promotion-gate", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "promotion_decision_source" in payload["error_codes"]
