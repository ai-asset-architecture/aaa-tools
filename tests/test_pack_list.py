import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class PackListTests(unittest.TestCase):
    def test_pack_list_outputs_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            repo_root = Path(__file__).resolve().parents[1]
            packs_dir = root / ".aaa" / "packs"
            packs_dir.mkdir(parents=True, exist_ok=True)
            installed = {"installed": [{"id": "agent-safety", "version": "1.0.0"}]}
            (packs_dir / "installed.json").write_text(
                json.dumps(installed, ensure_ascii=True),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, "-m", "aaa.cli", "pack", "list"],
                cwd=root,
                env={**os.environ, "PYTHONPATH": str(repo_root)},
                capture_output=True,
                text=True,
                check=False,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["installed"][0]["id"], "agent-safety")


if __name__ == "__main__":
    unittest.main()
