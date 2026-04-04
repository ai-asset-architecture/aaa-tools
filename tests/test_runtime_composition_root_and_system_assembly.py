import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import runtime_composition_root_and_system_assembly
from aaa.cli import app


PASS_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "composition_root",
    "line_class": "mandatory_core_absorption_line",
    "closeout_role": "core_line_closeout",
    "bootstrap_order": [
        "permission_gate",
        "event_stream",
        "session_persistence",
        "runtime_control",
        "result_normalization",
        "workflow_runtime",
        "delegation_lifecycle",
        "extension_plane",
    ],
    "consumed_runtime_planes": [
        "permission_gate",
        "event_stream",
        "session_persistence",
        "runtime_control",
        "result_normalization",
        "workflow_runtime",
        "delegation_lifecycle",
        "extension_plane",
    ],
    "consumed_runtime_plane_set_mode": "explicit_enumeration",
    "startup_boundary": "core_line_only",
    "assembly_outcome": "assembled",
    "consumed_plane_semantics_rejudgment_allowed": False,
    "new_primary_law_allowed": False,
    "conditional_expansion_enabled": False,
    "prose_fallback_allowed": False,
}


FAIL_BUNDLE = {
    "version": "v0.1",
    "runtime_plane_mode": "composition_root",
    "line_class": "mandatory_core_absorption_line",
    "closeout_role": "core_line_closeout",
    "bootstrap_order": [
        "permission_gate",
        "event_stream",
        "result_normalization",
    ],
    "consumed_runtime_planes": [
        "permission_gate",
        "event_stream",
        "result_normalization",
    ],
    "consumed_runtime_plane_set_mode": "explicit_enumeration",
    "startup_boundary": "core_plus_conditional",
    "assembly_outcome": "assembled",
    "consumed_plane_semantics_rejudgment_allowed": True,
    "new_primary_law_allowed": True,
    "conditional_expansion_enabled": True,
    "prose_fallback_allowed": True,
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_validate_bundle_accepts_explicit_core_line_assembly():
    result = runtime_composition_root_and_system_assembly.validate_bundle(PASS_BUNDLE)

    assert result["status"] == "ok"
    assert result["valid"] is True
    assert result["resolved_runtime_plane_mode"] == "composition_root"


def test_validate_bundle_rejects_partial_plane_set_and_semantics_rejudgment():
    result = runtime_composition_root_and_system_assembly.validate_bundle(FAIL_BUNDLE)

    assert result["status"] == "error"
    assert result["valid"] is False
    assert "bootstrap_order" in result["error_codes"]
    assert "consumed_runtime_planes" in result["error_codes"]
    assert "consumed_plane_semantics_rejudgment_allowed" in result["error_codes"]
    assert "conditional_expansion_enabled" in result["error_codes"]
    assert "prose_fallback_allowed" in result["error_codes"]


def test_cli_composition_root_json_success(tmp_path: Path):
    bundle = tmp_path / "bundle.pass.json"
    _write_json(bundle, PASS_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "composition-root", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["status"] == "ok"
    assert payload["valid"] is True


def test_cli_composition_root_json_failure(tmp_path: Path):
    bundle = tmp_path / "bundle.fail.json"
    _write_json(bundle, FAIL_BUNDLE)
    runner = CliRunner()

    result = runner.invoke(
        app,
        ["governance", "composition-root", "--bundle", str(bundle), "--format", "json"],
    )

    assert result.exit_code == 2
    payload = json.loads(result.output)
    assert payload["status"] == "error"
    assert payload["valid"] is False
    assert "consumed_plane_semantics_rejudgment_allowed" in payload["error_codes"]
