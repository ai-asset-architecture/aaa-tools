import json
import tempfile
import unittest
from pathlib import Path

from aaa import governance_commands


class TestGovernanceUpdateIndexCli(unittest.TestCase):
    def _write_md(self, path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    def test_cli_wrapper_creates_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp) / "docs"
            docs.mkdir(parents=True)
            self._write_md(
                docs / "001-adr.md",
                "---\n"
                "title: ADR One\nstatus: Accepted\nowner: @arch\n"
                "---\n\n# ADR One\n",
            )

            template = "# Index\n\n{{ range files }}- {{ .Path }}{{ end }}\n"
            payload = governance_commands.update_index_cli(
                target_dir=str(docs),
                pattern="*.md",
                readme_template=template,
                metadata_fields=["status", "owner"],
            )

            self.assertTrue((docs / "README.md").is_file())
            self.assertTrue((docs / "index.json").is_file())
            self.assertEqual(payload["source_dir"], str(docs))
            parsed = json.loads((docs / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(parsed["files"][0]["metadata"]["status"], "Accepted")

    def test_cli_wrapper_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp) / "docs"
            docs.mkdir(parents=True)
            self._write_md(docs / "001-adr.md", "# ADR One\n")

            payload = governance_commands.update_index_cli(
                target_dir=str(docs),
                pattern="*.md",
                readme_template="# Index\n",
                dry_run=True,
            )

            self.assertIn("files", payload)
            self.assertFalse((docs / "README.md").exists())
            self.assertFalse((docs / "index.json").exists())


if __name__ == "__main__":
    unittest.main()
