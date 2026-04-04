from pathlib import Path

from aaa import topology_aware_materialization_and_bootstrap_mapping as runtime


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "topology_aware_materialization_and_bootstrap_mapping",
    "line_class": "github_governance_topology_support_program",
    "topology_mode": "hybrid",
    "materialization_mapping_by_topology": ["hybrid_split"],
    "workflow_target_scope": "split",
    "codeowners_target_scope": "repo_local",
    "mapping_completeness": "complete",
    "materialization_scope_implies_governance_authority": False,
    "package_active_asserted": False,
    "prose_fallback_allowed": False,
}


def test_validate_bundle_passes_for_hybrid_mapping():
    result = runtime.validate_bundle(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["derived_results"]["topology_mode"] == "hybrid"


def test_materialization_scope_may_not_imply_authority():
    bundle = dict(PASS_BUNDLE)
    bundle["materialization_scope_implies_governance_authority"] = True

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "materialization_scope_implies_governance_authority" in result["error_codes"]


def test_repo_local_rejects_org_repo_only_targets():
    bundle = dict(PASS_BUNDLE)
    bundle["topology_mode"] = "repo_local"
    bundle["materialization_mapping_by_topology"] = ["repo_local_only"]
    bundle["workflow_target_scope"] = "org_repo"

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "workflow_target_scope" in result["error_codes"]


def _resolve_tpl_docs_example(example_name: str) -> Path:
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
            / "pass"
            / example_name
        )
        if candidate.exists():
            return candidate
    return candidates[0] / "internal" / "development" / "contracts" / "ops" / "examples" / "pass" / example_name


def test_validate_bundle_file_uses_canonical_fixture():
    bundle_path = _resolve_tpl_docs_example(
        "2026-04-04-v2.1.34-topology-aware-materialization-and-bootstrap-mapping.pass.json"
    )

    result = runtime.validate_bundle_file(bundle_path)

    assert result["valid"] is True
    assert result["bundle_path"].endswith(
        "2026-04-04-v2.1.34-topology-aware-materialization-and-bootstrap-mapping.pass.json"
    )
