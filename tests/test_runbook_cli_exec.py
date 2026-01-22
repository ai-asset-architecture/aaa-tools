import json
import subprocess
import sys
from pathlib import Path
import unittest


class RunbookCliJsonTests(unittest.TestCase):
    def test_runbook_cli_json_error_output(self):
        repo_root = Path(__file__).resolve().parents[1]
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
        )
        data = json.loads(result.stdout)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["error_code"], "SCOPE_VIOLATION")


if __name__ == "__main__":
    unittest.main()
