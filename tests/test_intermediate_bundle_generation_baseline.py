"""
Test suite: v2.1.42 Intermediate Bundle Generation Baseline
===========================================================
Covers: generation report, individual bundle generators, and schema validator.
"""

from __future__ import annotations

import pytest
from aaa.intermediate_bundle_generation_baseline import (
    ARTIFACT_CATALOGUE,
    RUNTIME_PLANE_MODE,
    LINE_CLASS,
    SCHEMA_VERSION,
    build_generation_report,
    generate_prerequisite_bundle,
    generate_materialization_mapping_bundle,
    validate_bundle,
)


# ---------------------------------------------------------------------------
# build_generation_report
# ---------------------------------------------------------------------------

class TestBuildGenerationReport:
    def test_no_filter_returns_all_artifacts(self):
        report = build_generation_report()
        assert report["version"] == SCHEMA_VERSION
        assert report["runtime_plane_mode"] == RUNTIME_PLANE_MODE
        assert report["line_class"] == LINE_CLASS
        assert report["supported_path_fully_automated"] is False
        assert report["full_orchestration_provided"] is False
        assert report["full_execution_readiness_certified"] is False
        assert len(report["artifacts"]) == len(ARTIFACT_CATALOGUE)

    def test_topology_filter_dedicated_repo(self):
        report = build_generation_report(topology="dedicated_repo")
        for art in report["artifacts"]:
            assert "dedicated_repo" in art["topology_constraints"]

    def test_topology_filter_repo_local(self):
        report = build_generation_report(topology="repo_local")
        for art in report["artifacts"]:
            assert "repo_local" in art["topology_constraints"]

    def test_topology_filter_hybrid(self):
        report = build_generation_report(topology="hybrid")
        for art in report["artifacts"]:
            assert "hybrid" in art["topology_constraints"]

    def test_profile_filter_local_sandbox(self):
        report = build_generation_report(topology="dedicated_repo", profile="local_sandbox")
        for art in report["artifacts"]:
            assert "local_sandbox" in art["profile_constraints"]

    def test_invalid_topology_raises(self):
        with pytest.raises(ValueError, match="topology must be one of"):
            build_generation_report(topology="invalid_topology")

    def test_generation_summary_counts(self):
        report = build_generation_report()
        total = report["generation_summary"]["total_artifacts"]
        automated = report["generation_summary"]["automated_in_v2_1_42"]
        pending = report["generation_summary"]["manual_pending"]
        assert automated + pending == total

    def test_supported_path_not_fully_automated(self):
        report = build_generation_report()
        # v2.1.42 explicitly declares partial automation only
        assert report["supported_path_fully_automated"] is False

    def test_not_in_scope_declared(self):
        report = build_generation_report()
        not_in_scope = report["not_in_scope"]
        assert any("orchestration" in item for item in not_in_scope)
        assert any("readiness certification" in item for item in not_in_scope)

    def test_gap_declaration_lists_manual_artifacts(self):
        report = build_generation_report()
        gap_ids = {g["artifact_id"] for g in report["gap_declaration"]}
        manual_ids = {
            a["artifact_id"] for a in report["artifacts"]
            if a["generation_status"] != "automated_in_v2_1_42"
        }
        assert gap_ids == manual_ids


# ---------------------------------------------------------------------------
# generate_prerequisite_bundle
# ---------------------------------------------------------------------------

class TestGeneratePrerequisiteBundle:
    @pytest.mark.parametrize("topology", ["dedicated_repo", "repo_local", "hybrid"])
    def test_all_topologies_generate(self, topology):
        bundle = generate_prerequisite_bundle(topology)
        assert bundle["artifact_id"] == "prerequisite_bundle"
        assert bundle["artifact_origin"] == "command_emitted"
        assert bundle["generation_status"] == "automated_in_v2_1_42"
        assert bundle["topology"] == topology

    def test_default_profile(self):
        bundle = generate_prerequisite_bundle("dedicated_repo")
        assert bundle["profile"] == "default"

    def test_local_sandbox_profile(self):
        bundle = generate_prerequisite_bundle("repo_local", profile="local_sandbox")
        assert bundle["profile"] == "local_sandbox"

    def test_gate_verdict_not_activation(self):
        bundle = generate_prerequisite_bundle("dedicated_repo")
        assert bundle["payload"]["gate_verdict_not_activation"] is True
        assert bundle["payload"]["gate_verdict_not_completion"] is True

    def test_invalid_topology_raises(self):
        with pytest.raises(ValueError, match="topology must be one of"):
            generate_prerequisite_bundle("bad_topology")


# ---------------------------------------------------------------------------
# generate_materialization_mapping_bundle
# ---------------------------------------------------------------------------

class TestGenerateMaterializationMappingBundle:
    @pytest.mark.parametrize("topology,expected_rule", [
        ("dedicated_repo", "org_repo_only"),
        ("repo_local", "repo_local_only"),
        ("hybrid", "hybrid_split"),
    ])
    def test_placement_rules(self, topology, expected_rule):
        bundle = generate_materialization_mapping_bundle(topology)
        assert bundle["payload"]["governance_asset_placement_rule"] == expected_rule

    def test_no_back_write_allowed(self):
        bundle = generate_materialization_mapping_bundle("dedicated_repo")
        assert bundle["payload"]["back_write_allowed"] is False

    def test_no_reinterpretation_allowed(self):
        bundle = generate_materialization_mapping_bundle("hybrid")
        assert bundle["payload"]["reinterpretation_allowed"] is False

    def test_invalid_topology_raises(self):
        with pytest.raises(ValueError, match="topology must be one of"):
            generate_materialization_mapping_bundle("wrong")


# ---------------------------------------------------------------------------
# validate_bundle
# ---------------------------------------------------------------------------

class TestValidateBundle:
    def _valid_payload(self):
        return {
            "version": "v0.1",
            "runtime_plane_mode": "intermediate_bundle_generation_baseline",
            "line_class": "canonical_path_generation_line",
            "supported_path_fully_automated": False,
            "full_orchestration_provided": False,
            "full_execution_readiness_certified": False,
            "artifacts": [
                {
                    "artifact_id": "prerequisite_bundle",
                    "artifact_role": "prerequisite_gate_input",
                    "artifact_origin": "command_emitted",
                    "artifact_required_for_step": True,
                    "artifact_not_auto_generated_in_v2_1_42": False,
                    "generation_status": "automated_in_v2_1_42",
                    "topology_constraints": ["dedicated_repo"],
                    "profile_constraints": ["default"],
                }
            ],
        }

    def test_valid_payload_passes(self):
        result = validate_bundle(self._valid_payload())
        assert result["verdict"] == "pass"
        assert result["error_count"] == 0

    def test_missing_top_level_key_fails(self):
        payload = self._valid_payload()
        del payload["supported_path_fully_automated"]
        result = validate_bundle(payload)
        assert result["verdict"] == "fail"
        assert result["error_count"] > 0

    def test_wrong_version_fails(self):
        payload = self._valid_payload()
        payload["version"] = "v0.2"
        result = validate_bundle(payload)
        assert result["verdict"] == "fail"

    def test_supported_path_true_fails(self):
        payload = self._valid_payload()
        payload["supported_path_fully_automated"] = True
        result = validate_bundle(payload)
        assert result["verdict"] == "fail"

    def test_invalid_artifact_origin_fails(self):
        payload = self._valid_payload()
        payload["artifacts"][0]["artifact_origin"] = "magic"
        result = validate_bundle(payload)
        assert result["verdict"] == "fail"

    def test_invalid_topology_in_artifact_fails(self):
        payload = self._valid_payload()
        payload["artifacts"][0]["topology_constraints"] = ["unknown_topo"]
        result = validate_bundle(payload)
        assert result["verdict"] == "fail"

    def test_empty_artifacts_fails(self):
        payload = self._valid_payload()
        payload["artifacts"] = []
        result = validate_bundle(payload)
        assert result["verdict"] == "fail"

    def test_inputs_digest_present(self):
        result = validate_bundle(self._valid_payload())
        assert "inputs_digest" in result
        assert len(result["inputs_digest"]) == 64  # sha256 hex

    def test_pass_fixture_validates(self):
        """Validate the Step1 pass fixture against the runtime validator."""
        import json, pathlib
        fixture_path = (
            pathlib.Path(__file__).parent.parent.parent
            / "aaa-tpl-docs/internal/development/contracts/ops/examples/pass"
            / "2026-04-05-v2.1.42-intermediate-bundle-generation-baseline.pass.json"
        )
        if fixture_path.exists():
            payload = json.loads(fixture_path.read_text())
            result = validate_bundle(payload)
            assert result["verdict"] == "pass", f"pass fixture failed: {result['errors']}"

    def test_fail_fixture_fails_validation(self):
        """Validate the Step1 fail fixture is caught by the runtime validator."""
        import json, pathlib
        fixture_path = (
            pathlib.Path(__file__).parent.parent.parent
            / "aaa-tpl-docs/internal/development/contracts/ops/examples/fail"
            / "2026-04-05-v2.1.42-intermediate-bundle-generation-baseline.fail.json"
        )
        if fixture_path.exists():
            payload = json.loads(fixture_path.read_text())
            result = validate_bundle(payload)
            assert result["verdict"] == "fail", "fail fixture should not pass"
