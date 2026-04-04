from pathlib import Path

from aaa import offering_package_prerequisite_gate


PASS_BUNDLE = (
    Path(__file__).resolve().parents[2]
    / "aaa-tpl-docs/internal/development/contracts/ops/examples/pass/2026-04-04-v2.1.25-offering-package-prerequisite-gate.pass.json"
)
FAIL_BUNDLE = (
    Path(__file__).resolve().parents[2]
    / "aaa-tpl-docs/internal/development/contracts/ops/examples/fail/2026-04-04-v2.1.25-offering-package-prerequisite-gate.fail.json"
)


def test_validate_bundle_accepts_canonical_prerequisite_gate_bundle() -> None:
    result = offering_package_prerequisite_gate.validate_bundle_file(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["status"] == "ok"
    assert result["resolved_runtime_plane_mode"] == "offering_package_prerequisite_gate"
    assert result["derived_results"]["package_level"] == "lite"
    assert result["derived_results"]["prerequisite_verdict"] == "pass_with_gap"


def test_validate_bundle_rejects_gate_verdict_that_implies_activation() -> None:
    result = offering_package_prerequisite_gate.validate_bundle_file(FAIL_BUNDLE)

    assert result["valid"] is False
    assert result["status"] == "error"
    assert "activation_implied" in result["error_codes"]
    assert "readiness_implied" in result["error_codes"]
    assert "completion_implied" in result["error_codes"]
    assert "post_topology_consumption_required" in result["error_codes"]


def test_validate_bundle_rejects_invalid_prerequisite_identifiers() -> None:
    payload = offering_package_prerequisite_gate.load_bundle(PASS_BUNDLE)
    payload["checked_prerequisites"] = ["basic_ci", "made_up_requirement"]

    result = offering_package_prerequisite_gate.validate_bundle(payload)

    assert result["valid"] is False
    assert "checked_prerequisites" in result["error_codes"]


def test_validate_bundle_preserves_gate_scope_and_topology_precedence_ref() -> None:
    result = offering_package_prerequisite_gate.validate_bundle_file(PASS_BUNDLE)

    assert result["derived_results"]["gate_scope"] == "pre_adoption_only"
    assert result["derived_results"]["topology_prerequisite_precedence_ref"] == "v2.1.33"
