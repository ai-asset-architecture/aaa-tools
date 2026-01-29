import pytest
from pathlib import Path
from aaa.os.kernel import AgentKernel

@pytest.fixture
def kernel(tmp_path):
    # Setup a mock workspace
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / ".aaa").mkdir()
    (workspace / ".aaa" / "registry").mkdir()
    # Create a dummy registry index
    (workspace / ".aaa" / "registry_index.json").write_text('{"packs": {}}')
    
    return AgentKernel(workspace_root=workspace)

def test_kernel_boot(kernel):
    status_data = kernel.boot()
    assert status_data["status"] == "ONLINE"

def test_kernel_run_safe_action(kernel):
    payload = {"action": "test"}
    result = kernel.run_safe_action("test_action", payload)
    assert result["status"] == "executed"

def test_kernel_escalate_conflict(kernel):
    case_id = kernel.escalate_conflict({"detail": "info"})
    assert case_id is not None
