from pathlib import Path

from aaa import package_machine_interface_read_boundary as runtime


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
    "aaa-tpl-docs/internal/development/contracts/ops/examples/pass/2026-04-04-v2.1.28-package-machine-interface-read-boundary.pass.json"
)
FAIL_BUNDLE = _resolve_fixture(
    "aaa-tpl-docs/internal/development/contracts/ops/examples/fail/2026-04-04-v2.1.28-package-machine-interface-read-boundary.fail.json"
)


def test_validate_bundle_accepts_canonical_read_boundary() -> None:
    result = runtime.validate_bundle_file(PASS_BUNDLE)

    assert result["valid"] is True
    assert result["status"] == "ok"
    assert result["resolved_runtime_plane_mode"] == "package_machine_interface_read_boundary"
    assert result["derived_results"]["cli_output_mapping_mode"] == "isomorphic_human_json_mapping"


def test_validate_bundle_rejects_write_capable_or_orchestration_claims() -> None:
    result = runtime.validate_bundle_file(FAIL_BUNDLE)

    assert result["valid"] is False
    assert "post_topology_consumption_required" in result["error_codes"]
    assert "topology_read_boundary_precedence_ref" in result["error_codes"]
    assert "exposed_payloads" in result["error_codes"]
    assert "cli_output_mapping_mode" in result["error_codes"]
    assert "read_only_boundary" in result["error_codes"]
    assert "ai_orchestration_claimed" in result["error_codes"]
    assert "remote_session_semantics_included" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_validate_bundle_requires_all_payload_classes() -> None:
    payload = runtime.load_bundle(PASS_BUNDLE)
    payload["exposed_payloads"] = ["package_selection", "package_status"]

    result = runtime.validate_bundle(payload)

    assert result["valid"] is False
    assert "exposed_payloads" in result["error_codes"]


def test_validate_bundle_preserves_read_only_boundary_shape() -> None:
    result = runtime.validate_bundle_file(PASS_BUNDLE)

    assert result["derived_results"]["interface_scope"] == "machine_read_boundary_only"
    assert result["derived_results"]["read_only_boundary"] is True
    assert len(result["derived_results"]["exposed_payloads"]) == 5
