import pytest
import os
import tempfile
import json
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock
from aaa.engine.federation import RemoteVerifier

class TestRemoteVerifier:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_dir = Path(self.temp_dir.name) / ".aaa" / "cache"
        self.verifier = RemoteVerifier(cache_dir=self.cache_dir)
        yield
        self.temp_dir.cleanup()

    @patch("urllib.request.urlopen")
    def test_fetch_remote_audit_success(self, mock_urlopen):
        """Test successful fetching of a remote audit."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "PASS",
            "compliance_rate": 0.95
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Act
        result = self.verifier.verify("https://example.com/repo")
        
        # Assert
        assert result["status"] == "PASS"
        assert result["compliance_rate"] == 0.95
        mock_urlopen.assert_called()

    @patch("urllib.request.urlopen")
    def test_fetch_remote_audit_cache_hit(self, mock_urlopen):
        """Test that cached result is returned if fresh."""
        # Setup Cache
        url = "https://example.com/repo"
        cache_key = hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json"
        
        cache_file = self.cache_dir / "remote_audits" / cache_key
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cached_data = {
            "status": "PASS", 
            "compliance_rate": 0.99,
            "fetched_at": 9999999999  # Future timestamp
        }
        cache_file.write_text(json.dumps(cached_data))

        # Act
        result = self.verifier.verify(url)
        
        # Assert
        assert result["compliance_rate"] == 0.99
        mock_urlopen.assert_not_called()  # Should not hit network

    @patch("urllib.request.urlopen")
    def test_fetch_remote_failure(self, mock_urlopen):
        """Test graceful handling of network failure."""
        mock_urlopen.side_effect = Exception("Network Error")

        with pytest.raises(Exception, match="Failed to fetch"):
             self.verifier.verify("https://example.com/bad-repo")
