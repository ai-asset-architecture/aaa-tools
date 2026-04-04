from pathlib import Path

from aaa import topology_aware_package_status_and_repo_checks as runtime


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "topology_aware_package_status_and_repo_checks",
    "line_class": "github_governance_topology_support_program",
    "topology_mode_expected": "repo_local",
    "topology_mode_detected": "repo_local",
    "topology_mode_resolved": "repo_local",
    "topology_compliance_status": "compliant",
    "missing_governance_assets": [],
    "misplaced_governance_assets": [],
    "narrative_only_compliance_allowed": False,
    "prose_fallback_allowed": False,
}


def test_validate_bundle_passes_for_repo_local_compliance():
    result = runtime.validate_bundle(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["derived_results"]["topology_mode_resolved"] == "repo_local"


def test_repo_local_may_not_report_missing_dot_github_repo():
    bundle = dict(PASS_BUNDLE)
    bundle["missing_governance_assets"] = [".github repo"]

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "missing_governance_assets" in result["error_codes"]


def test_resolved_mode_may_not_conflict_with_compliant_status():
    bundle = dict(PASS_BUNDLE)
    bundle["topology_mode_resolved"] = "degraded"

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "topology_mode_resolved" in result["error_codes"]


def _resolve_tpl_docs_example(example_name: str, variant: str) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    workspace_root = repo_root.parent
    candidates = [
        repo_root / "aaa-tpl-docs",
        workspace_root / "aaa-tpl-docs",
    ]
    for candidate_root in candidates:
        candidate = (
            candidate_root
            / "internal"
            / "development"
            / "contracts"
            / "ops"
            / "examples"
            / variant
            / example_name
        )
        if candidate.exists():
            return candidate
    return (
        candidates[0]
        / "internal"
        / "development"
        / "contracts"
        / "ops"
        / "examples"
        / variant
        / example_name
    )


def test_validate_bundle_file_uses_canonical_fixture():
    bundle_path = _resolve_tpl_docs_example(
        "2026-04-04-v2.1.35-topology-aware-package-status-and-repo-checks.pass.json",
        "pass",
    )

    result = runtime.validate_bundle_file(bundle_path)

    assert result["valid"] is True
    assert result["bundle_path"].endswith(
        "2026-04-04-v2.1.35-topology-aware-package-status-and-repo-checks.pass.json"
    )
