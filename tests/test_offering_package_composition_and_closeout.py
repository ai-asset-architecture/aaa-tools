from pathlib import Path

from aaa import offering_package_composition_and_closeout as runtime


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
    "aaa-tpl-docs/internal/development/contracts/ops/examples/pass/2026-04-04-v2.1.29-offering-package-composition-and-closeout.pass.json"
)
FAIL_BUNDLE = _resolve_fixture(
    "aaa-tpl-docs/internal/development/contracts/ops/examples/fail/2026-04-04-v2.1.29-offering-package-composition-and-closeout.fail.json"
)


def test_validate_bundle_accepts_explicit_package_runtime_closeout() -> None:
    result = runtime.validate_bundle_file(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["status"] == "ok"
    assert result["resolved_runtime_plane_mode"] == "offering_package_composition_closeout"
    assert result["derived_results"]["consumed_stage_count"] == 6


def test_validate_bundle_rejects_semantics_rejudgment_and_conditional_expansion() -> None:
    result = runtime.validate_bundle_file(FAIL_BUNDLE)

    assert result["valid"] is False
    assert "post_topology_consumption_required" in result["error_codes"]
    assert "topology_closeout_precedence_ref" in result["error_codes"]
    assert "consumed_package_runtime_stages" in result["error_codes"]
    assert "consumed_stage_set_mode" in result["error_codes"]
    assert "consumed_stage_set_hash" in result["error_codes"]
    assert "offering_semantics_rejudgment_allowed" in result["error_codes"]
    assert "conditional_expansion_triggered" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_validate_bundle_requires_canonical_stage_order() -> None:
    payload = runtime.load_bundle(PASS_BUNDLE)
    payload["consumed_package_runtime_stages"] = list(reversed(payload["consumed_package_runtime_stages"]))

    result = runtime.validate_bundle(payload)

    assert result["valid"] is False
    assert "consumed_package_runtime_stages" in result["error_codes"]


def test_validate_bundle_exposes_topology_precedence_ref() -> None:
    result = runtime.validate_bundle_file(PASS_BUNDLE)

    assert result["derived_results"]["closeout_role"] == "package_runtime_core_closeout"
    assert result["derived_results"]["topology_closeout_precedence_ref"] == "v2.1.36"
