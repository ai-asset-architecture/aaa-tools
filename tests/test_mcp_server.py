import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from aaa import mcp_server

def test_mcp_aaa_check():
    with patch("aaa.check_commands.run_blocking_check") as mock_check:
        mock_check.return_value = {"status": "success", "errors": []}
        result = mcp_server.aaa_check(".")
        assert "SUCCESS" in result or "HEALTHY" in result

def test_mcp_aaa_audit():
    with patch("aaa.audit_commands.run_local_audit") as mock_audit:
        mock_audit.return_value = {"status": "success", "artifacts": []}
        result = mcp_server.aaa_audit(".")
        assert "SUCCESS" in result
