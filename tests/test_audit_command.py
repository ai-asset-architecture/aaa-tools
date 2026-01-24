import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class AuditCommandTests(unittest.TestCase):
    def _write_runner(self, root: Path) -> None:
        runner = root / "runner" / "run_repo_checks.py"
        runner.parent.mkdir(parents=True, exist_ok=True)
        runner.write_text(
            "import json\n"
            "print(json.dumps({'check': 'stub', 'pass': True, 'details': []}))\n",
            encoding="utf-8",
        )

    def test_audit_local_outputs_report(self):
        with tempfile.TemporaryDirectory() as repo_dir, tempfile.TemporaryDirectory() as evals_dir:
            repo_root = Path(repo_dir)
            evals_root = Path(evals_dir)
            self._write_runner(evals_root)
            (repo_root / ".aaa").mkdir(parents=True, exist_ok=True)
            (repo_root / ".aaa" / "metadata.json").write_text(
                json.dumps({"repo_type": "docs"}, ensure_ascii=True),
                encoding="utf-8",
            )
            output_path = repo_root / "compliance_report.json"
            repo_root = Path(repo_dir)
            repo_src = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "aaa.cli",
                    "audit",
                    "--local",
                    "--output",
                    str(output_path),
                ],
                cwd=repo_root,
                env={**os.environ, "AAA_EVALS_ROOT": str(evals_root), "PYTHONPATH": str(repo_src)},
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["repos"]), 1)
            self.assertEqual(payload["repos"][0]["repo_type"], "docs")


if __name__ == "__main__":
    unittest.main()
