import json
import tempfile
import unittest
from pathlib import Path

from aaa import governance_index


class TestGovernanceUpdateIndex(unittest.TestCase):
    def _write_md(self, path: Path, content: str) -> None:
        path.write_text(content, encoding="utf-8")

    def test_generates_index_and_readme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs" / "adrs"
            docs.mkdir(parents=True)

            self._write_md(
                docs / "001-foo.md",
                """---
""" +
                "title: Foo ADR\nstatus: Accepted\nowner: @architect\ntags: [architecture, v0.5]\ndate: 2026-01-21\n" +
                "---\n\n# Foo ADR\n" ,
            )
            self._write_md(
                docs / "002-bar.md",
                "# Bar ADR\n\nBody\n",
            )

            template = """# ADR Index

{{ range files }}
- {{ .Path }} | {{ .Title }} | {{ .Metadata.status }} | {{ .Metadata.owner }}
{{ end }}
"""

            index = governance_index.update_index(
                target_dir=docs,
                pattern="*.md",
                readme_template=template,
                index_output="index.json",
                metadata_fields=["status", "owner", "tags"],
            )

            readme = (docs / "README.md").read_text(encoding="utf-8")
            self.assertIn("001-foo.md", readme)
            self.assertIn("Foo ADR", readme)
            self.assertIn("Accepted", readme)
            self.assertTrue((docs / "index.json").is_file())

            payload = json.loads((docs / "index.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["source_dir"], str(docs))
            self.assertEqual(payload["hash_algo"], "sha256")
            self.assertEqual(len(payload["files"]), 2)
            first = payload["files"][0]
            self.assertIn("path", first)
            self.assertIn("metadata", first)

    def test_fails_when_no_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            docs = root / "docs" / "adrs"
            docs.mkdir(parents=True)
            with self.assertRaises(ValueError):
                governance_index.update_index(
                    target_dir=docs,
                    pattern="*.md",
                    readme_template="# Index\n",
                    index_output="index.json",
                    metadata_fields=["status"],
                )


if __name__ == "__main__":
    unittest.main()
