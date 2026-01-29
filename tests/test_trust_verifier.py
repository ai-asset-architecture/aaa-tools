import pytest
from aaa.trust.verifier import TrustVerifier

@pytest.fixture
def verifier(tmp_path):
    return TrustVerifier(trust_store=tmp_path)

def test_verify_remote_repo(verifier):
    # Mock behavior for now
    result = verifier.verify_repo("ai-asset-architecture/aaa-tools", "SIG-123")
    assert result is True

def test_get_certification_status(verifier, tmp_path):
    # Create a mock workspace
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / ".aaa").mkdir()
    
    status = verifier.get_certification_status(workspace)
    assert status["tier"] == "Bronze"
