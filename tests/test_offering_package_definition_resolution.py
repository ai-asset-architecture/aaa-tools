from pathlib import Path

from aaa import offering_package_definition_resolution as runtime


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "offering_package_definition_resolution",
    "line_class": "offering_package_runtime_enablement_line",
    "baseline_scope": "pre_topology_baseline",
    "post_topology_consumption_required": True,
    "topology_resolution_precedence_ref": "v2.1.32",
    "package_level": "core",
    "source_definition_artifact": "aaa-docs/bootstrap/offering_definition_skeleton.md",
    "source_definition_artifact_ref": "aaa-docs/bootstrap/offering_definition_skeleton.md",
    "minimum_repo_set": [
        "aaa-actions",
        "aaa-evals",
        "aaa-tools",
        "aaa-prompts",
        "aaa-tpl-docs",
        "aaa-tpl-service",
        "aaa-tpl-frontend",
    ],
    "workflow_inclusion_level": "core",
    "client_prerequisites": [
        "ci_discipline",
        "contract_first",
        "mock_first",
        "review_evidence_discipline",
    ],
    "back_write_allowed": False,
    "reinterpretation_allowed": False,
    "dedicated_github_universal_invariant": False,
    "prose_fallback_allowed": False,
}


def test_validate_bundle_passes_for_pre_topology_resolution():
    result = runtime.validate_bundle(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "offering_package_definition_resolution"
    assert result["derived_results"]["package_level"] == "core"
    assert result["derived_results"]["topology_resolution_precedence_ref"] == "v2.1.32"


def test_requires_post_topology_consumption():
    bundle = dict(PASS_BUNDLE)
    bundle["post_topology_consumption_required"] = False

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "post_topology_consumption_required" in result["error_codes"]


def test_rejects_noncanonical_source_definition_ref():
    bundle = dict(PASS_BUNDLE)
    bundle["source_definition_artifact_ref"] = "bootstrap/offering_definition_skeleton.md"

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "source_definition_artifact_ref" in result["error_codes"]


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
        "2026-04-04-v2.1.24-offering-package-definition-resolution.pass.json"
    )

    result = runtime.validate_bundle_file(bundle_path)

    assert result["valid"] is True
    assert result["bundle_path"].endswith(
        "2026-04-04-v2.1.24-offering-package-definition-resolution.pass.json"
    )
