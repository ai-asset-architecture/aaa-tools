import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import topology_aware_init_plan_validation
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "topology_aware_init_plan_validation",
    "line_class": "github_governance_topology_support_program",
    "topology_mode": "repo_local",
    "validation_scope": "declared_planned_structure_compatibility",
    "required_structure_by_topology": ["repo_local_dot_github"],
    "github_repo_existence_required": False,
    "dual_side_evidence_required": False,
    "runtime_detected_topology_verdict_emitted": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "topology_aware_init_plan_validation",
    "line_class": "github_governance_topology_support_program",
    "topology_mode": "repo_local",
    "validation_scope": "declared_planned_structure_compatibility",
    "required_structure_by_topology": ["repo_local_dot_github"],
    "github_repo_existence_required": True,
    "dual_side_evidence_required": False,
    "runtime_detected_topology_verdict_emitted": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_declared_structure_compatibility():
    result = topology_aware_init_plan_validation.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "topology_aware_init_plan_validation"


def test_validate_bundle_rejects_runtime_detection_verdict_emission():
    result = topology_aware_init_plan_validation.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "runtime_detected_topology_verdict_emitted" in result["error_codes"]
    assert "github_repo_existence_required" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_topology_aware_init_plan_validation_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "topology-aware-init-plan-validation", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_topology_aware_init_plan_validation_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "topology-aware-init-plan-validation", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "runtime_detected_topology_verdict_emitted" in payload["error_codes"]
