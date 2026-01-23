import json
import tempfile
import unittest
from pathlib import Path

from aaa.verify_ci import load_checks_manifest, validate_checks


class TestVerifyCiManifest(unittest.TestCase):
    def test_load_checks_manifest_reads_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            manifest = tmp_path / "checks.manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "checks": [
                            {
                                "id": "lint",
                                "name": "ci/lint / lint (pull_request)",
                                "applies_to": ["all"],
                            }
                        ],
                    }
                )
            )

            payload = load_checks_manifest(manifest)

            self.assertEqual(payload["checks"][0]["id"], "lint")

    def test_validate_checks_flags_missing(self):
        manifest = {
            "checks": [
                {"id": "lint", "name": "ci/lint / lint (pull_request)", "applies_to": ["all"]},
                {"id": "security", "name": "Agent safety check", "applies_to": ["agent"]},
            ]
        }
        actual = ["ci/test / test (pull_request)"]

        ok, missing = validate_checks(actual, manifest, repo_type="docs")

        self.assertIs(ok, False)
        self.assertIn("ci/lint / lint (pull_request)", missing)
        self.assertNotIn("Agent safety check", missing)


if __name__ == "__main__":
    unittest.main()
