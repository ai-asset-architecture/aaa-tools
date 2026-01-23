import json
import os
import tempfile
from pathlib import Path
import unittest


from aaa import check_commands


class CheckCommandTests(unittest.TestCase):
    def _write_runner(self, root: Path) -> Path:
        runner = root / "runner" / "run_repo_checks.py"
        runner.parent.mkdir(parents=True, exist_ok=True)
        runner.write_text(
            "import json\n"
            "print(json.dumps({'check': 'stub', 'pass': True, 'details': []}))\n",
            encoding="utf-8",
        )
        return runner

    def _write_gate_workflow(self, repo_root: Path, uses_gate: bool) -> None:
        workflows = repo_root / ".github" / "workflows"
        workflows.mkdir(parents=True, exist_ok=True)
        content = "name: ci\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - run: echo ok\n"
        if uses_gate:
            content = (
                "name: gate\njobs:\n  governance-gate:\n    uses: "
                "ai-asset-architecture/aaa-actions/.github/workflows/reusable-gate.yaml@main\n"
            )
        (workflows / "ci.yml").write_text(content, encoding="utf-8")

    def test_blocking_check_fails_without_gate(self):
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as evals_dir:
            repo_root = Path(repo_dir)
            evals_root = Path(evals_dir)
            self._write_runner(evals_root)
            self._write_gate_workflow(repo_root, uses_gate=False)
            os.environ["AAA_EVALS_ROOT"] = str(evals_root)
            result = check_commands.run_blocking_check(repo_root)
            self.assertNotEqual(result["exit_code"], 0)
            self.assertIn("missing_gate_workflow", result["errors"])

    def test_blocking_check_passes_with_gate(self):
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as evals_dir:
            repo_root = Path(repo_dir)
            evals_root = Path(evals_dir)
            self._write_runner(evals_root)
            self._write_gate_workflow(repo_root, uses_gate=True)
            os.environ["AAA_EVALS_ROOT"] = str(evals_root)
            result = check_commands.run_blocking_check(repo_root)
            self.assertEqual(result["exit_code"], 0)
            self.assertEqual(result["errors"], [])


if __name__ == "__main__":
    unittest.main()
