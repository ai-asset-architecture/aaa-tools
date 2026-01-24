import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class InitEnterpriseTests(unittest.TestCase):
    def test_init_enterprise_creates_gate_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            repo_src = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                [sys.executable, "-m", "aaa.cli", "init", "enterprise", "--repo-type", "docs"],
                cwd=repo_root,
                env={
                    **os.environ,
                    "AAA_ENTERPRISE_ROOT": str(repo_root),
                    "PYTHONPATH": str(repo_src),
                },
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            gate_path = repo_root / ".github" / "workflows" / "aaa-gate.yaml"
            metadata_path = repo_root / ".aaa" / "metadata.json"
            self.assertTrue(gate_path.exists())
            self.assertTrue(metadata_path.exists())
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["repo_type"], "docs")


if __name__ == "__main__":
    unittest.main()
