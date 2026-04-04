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
