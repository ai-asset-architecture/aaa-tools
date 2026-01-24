import json
import tempfile
import unittest
from pathlib import Path

from aaa.utils import version_check


class TestVersionCheck(unittest.TestCase):
    def test_update_hint_when_remote_newer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"
            result = version_check.check_for_update(
                now=1_700_000_000.0,
                cache_path=cache_path,
                local_version="1.0.0",
                fetch_remote=lambda: version_check.UpdateResult(
                    local_version="1.0.0",
                    remote_version="1.1.0",
                    release_url="https://example.com",
                    source="test",
                ),
            )
            self.assertIn("Update available 1.0.0", result or "")

    def test_no_hint_when_up_to_date(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"
            result = version_check.check_for_update(
                now=1_700_000_000.0,
                cache_path=cache_path,
                local_version="1.1.0",
                fetch_remote=lambda: version_check.UpdateResult(
                    local_version="1.1.0",
                    remote_version="1.1.0",
                    release_url="",
                    source="test",
                ),
            )
            self.assertIsNone(result)

    def test_cache_reuse(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            cache_path = Path(temp_dir) / "cache.json"
            cached = {
                "checked_at": 1_700_000_000.0,
                "local_version": "1.0.0",
                "remote_version": "1.2.0",
                "release_url": "https://example.com",
                "source": "cache",
            }
            cache_path.write_text(json.dumps(cached), encoding="utf-8")
            called = {"value": False}

            def fetch_remote():
                called["value"] = True
                return None

            result = version_check.check_for_update(
                now=1_700_000_100.0,
                cache_path=cache_path,
                local_version="1.0.0",
                fetch_remote=fetch_remote,
            )
            self.assertFalse(called["value"])
            self.assertIn("Update available", result or "")


if __name__ == "__main__":
    unittest.main()
