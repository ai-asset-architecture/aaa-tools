import json
import tempfile
import unittest
from pathlib import Path

from aaa import init_commands


class TestRepoMetadataAnchor(unittest.TestCase):
    def test_write_repo_metadata_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()
            init_commands.write_repo_metadata(repo_root, "docs", "plan.v0.7.json")

            metadata = repo_root / ".aaa" / "metadata.json"
            self.assertTrue(metadata.exists())
            payload = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(payload["repo_type"], "docs")
            self.assertEqual(payload["plan_ref"], "plan.v0.7.json")


if __name__ == "__main__":
    unittest.main()
