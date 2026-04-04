from pathlib import Path

from aaa import topology_aware_offering_package_definition_resolution as runtime


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "topology_aware_offering_package_definition_resolution",
    "line_class": "github_governance_topology_support_program",
    "package_level": "core",
    "topology_mode": "repo_local",
    "source_definition_artifact_ref": "aaa-docs/bootstrap/offering_definition_skeleton.md",
    "minimum_repo_set_by_topology": [
        "aaa-actions",
        "aaa-evals",
        "aaa-tools",
        "aaa-prompts",
        "aaa-tpl-docs",
        "aaa-tpl-service",
        "aaa-tpl-frontend",
    ],
    "workflow_inclusion_level_by_topology": "core",
    "governance_asset_placement_rules": ["repo_local_only"],
    "back_write_allowed": False,
    "reinterpretation_allowed": False,
    "prose_fallback_allowed": False,
}


def test_validate_bundle_passes_for_repo_local_resolution():
    result = runtime.validate_bundle(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "topology_aware_offering_package_definition_resolution"
    assert result["derived_results"]["package_level"] == "core"
    assert result["derived_results"]["topology_mode"] == "repo_local"


def test_repo_local_rejects_dedicated_dot_github_requirement():
    bundle = dict(PASS_BUNDLE)
    bundle["minimum_repo_set_by_topology"] = [".github", "aaa-actions"]

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "minimum_repo_set_by_topology" in result["error_codes"]


def test_mother_draft_reference_is_required():
    bundle = dict(PASS_BUNDLE)
    bundle["source_definition_artifact_ref"] = "README.md"

    result = runtime.validate_bundle(bundle)

    assert result["valid"] is False
    assert "source_definition_artifact_ref" in result["error_codes"]


def test_validate_bundle_file_uses_canonical_fixture():
    bundle_path = (
        Path(__file__).resolve().parents[2]
        / "aaa-tpl-docs"
        / "internal"
        / "development"
        / "contracts"
        / "ops"
        / "examples"
        / "pass"
        / "2026-04-04-v2.1.32-topology-aware-offering-package-definition-resolution.pass.json"
    )

    result = runtime.validate_bundle_file(bundle_path)

    assert result["valid"] is True
    assert result["bundle_path"].endswith(
        "2026-04-04-v2.1.32-topology-aware-offering-package-definition-resolution.pass.json"
    )
