from pathlib import Path

from aaa import topology_aware_prerequisite_gate as runtime


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "topology_aware_prerequisite_gate",
    "line_class": "github_governance_topology_support_program",
    "topology_expected": "hybrid",
    "topology_detected": "hybrid",
    "topology_compliance_verdict": "pass",
    "evidence_sufficiency_verdict": "sufficient",
    "gate_verdict_is_activation": False,
    "prose_fallback_allowed": False,
}


def test_validate_bundle_passes_for_matching_topology_gate():
    result = runtime.validate_bundle(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["derived_results"]["topology_mismatch"] is False


def test_topology_mismatch_may_not_claim_pass():
    bundle = dict(PASS_BUNDLE)
    bundle["topology_expected"] = "repo_local"
    bundle["topology_detected"] = "dedicated_repo"

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "topology_compliance_verdict" in result["error_codes"]


def test_gate_verdict_may_not_be_activation():
    bundle = dict(PASS_BUNDLE)
    bundle["gate_verdict_is_activation"] = True

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "gate_verdict_is_activation" in result["error_codes"]


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
        "2026-04-04-v2.1.33-topology-aware-prerequisite-gate.pass.json"
    )

    result = runtime.validate_bundle_file(bundle_path)

    assert result["valid"] is True
    assert result["bundle_path"].endswith(
        "2026-04-04-v2.1.33-topology-aware-prerequisite-gate.pass.json"
    )
