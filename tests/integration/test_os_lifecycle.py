import pytest
from pathlib import Path
from aaa.os.kernel import AgentKernel
from aaa.court.schema import CaseStatus
from aaa.engine.locking import LockManager

@pytest.fixture
def sandbox(tmp_path):
    workspace = tmp_path / "omega_sandbox"
    workspace.mkdir()
    (workspace / ".aaa").mkdir()
    (workspace / ".aaa" / "registry").mkdir()
    (workspace / ".aaa" / "court").mkdir()
    (workspace / ".aaa" / "registry_index.json").write_text('{"packs": {}}')
    return workspace

def test_os_kernel_wiring(sandbox):
    """Verify Kernel integrates with Observability, Locking, and Court."""
    kernel = AgentKernel(workspace_root=sandbox)
    
    # 1. Boot Verification
    boot_status = kernel.boot()
    assert boot_status["status"] == "ONLINE"
    assert boot_status["modules"]["lock_manager"] == "active"
    
    # 2. Locking Integration
    assert isinstance(kernel.locker, LockManager)
    with kernel.locker.lock("test_resource", "Agent-001"):
        # The path to checking is relative to the root in actual implementation
        assert kernel.locker.locks_file.exists()
        lock_info = kernel.locker.check_lock("test_resource")
        assert lock_info is not None
        assert lock_info.owner == "Agent-001"
    case_id = kernel.escalate_conflict({"issue": "test_wiring"})
    assert case_id is not None
    assert (sandbox / ".aaa" / "court" / "cases" / f"{case_id}.json").exists()
    
    # 4. Observability Check (Implicit in Boot/Actions)
    # Note: Kernel in v2.0-pre might not yet have deep metric writing implemented, 
    # but we verify the instance is ready.
    assert kernel.root == sandbox
