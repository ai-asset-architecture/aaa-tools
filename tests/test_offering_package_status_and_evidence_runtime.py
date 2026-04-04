from pathlib import Path

from aaa import offering_package_status_and_evidence_runtime as runtime


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
    "aaa-tpl-docs/internal/development/contracts/ops/examples/pass/2026-04-04-v2.1.27-offering-package-status-and-evidence-runtime.pass.json"
)
FAIL_BUNDLE = _resolve_fixture(
    "aaa-tpl-docs/internal/development/contracts/ops/examples/fail/2026-04-04-v2.1.27-offering-package-status-and-evidence-runtime.fail.json"
)


def test_validate_bundle_accepts_canonical_status_bundle() -> None:
    result = runtime.validate_bundle_file(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["status"] == "ok"
    assert result["resolved_runtime_plane_mode"] == "offering_package_status_evidence"
    assert result["derived_results"]["package_stage"] == "materialized"
    assert result["derived_results"]["topology_status_precedence_ref"] == "v2.1.35"


def test_validate_bundle_rejects_collapsed_status_axis_and_narrative_fallback() -> None:
    result = runtime.validate_bundle_file(FAIL_BUNDLE)

    assert result["valid"] is False
    assert result["status"] == "error"
    assert "post_topology_consumption_required" in result["error_codes"]
    assert "topology_status_precedence_ref" in result["error_codes"]
    assert "package_stage" in result["error_codes"]
    assert "package_compliance_status" in result["error_codes"]
    assert "runtime_activity_requires_minimum_evidence_refs" in result["error_codes"]
    assert "prerequisite_verdict_used_as_activation" in result["error_codes"]
    assert "narrative_only_status_allowed" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_validate_bundle_rejects_active_runtime_without_evidence() -> None:
    payload = runtime.load_bundle(PASS_BUNDLE)
    payload["package_runtime_activity"] = "active"
    payload["evidence_refs"] = []

    result = runtime.validate_bundle(payload)

    assert result["valid"] is False
    assert "evidence_refs" in result["error_codes"]


def test_validate_bundle_preserves_status_layers() -> None:
    result = runtime.validate_bundle_file(PASS_BUNDLE)

    assert result["derived_results"]["package_stage"] == "materialized"
    assert result["derived_results"]["package_compliance_status"] == "compliant_with_gap"
    assert result["derived_results"]["package_runtime_activity"] == "inactive"
    assert result["derived_results"]["evidence_ref_count"] == 1
