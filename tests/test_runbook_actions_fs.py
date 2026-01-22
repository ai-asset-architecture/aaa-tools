import os
import unittest
from pathlib import Path

from aaa import runbook_runtime
from aaa.action_registry import RuntimeSecurityError


class TestRunbookActionsFs(unittest.TestCase):
    def test_fs_write_and_update_frontmatter(self):
        tmp_path = Path(__file__).parent / "_tmp_fs"
        tmp_path.mkdir(parents=True, exist_ok=True)
        report_path = tmp_path / "report.md"
        md_path = tmp_path / "milestone.md"
        md_path.write_text("---\nstatus: Draft\n---\n\n# Title\n", encoding="utf-8")

        runbook = {
            "metadata": {"id": "ops/test", "version": "1.0.0"},
            "contract": {
                "inputs": [],
                "preconditions": [],
                "outputs": [],
                "required_scopes": ["fs:write"],
                "timeout_seconds": 30,
                "idempotency_check": {"command": "true", "expect_exit_code": 0},
                "error_codes": [],
            },
            "observability": {
                "emit_events": True,
                "audit_artifacts": [],
                "failure_modes": [],
                "declared_side_effects": [],
            },
            "steps": [
                {
                    "name": "write",
                    "action": "fs_write",
                    "args": ["path", str(report_path), "content", "Hello"],
                },
                {
                    "name": "update",
                    "action": "fs_update_frontmatter",
                    "args": [
                        "path",
                        str(md_path),
                        "set",
                        "status=Completed",
                        "completed_at=2026-01-22",
                    ],
                },
            ],
        }

        runbook_runtime.execute_runbook(runbook, inputs={})
        self.assertEqual(report_path.read_text(encoding="utf-8"), "Hello")
        updated = md_path.read_text(encoding="utf-8")
        self.assertIn("status: Completed", updated)
        self.assertIn("completed_at: 2026-01-22", updated)

    def test_fs_write_blocks_path_traversal(self):
        repo_root = Path(__file__).resolve().parents[1]
        escape_path = repo_root.parent / "escape.txt"
        if escape_path.exists():
            escape_path.unlink()

        runbook = {
            "metadata": {"id": "ops/test", "version": "1.0.0"},
            "contract": {
                "inputs": [],
                "preconditions": [],
                "outputs": [],
                "required_scopes": ["fs:write"],
                "timeout_seconds": 30,
                "idempotency_check": {"command": "true", "expect_exit_code": 0},
                "error_codes": [],
            },
            "observability": {
                "emit_events": True,
                "audit_artifacts": [],
                "failure_modes": [],
                "declared_side_effects": [],
            },
            "steps": [
                {
                    "name": "escape",
                    "action": "fs_write",
                    "args": ["path", str(escape_path), "content", "x"],
                }
            ],
        }

        cwd = Path.cwd()
        os.chdir(repo_root)
        try:
            with self.assertRaises(RuntimeSecurityError) as ctx:
                runbook_runtime.execute_runbook(runbook, inputs={})
            self.assertEqual(ctx.exception.code, "PATH_TRAVERSAL")
        finally:
            os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
