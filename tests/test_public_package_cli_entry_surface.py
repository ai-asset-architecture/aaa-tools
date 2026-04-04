from pathlib import Path

from typer.testing import CliRunner

from aaa.cli import app
from aaa import package_commands


runner = CliRunner()


def test_package_select_exposes_public_cli_entry_surface() -> None:
    result = runner.invoke(app, ["package", "select", "--level", "core", "--format", "json"])

    assert result.exit_code == 0
    assert '"command": "package_select"' in result.output
    assert '"package_level": "core"' in result.output


def test_package_select_rejects_alias_levels() -> None:
    result = runner.invoke(app, ["package", "select", "--level", "lite-bootstrap"])

    assert result.exit_code == 2
    assert "package level must be one of lite/core/full" in result.output


def test_package_resolve_uses_topology_aware_truth() -> None:
    result = runner.invoke(
        app,
        ["package", "resolve", "--level", "core", "--topology-mode", "repo_local", "--format", "json"],
    )

    assert result.exit_code == 0
    assert '"command": "package_resolve"' in result.output
    assert '"source_definition_artifact_ref": "aaa-docs/bootstrap/offering_definition_skeleton.md"' in result.output
    assert '"topology_mode": "repo_local"' in result.output


def test_package_status_reports_layered_topology_results(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    (workspace / "aaa-tools" / ".github" / "workflows").mkdir(parents=True)
    (workspace / "aaa-tpl-docs" / ".github" / "workflows").mkdir(parents=True)

    result = runner.invoke(
        app,
        [
            "package",
            "status",
            "--level",
            "core",
            "--topology-mode",
            "repo_local",
            "--workspace",
            str(workspace),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    assert '"topology_mode_detected": "repo_local"' in result.output
    assert '"structure_acceptance_status": "structure_accepted"' in result.output
    assert '"topology_completion_status": "topology_compliant"' in result.output


def test_detect_topology_mode_returns_hybrid_when_both_signals_exist(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    (workspace / ".github").mkdir(parents=True)
    (workspace / "aaa-tools" / ".github" / "workflows").mkdir(parents=True)

    result = package_commands.detect_topology_mode(workspace)

    assert result["detected_topology_mode"] == "hybrid"
