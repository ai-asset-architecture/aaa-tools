from typer.testing import CliRunner

from aaa import bootstrap_commands
from aaa.cli import app


runner = CliRunner()


def test_bootstrap_supported_path_exposes_single_canonical_sequence() -> None:
    result = runner.invoke(
        app,
        ["bootstrap", "supported-path", "--level", "core", "--topology-mode", "repo_local", "--format", "json"],
    )

    assert result.exit_code == 0
    assert '"command": "bootstrap_supported_path"' in result.output
    assert '"canonical_supported_path_count": 1' in result.output
    assert '"path_semantics": "publicly_documented_sequence"' in result.output
    assert '"supported_path_fully_automated": false' in result.output
    assert '"full_execution_readiness_certified": false' in result.output


def test_bootstrap_supported_path_rejects_alias_level() -> None:
    result = runner.invoke(app, ["bootstrap", "supported-path", "--level", "lite-bootstrap"])

    assert result.exit_code == 2
    assert "package level must be one of lite/core/full" in result.output


def test_bootstrap_supported_path_marks_local_sandbox_as_profile_not_path() -> None:
    payload = bootstrap_commands.supported_path("full", "hybrid")

    assert payload["local_sandbox_is_supported_path_alias"] is False
    assert payload["environment_profile_counted_as_supported_path"] is False
    assert payload["alternate_sequences"][1]["classification"] == "environment_profile_overlay_only"


def test_bootstrap_supported_path_human_output_lists_commands() -> None:
    result = runner.invoke(app, ["bootstrap", "supported-path", "--level", "lite", "--topology-mode", "dedicated_repo"])

    assert result.exit_code == 0
    assert "1.package_select" in result.output
    assert "aaa package select --level lite --format json" in result.output
    assert "5.topology_status_check" in result.output
    assert "supported_path_fully_automated=false" in result.output


def test_bootstrap_supported_path_json_marks_client_authored_artifacts() -> None:
    payload = bootstrap_commands.supported_path("core", "repo_local")

    step3 = payload["canonical_bootstrap_steps"][2]
    step4 = payload["canonical_bootstrap_steps"][3]

    assert step3["input_artifacts"][0]["artifact_origin"] == "client_authored"
    assert step3["input_artifacts"][0]["artifact_required_for_step"] is True
    assert step3["input_artifacts"][0]["artifact_not_auto_generated_in_v2_1_41"] is True
    assert step3["input_artifacts"][0]["artifact_classification"] == "canonical_public_artifact"

    assert step4["input_artifacts"][0]["artifact_origin"] == "client_authored"
    assert step4["input_artifacts"][0]["artifact_not_auto_generated_in_v2_1_41"] is True
    assert payload["client_authored_artifacts_present"] is True
    assert payload["runtime_generation_coverage_complete"] is False
    assert payload["automation_boundary"] == "client_authored_inputs_still_required"


def test_bootstrap_supported_path_separates_canonical_and_diagnostic_artifacts() -> None:
    payload = bootstrap_commands.supported_path("core", "hybrid")

    profile_overlay = payload["alternate_sequences"][1]

    assert profile_overlay["classification"] == "environment_profile_overlay_only"
    assert profile_overlay["diagnostic_or_internal_only_artifacts"][0]["artifact_classification"] == (
        "diagnostic_or_internal_only_artifact"
    )
