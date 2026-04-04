import json
from pathlib import Path

from typer.testing import CliRunner

from aaa import init_commands
from aaa.cli import app


runner = CliRunner()


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _repo_local_plan() -> dict:
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
            "project_slug": "sandbox-demo",
            "org": "demo",
            "visibility": "private",
            "default_branch": "main",
            "mode": "pr",
            "github_governance_topology": "repo_local",
        },
        "steps": [
            {"id": "preflight", "type": "check", "description": "preflight", "commands": ["aaa --version"]},
            {"id": "ensure_repos", "type": "github", "description": "ensure repos", "commands": ["aaa init ensure-repos"]},
        ],
        "reporting": {"output_schema_path": "output.schema.json", "required_fields": ["metadata"]},
        "default_preset": "repo_local_sandbox",
        "presets": {
            "repo_local_sandbox": {
                "github_governance_topology": "repo_local",
                "repos": [
                    {
                        "name": "client-docs",
                        "type": "docs",
                        "template": "aaa-tpl-docs",
                        "description": "Client docs repo",
                        "owners": ["@aaa/architect"],
                        "required_checks": ["lint", "test", "eval"],
                    }
                ],
            }
        },
    }


def test_bootstrap_profile_exposes_local_sandbox_contract() -> None:
    result = runner.invoke(
        app,
        [
            "bootstrap",
            "profile",
            "--profile",
            "local_sandbox",
            "--level",
            "core",
            "--topology-mode",
            "repo_local",
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["profile_name"] == "local_sandbox"
    assert payload["dry_run_alias"] is False
    assert payload["requires_github_side_effects"] is False
    assert payload["requires_org_repo_creation"] is False
    assert payload["supported_path_count_changed"] is False


def test_init_local_sandbox_profile_runs_without_github_and_emits_candidate_evidence(
    tmp_path: Path, monkeypatch
) -> None:
    plan_path = tmp_path / "plan.json"
    workspace_dir = tmp_path / "workspace"
    workspace_dir.mkdir()
    log_dir = tmp_path / "logs"
    _write_json(plan_path, _repo_local_plan())

    original_which = init_commands.shutil.which

    def fake_which(name: str):
        if name == "gh":
            return None
        return original_which(name)

    monkeypatch.setattr(init_commands.shutil, "which", fake_which)
    monkeypatch.setenv("WORKSPACE_DIR", str(workspace_dir))

    result = runner.invoke(
        app,
        [
            "init",
            "--plan",
            str(plan_path),
            "--preset",
            "repo_local_sandbox",
            "--profile",
            "local_sandbox",
            "--jsonl",
            "--log-dir",
            str(log_dir),
        ],
    )

    assert result.exit_code == 0

    report_path = log_dir / "aaa-init-report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    profile = report["summary"]["execution_profile"]
    assert profile["profile_name"] == "local_sandbox"
    assert profile["dry_run_alias"] is False
    assert report["summary"]["candidate_evidence_bundle_path"].endswith(
        ".aaa/local_sandbox_bootstrap_candidate_evidence.json"
    )

    repo_root = workspace_dir / "client-docs"
    assert repo_root.exists()
    assert (repo_root / ".aaa" / "metadata.json").exists()

    candidate_bundle = workspace_dir / ".aaa" / "local_sandbox_bootstrap_candidate_evidence.json"
    assert candidate_bundle.exists()
    bundle = json.loads(candidate_bundle.read_text(encoding="utf-8"))
    assert bundle["profile_name"] == "local_sandbox"
    assert bundle["canonical_evidence_plane"] is False
    assert bundle["requires_explicit_promotion"] is True
