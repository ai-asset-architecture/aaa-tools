import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import skill_and_plugin_extension_runtime
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "extension_plane",
    "line_class": "mandatory_core_absorption_line",
    "extension_id": "skill://repo-check-helper",
    "manifest_class": "skill_manifest",
    "load_mode": "registered_load",
    "register_boundary": "tool_injection",
    "trust_boundary": "trusted",
    "injection_target": "tool_registry_slot",
    "canonical_override_allowed": False,
    "task_lifecycle_definition_allowed": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "extension_plane",
    "line_class": "mandatory_core_absorption_line",
    "extension_id": "plugin://override-core",
    "manifest_class": "plugin_manifest",
    "load_mode": "local_load",
    "register_boundary": "command_injection",
    "trust_boundary": "restricted",
    "injection_target": "command_registry_slot",
    "canonical_override_allowed": True,
    "task_lifecycle_definition_allowed": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_governed_extension_plane():
    result = skill_and_plugin_extension_runtime.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "extension_plane"


def test_validate_bundle_rejects_canonical_override_and_task_lifecycle_expansion():
    result = skill_and_plugin_extension_runtime.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "canonical_override_allowed" in result["error_codes"]
    assert "task_lifecycle_definition_allowed" in result["error_codes"]
    assert "trust_boundary" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_extension_runtime_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "extension-runtime", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_extension_runtime_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "extension-runtime", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "canonical_override_allowed" in payload["error_codes"]
