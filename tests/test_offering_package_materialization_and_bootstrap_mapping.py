from pathlib import Path

from aaa import offering_package_materialization_and_bootstrap_mapping as runtime


def _resolve_fixture(relative_path: str) -> Path:
    test_file = Path(__file__).resolve()
    candidates = [
        test_file.parents[1] / relative_path,
        test_file.parents[2] / relative_path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


PASS_BUNDLE = _resolve_fixture(
    "aaa-tpl-docs/internal/development/contracts/ops/examples/pass/2026-04-04-v2.1.26-offering-package-materialization-and-bootstrap-mapping.pass.json"
)
FAIL_BUNDLE = _resolve_fixture(
    "aaa-tpl-docs/internal/development/contracts/ops/examples/fail/2026-04-04-v2.1.26-offering-package-materialization-and-bootstrap-mapping.fail.json"
)


def test_validate_bundle_accepts_canonical_materialization_mapping_bundle() -> None:
    result = runtime.validate_bundle_file(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["status"] == "ok"
    assert result["resolved_runtime_plane_mode"] == "offering_package_materialization_mapping"
    assert result["derived_results"]["package_level"] == "lite"
    assert result["derived_results"]["topology_mapping_precedence_ref"] == "v2.1.34"


def test_validate_bundle_rejects_mapping_that_implies_status() -> None:
    result = runtime.validate_bundle_file(FAIL_BUNDLE)

    assert result["valid"] is False
    assert result["status"] == "error"
    assert "post_topology_consumption_required" in result["error_codes"]
    assert "mapping_completeness" in result["error_codes"]
    assert "dedicated_github_universal_invariant" in result["error_codes"]
    assert "package_status_assertion_included" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_validate_bundle_rejects_unsupported_governance_assets() -> None:
    payload = runtime.load_bundle(PASS_BUNDLE)
    payload["governance_asset_load_list"] = ["ai_command_center", "unknown_asset"]

    result = runtime.validate_bundle(payload)

    assert result["valid"] is False
    assert "governance_asset_load_list" in result["error_codes"]


def test_validate_bundle_preserves_materialization_shape() -> None:
    result = runtime.validate_bundle_file(PASS_BUNDLE)

    assert result["derived_results"]["materialization_target_mode"] == "repo_template_workflow_asset_mapping"
    assert result["derived_results"]["template_sync_required"] is True
    assert result["derived_results"]["workflow_enablement_required"] is True
