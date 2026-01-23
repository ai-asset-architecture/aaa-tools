import json
import tempfile
import unittest
from pathlib import Path

from aaa.verify_ci import load_checks_manifest


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


if __name__ == "__main__":
    unittest.main()
