import pytest
import logging
from pathlib import Path
from unittest.mock import MagicMock
from aaa.runbook_runtime import (
    execute_runbook,
    _render_template,
    _resolve_safe_path,
    _fs_write,
    _fs_update_frontmatter,
    _parse_frontmatter
)
from aaa.action_registry import ActionRegistry, RuntimeSecurityError

def test_render_template_simple():
    inputs = {"name": "World", "version": "1.0"}
    steps = []
    
    assert _render_template("Hello {{ inputs.name }}", inputs, steps) == "Hello World"
    assert _render_template("v{{ inputs.version }}", inputs, steps) == "v1.0"
    assert _render_template("No vars", inputs, steps) == "No vars"

def test_execute_runbook_flow():
    # Mock registry
    registry = MagicMock(spec=ActionRegistry)
    registry.execute.return_value = {"status": "ok"}
    
    runbook = {
        "steps": [
            {
                "name": "step1",
                "action": "test.action",
                "args": {"msg": "Hello {{ inputs.user }}"}
            }
        ]
    }
    inputs = {"user": "Alice"}
    
    result = execute_runbook(runbook, inputs, registry=registry)
    
    registry.execute.assert_called_once()
    args_call = registry.execute.call_args[0][1]
    assert args_call["msg"] == "Hello Alice"
    
    assert len(result["steps"]) == 1
    assert result["steps"][0]["output"] == {"status": "ok"}

def test_fs_write_safe(tmp_path):
    # Test writing to a safe path
    target = tmp_path / "test.txt"
    args = {"path": str(target), "content": "Hello FS"}
    
    # We need to monkeypatch cwd if _resolve_safe_path checks relative to cwd
    # But _resolve_safe_path uses Path.cwd(). If logic allows absolute paths inside cwd?
    # Let's verify _resolve_safe_path logic.
    # It allows absolute path if it is inside base (cwd).
    
    # Since tmp_path is likely usually outside cwd, this might fail safe check unless we mock cwd.
    pass

def test_resolve_safe_path_security(monkeypatch, tmp_path):
    # Mock CWD to be tmp_path
    monkeypatch.chdir(tmp_path)
    
    # 1. Safe relative path
    safe = _resolve_safe_path("foo/bar.txt")
    assert safe == tmp_path / "foo/bar.txt"
    
    # 2. Path Traversal
    with pytest.raises(RuntimeSecurityError):
        _resolve_safe_path("../secret.txt")
        
    # 3. Absolute path outside
    with pytest.raises(RuntimeSecurityError):
        _resolve_safe_path("/etc/passwd")

def test_parse_frontmatter_logic():
    content = """---
key: value
title: Test
---
Body content"""
    meta, body = _parse_frontmatter(content)
    assert meta["key"] == "value"
    assert meta["title"] == "Test"
    assert body == "Body content"

@pytest.fixture
def mock_resolve_safe_path(monkeypatch):
    def mock_resolve(path):
        return Path(path)
    monkeypatch.setattr("aaa.runbook_runtime._resolve_safe_path", mock_resolve)


def test_fs_update_frontmatter_action(tmp_path):
    # Create valid markdown file
    p = tmp_path / "doc.md"
    p.write_text("---\nstatus: draft\n---\nHello", encoding="utf-8")
    
    # Prepare args. Usually args is dict or list. command line args are list?
    # Function supports both. Let's use dict for unit testing internal logic.
    args = {
        "path": str(p),
        "set": {"status": "published", "author": "bot"}
    }
    
    _fs_update_frontmatter(args)
    
    new_content = p.read_text(encoding="utf-8")
    assert "status: published" in new_content
    assert "author: bot" in new_content
    assert "Hello" in new_content

def test_fs_update_frontmatter_list_args(tmp_path):
    p = tmp_path / "doc_cli.md"
    p.write_text("---\nver: 1\n---\n", encoding="utf-8")
    
    args = ["path", str(p), "set", "ver=2", "reviewed=true"]
    _fs_update_frontmatter(args)
    
    new_content = p.read_text(encoding="utf-8")
    assert "ver: 2" in new_content
    assert "reviewed: true" in new_content

def test_milestone_actions_mock(monkeypatch):
    # Mock milestone_manager
    mock_mgr = MagicMock()
    monkeypatch.setattr("aaa.runbook_runtime.milestone_manager", mock_mgr)
    
    from aaa.runbook_runtime import _milestone_init, _milestone_complete
    
    # Test Init
    _milestone_init({"id": "v1.0", "workspace_root": "/tmp"})
    mock_mgr.init_milestone.assert_called_with("v1.0", Path("/tmp"))
    
    # Test Complete
    _milestone_complete({"milestone_id": "v1.0"})  # Test alias
    mock_mgr.complete_milestone.assert_called_with("v1.0", Path.cwd())

def test_cli_wrappers_mock(monkeypatch):
    # Mock subprocess.run
    mock_run = MagicMock()
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "ok"
    mock_run.return_value.stderr = ""
    monkeypatch.setattr("subprocess.run", mock_run)
    
    from aaa.runbook_runtime import _aaa_cli, _gh_cli
    
    # Test aaa_cli
    res = _aaa_cli(["check", "--mode=blocking"])
    assert res["returncode"] == 0
    assert "aaa.cli" in mock_run.call_args[0][0] # Command list check
    
    # Test gh_cli
    res = _gh_cli(["pr", "list"])
    assert res["stdout"] == "ok"
    assert mock_run.call_args[0][0][0] == "gh"

def test_fs_write_safe(tmp_path, mock_resolve_safe_path):
    target = tmp_path / "test.txt"
    args = {"path": str(target), "content": "Hello FS"}
    
    from aaa.runbook_runtime import _fs_write
    
    res = _fs_write(args)
    assert res["path"] == str(target)
    assert target.read_text(encoding="utf-8") == "Hello FS"

def test_notify_stdout(capsys):
    from aaa.runbook_runtime import _notify_stdout
    res = _notify_stdout({"message": "Alert"})
    assert res["message"] == "Alert"
    captured = capsys.readouterr()
    assert ' "message": "Alert"' in captured.out

def test_default_registry():
    from aaa.runbook_runtime import _default_registry
    reg = _default_registry()
    assert "fs_write" in reg._actions
    assert "notify" in reg._actions
    assert "milestone.init" in reg._actions

def test_governance_update_index_mock(monkeypatch):
    mock_update = MagicMock(return_value={"count": 1})
    monkeypatch.setattr("aaa.runbook_runtime.governance_index.update_index", mock_update)
    
    from aaa.runbook_runtime import _governance_update_index
    args = ["--target-dir", "docs", "--pattern", "*.md"]
    res = _governance_update_index(args)
    
    mock_update.assert_called_once()
    assert res["payload"]["count"] == 1
    call_kwargs = mock_update.call_args[1]
    assert call_kwargs["target_dir"] == "docs"
    assert call_kwargs["pattern"] == "*.md"

def test_aaa_evals_run_mock(monkeypatch):
    mock_run = MagicMock()
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "eval ok"
    monkeypatch.setattr("subprocess.run", mock_run)
    
    from aaa.runbook_runtime import _aaa_evals_run
    res = _aaa_evals_run({"suite": "security"})
    assert res["stdout"] == "eval ok"
    cmd = mock_run.call_args[0][0]
    assert "aaa.cli" in cmd
    assert "eval" in cmd
    assert "security" in cmd

# Helper fixture for mocking resolve
@pytest.fixture
def mock_resolve(monkeypatch):
    pass
    # Need to register this properly or just use context manager inside test


