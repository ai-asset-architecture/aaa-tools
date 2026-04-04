import json
import subprocess
import sys
import tempfile
from pathlib import Path


def _write_note(path: Path) -> None:
    path.write_text(
        """# AAA Outside-In Validation Note

- date: 2026-04-05
- mode: remote client outside-in validation
- workspace_root: `/tmp/test-outside-in`
- disposable_boundary: `/tmp only; not canonical evidence storage`

## Step-by-step log

1. Read docs.
2. Ran package status.

## Observed outputs

- package CLI works

## Topology assumption summary

- repo_local expected and detected

## Blockers

1. none

## What evidence should be preserved outside /tmp

- logs/aaa-init-report.json
- package-select.txt

## Suggested follow-up tests

1. rerun with hybrid
""",
        encoding="utf-8",
    )


def test_outside_in_validate_builds_manifest_and_comparison_bundle(tmp_path: Path) -> None:
    sandbox_root = Path(tempfile.mkdtemp(prefix="aaa-v2140-test-", dir="/tmp"))
    workspace = sandbox_root / "workspace"
    service_repo = workspace / "aaa-tpl-service"
    (service_repo / ".github").mkdir(parents=True)
    (workspace / "logs").mkdir(parents=True)
    (workspace / "logs" / "aaa-init-report.json").write_text('{"summary":{"status":"pass"}}\n', encoding="utf-8")
    (workspace / "package-select.txt").write_text("ok\n", encoding="utf-8")
    (workspace / "aaa-init-report.json").write_text('{"summary":{"status":"pass"}}\n', encoding="utf-8")
    (workspace / ".aaa").mkdir(parents=True)
    (workspace / ".aaa" / "local_sandbox_bootstrap_candidate_evidence.json").write_text(
        json.dumps({"profile_name": "local_sandbox"}, ensure_ascii=True),
        encoding="utf-8",
    )
    note = sandbox_root / "outside-in-note.md"
    _write_note(note)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aaa.cli",
            "bootstrap",
            "outside-in-validate",
            "--note",
            str(note),
            "--workspace",
            str(workspace),
            "--level",
            "core",
            "--topology-mode",
            "repo_local",
            "--format",
            "json",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["validation"]["ok"] is True
    assert payload["comparison_ready_result_bundle"]["topology_mode_resolved"] == "repo_local"
    assert payload["comparison_ready_result_bundle"]["structure_acceptance_status"] == "structure_accepted"
    manifest = payload["promotion_candidate_manifest"]
    assert manifest["explicit_promotion_required"] is True
    assert manifest["unpromoted_artifacts_citable_by_version_index"] is False
    assert any(item["declared_path"] == "logs/aaa-init-report.json" for item in manifest["candidate_artifacts"])


def test_outside_in_validate_rejects_missing_sections_and_non_tmp_workspace(tmp_path: Path) -> None:
    outside_workspace = Path.cwd() / "not-tmp-workspace"
    note = tmp_path / "bad-note.md"
    note.write_text("# bad\n\n## Step-by-step log\n\n1. only one section\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aaa.cli",
            "bootstrap",
            "outside-in-validate",
            "--note",
            str(note),
            "--workspace",
            str(outside_workspace),
            "--level",
            "core",
            "--topology-mode",
            "repo_local",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "must live under /tmp" in (result.stdout + result.stderr)
