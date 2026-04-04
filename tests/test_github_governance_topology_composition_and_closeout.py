from pathlib import Path

from aaa import github_governance_topology_composition_and_closeout as runtime


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "github_governance_topology_composition_and_closeout",
    "line_class": "github_governance_topology_support_program",
    "closeout_role": "topology_support_closeout",
    "consumed_topology_stages": [
        "topology_contract_baseline",
        "topology_aware_init_validation",
        "topology_aware_definition_resolution",
        "topology_aware_prerequisite_gate",
        "topology_aware_materialization_mapping",
        "topology_aware_status_repo_checks",
    ],
    "consumed_stage_set_hash": "sha256:30a31b32c33d34ef",
    "semantics_rejudgment_allowed": False,
    "primary_semantics_backfill_allowed": False,
    "conditional_expansion_triggered": False,
    "prose_fallback_allowed": False,
}


def test_validate_bundle_passes_for_complete_topology_stage_set():
    result = runtime.validate_bundle(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["derived_results"]["consumed_stage_count"] == 6


def test_closeout_may_not_rejudge_or_backfill_primary_semantics():
    bundle = dict(PASS_BUNDLE)
    bundle["semantics_rejudgment_allowed"] = True
    bundle["primary_semantics_backfill_allowed"] = True

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "semantics_rejudgment_allowed" in result["error_codes"]
    assert "primary_semantics_backfill_allowed" in result["error_codes"]


def test_closeout_requires_full_consumed_stage_set():
    bundle = dict(PASS_BUNDLE)
    bundle["consumed_topology_stages"] = [
        "topology_contract_baseline",
        "topology_aware_status_repo_checks",
    ]

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "consumed_topology_stages" in result["error_codes"]


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
        "2026-04-04-v2.1.36-github-governance-topology-composition-and-closeout.pass.json",
        "pass",
    )

    result = runtime.validate_bundle_file(bundle_path)

    assert result["valid"] is True
    assert result["bundle_path"].endswith(
        "2026-04-04-v2.1.36-github-governance-topology-composition-and-closeout.pass.json"
    )
