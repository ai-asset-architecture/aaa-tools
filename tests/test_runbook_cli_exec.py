import os
import json
import subprocess
import sys
from pathlib import Path
import unittest


class RunbookCliJsonTests(unittest.TestCase):
    def test_runbook_cli_json_error_output(self):
        repo_root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env["AAA_DISABLE_UPDATE_HINT"] = "1"
        env["PYTHONPATH"] = str(repo_root)
        
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "aaa.cli",
                "run",
                "runbook",
                "security/attack-scope@1.0.0",
                "--json",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "failure")
        self.assertTrue("SCOPE_VIOLATION" in data.get("errors", []) or "SCOPE_VIOLATION" in str(data))

    def test_runbook_cli_json_error_output_from_file(self):
        repo_root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env["AAA_DISABLE_UPDATE_HINT"] = "1"
        env["PYTHONPATH"] = str(repo_root)

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "aaa.cli",
                "run",
                "runbook",
                "--runbook-file",
                "runbooks/security/attack-scope.yaml",
                "--json",
            ],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "failure")
        self.assertTrue("SCOPE_VIOLATION" in data.get("errors", []) or "SCOPE_VIOLATION" in str(data))


if __name__ == "__main__":
    unittest.main()
