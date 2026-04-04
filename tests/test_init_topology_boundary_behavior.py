import json
from pathlib import Path

from typer.testing import CliRunner

from aaa.cli import app


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _hybrid_plan() -> dict:
    return {
        "plan_version": "2.0",
        "aaa": {
            "org": "ai-asset-architecture",
            "version_tag": "v2.0.4",
            "templates": {
                "docs": "aaa-tpl-docs",
                "service": "aaa-tpl-service",
                "frontend": "aaa-tpl-frontend",
            },
            "actions_repo": "aaa-actions",
        },
        "target": {
            "project_slug": "demo",
            "org": "demo",
            "visibility": "private",
            "default_branch": "main",
            "mode": "pr",
            "github_governance_topology": "hybrid",
        },
        "steps": [
            {"id": "preflight", "type": "check", "description": "preflight", "commands": ["aaa --version"]}
        ],
        "reporting": {"output_schema_path": "output.schema.json", "required_fields": ["metadata"]},
        "default_preset": "governance_native",
        "presets": {
            "governance_native": {
                "github_governance_topology": "hybrid",
                "repos": [
                    {
                        "name": ".github",
                        "type": "docs",
                        "template": "aaa-tpl-docs",
                        "description": "Governance repo",
                        "owners": ["@aaa/architect"],
                        "required_checks": ["lint", "test", "eval"],
                    },
                    {
                        "name": "org-docs",
                        "type": "docs",
                        "template": "aaa-tpl-docs",
                        "description": "Docs repo",
                        "owners": ["@aaa/architect"],
                        "required_checks": ["lint", "test", "eval"],
                    },
                ],
            }
        },
    }


def test_validate_plan_jsonl_emits_structure_only_topology_boundary_signal(tmp_path: Path):
    plan_path = tmp_path / "plan.json"
    _write_json(plan_path, _hybrid_plan())
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "init",
            "validate-plan",
            "--plan",
            str(plan_path),
            "--schema",
            str(Path(__file__).resolve().parents[1] / "specs" / "plan.schema.json"),
            "--jsonl",
        ],
    )

    assert result.exit_code == 0
    lines = [json.loads(line) for line in result.output.splitlines() if line.strip()]
    payload = lines[-1]["data"]
    assert payload["topology_mode"] == "hybrid"
    assert payload["structure_pass_is_topology_completion_pass"] is False
    assert payload["downstream_topology_adjudication_ref"] == "v2.1.35"


def test_run_plan_creates_missing_log_dir_for_report(tmp_path: Path, monkeypatch):
    plan_path = tmp_path / "plan.json"
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    log_dir = tmp_path / "missing-log-dir"
    _write_json(plan_path, _hybrid_plan())
    runner = CliRunner()
    monkeypatch.setenv("WORKSPACE_DIR", str(workspace_dir))

    result = runner.invoke(
        app,
        [
            "init",
            "--plan",
            str(plan_path),
            "--preset",
            "governance_native",
            "--dry-run",
            "--jsonl",
            "--log-dir",
            str(log_dir),
        ],
    )

    assert result.exit_code == 0
    report_path = log_dir / "aaa-init-report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["topology_boundary_signal"]["topology_mode"] == "hybrid"
    assert report["summary"]["topology_boundary_signal"]["structure_pass_is_topology_completion_pass"] is False
