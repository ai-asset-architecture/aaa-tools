import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from aaa import mcp_server
from aaa import output_formatter

def test_mcp_aaa_check():
    with patch("aaa.check_commands.run_blocking_check") as mock_check:
        mock_check.return_value = {"status": "success", "errors": []}
        result = mcp_server.aaa_check(".")
        assert "SUCCESS" in result["report"] or "HEALTHY" in result["report"]
        assert "post_init_required" in result

def test_mcp_aaa_audit():
    with patch("aaa.audit_commands.run_local_audit") as mock_audit:
        mock_audit.return_value = {"status": "success", "artifacts": []}
        result = mcp_server.aaa_audit(".")
        assert "SUCCESS" in result["report"]
        assert "post_init_required" in result

def test_mcp_aaa_check_includes_hint_on_failure():
    with patch("aaa.check_commands.run_blocking_check") as mock_check:
        mock_check.return_value = {"status": "failure", "errors": ["check_failed:readme"]}
        result = mcp_server.aaa_check(".")
        assert "post_init_required" in result

def test_mcp_aaa_audit_includes_hint_on_failure():
    with patch("aaa.audit_commands.run_local_audit") as mock_audit:
        mock_audit.return_value = {"status": "failure", "errors": ["runner"]}
        result = mcp_server.aaa_audit(".")
        assert "post_init_required" in result

def test_llm_formatter_does_not_include_mcp_fields():
    semantic = output_formatter.SemanticResult(status="success", command="check", violations=[])
    text = output_formatter.get_formatter("llm").format(semantic)
    assert "post_init_required" not in text
