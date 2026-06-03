from pathlib import Path

from typer.testing import CliRunner

from aaa.cli import app


runner = CliRunner()
REPO_ROOT = Path(__file__).resolve().parents[1]


def test_validate_plan_example_is_runnable_from_repo_paths() -> None:
    plan_path = REPO_ROOT / "specs" / "examples" / "init-plan.example.json"
    schema_path = REPO_ROOT / "specs" / "plan.schema.json"

    result = runner.invoke(
        app,
        [
            "init",
            "validate-plan",
            "--plan",
            str(plan_path),
            "--schema",
            str(schema_path),
            "--jsonl",
        ],
    )

    assert result.exit_code == 0
    assert '"status": "ok"' in result.output or '"status":"ok"' in result.output
    assert str(plan_path) in result.output


def test_read_only_runbook_example_is_runnable_from_repo_paths() -> None:
    runbook_path = REPO_ROOT / "runbooks" / "examples" / "read-only-inspection.json"

    result = runner.invoke(
        app,
        [
            "run",
            "runbook",
            "--runbook-file",
            str(runbook_path),
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert "read-only inspection example completed" in result.output
    assert '"status": "success"' in result.output or '"status":"success"' in result.output
