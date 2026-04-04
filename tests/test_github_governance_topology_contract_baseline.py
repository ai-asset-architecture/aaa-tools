import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import github_governance_topology_contract_baseline
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "github_governance_topology_contract_baseline",
    "line_class": "github_governance_topology_support_program",
    "topology_mode": "hybrid",
    "authority_split": "mixed_authority",
    "asset_class_authority_model": [
        {
            "asset_class": "org_profile_metadata",
            "allowed_topology_modes": ["dedicated_repo", "hybrid"],
            "authority_owner": "org_centralized",
            "placement_mode": "org_repo_only",
            "precedence_rule": "org_precedence",
            "conflict_rule": "hard_fail",
            "evidence_requirements": ["org_repo_presence", "profile_metadata_ref"],
        },
        {
            "asset_class": "repo_local_workflows",
            "allowed_topology_modes": ["dedicated_repo", "repo_local", "hybrid"],
            "authority_owner": "repo_distributed",
            "placement_mode": "repo_local_only",
            "precedence_rule": "repo_precedence",
            "conflict_rule": "degraded",
            "evidence_requirements": ["repo_workflows_presence"],
        },
        {
            "asset_class": "codeowners",
            "allowed_topology_modes": ["dedicated_repo", "repo_local", "hybrid"],
            "authority_owner": "repo_distributed",
            "placement_mode": "repo_local_only",
            "precedence_rule": "single_source_only",
            "conflict_rule": "hard_fail",
            "evidence_requirements": ["codeowners_path"],
        },
    ],
    "precedence_law": "machine_checkable_precedence_required",
    "conflict_law": "machine_checkable_conflict_verdict_required",
    "evidence_sufficiency_law": "machine_checkable_evidence_sufficiency_required",
    "dedicated_repo_existence_is_only_truth": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "github_governance_topology_contract_baseline",
    "line_class": "github_governance_topology_support_program",
    "topology_mode": "hybrid",
    "authority_split": "mixed_authority",
    "asset_class_authority_model": [],
    "precedence_law": "machine_checkable_precedence_required",
    "conflict_law": "machine_checkable_conflict_verdict_required",
    "evidence_sufficiency_law": "machine_checkable_evidence_sufficiency_required",
    "dedicated_repo_existence_is_only_truth": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_hybrid_asset_authority_model():
    result = github_governance_topology_contract_baseline.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "github_governance_topology_contract_baseline"
    assert result["derived_results"]["asset_class_count"] == 3


def test_validate_bundle_rejects_dedicated_only_truth_fallback():
    result = github_governance_topology_contract_baseline.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "asset_class_authority_model" in result["error_codes"]
    assert "dedicated_repo_existence_is_only_truth" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_github_governance_topology_contract_baseline_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "github-governance-topology-contract-baseline", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_github_governance_topology_contract_baseline_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "github-governance-topology-contract-baseline", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "dedicated_repo_existence_is_only_truth" in payload["error_codes"]
