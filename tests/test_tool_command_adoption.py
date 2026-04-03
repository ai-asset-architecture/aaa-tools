import json
from pathlib import Path

from typer.testing import CliRunner

from aaa.cli import app
from aaa import tool_command_adoption


PASS_BUNDLE = {
    "version": "v0.1",
    "tool_refs": ["ops.registry.inspect", "ops.registry.rebuild"],
    "command_refs": ["aaa.ops.registry.rebuild"],
    "binding_mode": "machine_parseable",
    "allowed_authority_map": {
        "aaa.ops.registry.rebuild": ["analysis_only", "mutation_repo"]
    },
    "evidence_targets": ["registry_snapshot", "artifact_report"],
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "tool_refs": ["ops.registry.inspect"],
    "command_refs": ["aaa.ops.registry.rebuild"],
    "binding_mode": "prose_only",
    "allowed_authority_map": {
        "aaa.ops.registry.rebuild": ["mutation_repo"]
    },
    "evidence_targets": ["registry_snapshot"],
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_machine_parseable_binding():
    result = tool_command_adoption.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_commands"] == ["aaa.ops.registry.rebuild"]
    assert result["resolved_tools"] == ["ops.registry.inspect", "ops.registry.rebuild"]


def test_validate_bundle_rejects_prose_only_binding():
    result = tool_command_adoption.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "binding_mode" in result["error_codes"]


def test_cli_validate_tool_command_adoption_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "validate-tool-command-adoption", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_validate_tool_command_adoption_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "validate-tool-command-adoption", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "binding_mode" in payload["error_codes"]
