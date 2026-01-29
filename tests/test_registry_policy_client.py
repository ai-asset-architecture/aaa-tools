import pytest
from pathlib import Path
from aaa.registry.policy_client import RegistryClient, RegistryClientError
from aaa.distribution.manifest import ManifestGenerator

@pytest.fixture
def mock_registry(tmp_path):
    root = tmp_path / "reg"
    root.mkdir()
    policies = root / "policies"
    policies.mkdir()
    
    (policies / "test" / "1.0.0").mkdir(parents=True)
    script = policies / "test" / "1.0.0" / "check_test.py"
    script.write_text("print('ok')", encoding="utf-8")
    
    # Generate manifest
    manifest = ManifestGenerator.generate(root)
    (root / "policies.json").write_text(manifest.model_dump_json(), encoding="utf-8")
    
    return root

def test_fetch_manifest_success(mock_registry):
    url = f"file://{mock_registry}"
    client = RegistryClient(url)
    manifest = client.fetch_manifest()
    assert "test" in manifest.policies

def test_download_policy_success(mock_registry, tmp_path):
    url = f"file://{mock_registry}"
    cache = tmp_path / "cache"
    client = RegistryClient(url, cache_dir=cache)
    
    path = client.download_policy("test", "1.0.0")
    assert path.exists()
    assert path.read_text() == "print('ok')"

def test_download_hash_mismatch(mock_registry, tmp_path):
    # Tamper with file after manifest generation
    script = mock_registry / "policies" / "test" / "1.0.0" / "check_test.py"
    script.write_text("print('hacked')", encoding="utf-8")
    
    url = f"file://{mock_registry}"
    client = RegistryClient(url, cache_dir=tmp_path)
    
    with pytest.raises(RegistryClientError, match="Hash mismatch"):
        client.download_policy("test", "1.0.0")

def test_policy_not_found(mock_registry):
    client = RegistryClient(f"file://{mock_registry}")
    with pytest.raises(RegistryClientError, match="Policy 'missing' not found"):
        client.get_policy_url("missing")

def test_version_not_found(mock_registry):
    client = RegistryClient(f"file://{mock_registry}")
    with pytest.raises(RegistryClientError, match="Version '9.9.9' not found"):
        client.get_policy_url("test", "9.9.9")
