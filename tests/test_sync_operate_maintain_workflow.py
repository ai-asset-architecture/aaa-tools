import json
import os
import subprocess
import sys
from pathlib import Path


def _run_cli(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[1]
    env = os.environ.copy()
    env["AAA_DISABLE_UPDATE_HINT"] = "1"
    env["PYTHONPATH"] = str(repo_root)
    return subprocess.run(
        [sys.executable, "-m", "aaa.cli", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def test_sync_operate_maintain_workflow_preserves_existing_indexes(tmp_path):
    existing = tmp_path / "aaa-tpl-docs" / "version_index.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("# custom version index\n", encoding="utf-8")

    result = _run_cli(tmp_path, ["sync", "operate-maintain-workflow"])
    assert result.returncode == 0

    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["capability"] == "operate_maintain_workflow_v2"
    assert "aaa-tpl-docs/version_index.md" in payload["skipped"]
    assert existing.read_text(encoding="utf-8") == "# custom version index\n"
    assert (tmp_path / "aaa-tpl-docs" / "workflow_index.md").exists()
    assert (tmp_path / "aaa-docs" / "bootstrap" / "operate_maintain_guide.md").exists()


def test_sync_operate_maintain_workflow_force_index_overwrites(tmp_path):
    existing = tmp_path / "aaa-tpl-docs" / "workflow_index.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("# custom workflow index\n", encoding="utf-8")

    result = _run_cli(tmp_path, ["sync", "operate-maintain-workflow", "--force-index"])
    assert result.returncode == 0

    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["force_index"] is True
    assert "aaa-tpl-docs/workflow_index.md" in payload["copied"]
    assert existing.read_text(encoding="utf-8").startswith("# Workflow Index (Canonical Source)")
