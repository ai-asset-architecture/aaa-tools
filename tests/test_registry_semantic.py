import pytest
from pathlib import Path
import json
from aaa.registry.client import RegistryClient, VersionIncompatibilityError

MOCK_REGISTRY_V2 = {
    "schema_version": "2.0",
    "min_cli_version": "1.0.0",
    "object_types": {
        "service": {"display_name": "Service", "rules": ["readme"]},
        "library": {"display_name": "Library", "rules": ["versioning"]}
    },
    "packs": {
        "agent-safety": {
            "capabilities": ["prevents prompt injection", "validates tools", "security"]
        },
        "core-governance": {
            "capabilities": ["enforces readme structure", "governance"]
        },
        "data-ops": {
            "capabilities": ["manages data pipelines"]
        },
        "legacy-pack": {
            "capabilities": "invalid-list-format" # Edge case: handle bad data
        }
    }
}

@pytest.fixture
def registry_file(tmp_path):
    p = tmp_path / "registry_index.v2.json"
    with open(p, "w") as f:
        json.dump(MOCK_REGISTRY_V2, f)
    return p

def test_load_registry(registry_file):
    client = RegistryClient(registry_file)
    assert client._data["schema_version"] == "2.0"

def test_version_handshake_fail(tmp_path):
    # Mock a registry requiring a future version
    future_registry = {
        "min_cli_version": "99.9.9"
    }
    p = tmp_path / "future_registry.json"
    with open(p, "w") as f:
        json.dump(future_registry, f)
    
    with pytest.raises(VersionIncompatibilityError) as excinfo:
        RegistryClient(p)
    assert "Registry requires CLI version >= 99.9.9" in str(excinfo.value)

def test_query_semantic_id_match(registry_file):
    client = RegistryClient(registry_file)
    results = client.query_capabilities(["safety"])
    
    # "safety" is in "agent-safety" ID -> Score 5
    # "safety" is NOT in capabilities directly? Wait, let's check.
    # Actually, if I search "safety", it matches "agent-safety" (ID) and logic will add 5.
    
    assert len(results) >= 1
    top_result = results[0]
    assert top_result["pack_id"] == "agent-safety"
    assert top_result["score"] >= 5

def test_query_semantic_capability_match(registry_file):
    client = RegistryClient(registry_file)
    results = client.query_capabilities(["injection"])
    
    # "injection" in "prevents prompt injection" -> Score 1
    assert len(results) == 1
    assert results[0]["pack_id"] == "agent-safety"
    assert results[0]["score"] == 1
    assert "prevents prompt injection" in results[0]["matched_capabilities"]

def test_query_sorting(registry_file):
    client = RegistryClient(registry_file)
    # Search for "governance" which is in core-governance ID (5) and capability (1) = 6?
    # Wait, ID match "core-governance" contains "governance"? Yes.
    
    # Let's try term "readme".
    # core-governance: cap "enforces readme structure" -> 1
    # agent-safety: no match -> 0
    results = client.query_capabilities(["readme"])
    assert results[0]["pack_id"] == "core-governance"

def test_query_mixed_scoring(registry_file):
    # "data" matches "data-ops" (ID: 5) and "manages data pipelines" (Cap: 1) -> Total 6
    client = RegistryClient(registry_file)
    results = client.query_capabilities(["data"])
    assert results[0]["pack_id"] == "data-ops"
    assert results[0]["score"] >= 6

def test_get_object_type(registry_file):
    client = RegistryClient(registry_file)
    svc = client.get_object_type("service")
    assert svc is not None
    assert svc["display_name"] == "Service"
    
    assert client.get_object_type("unknown") is None

def test_legacy_format_robustness(registry_file):
    # "legacy-pack" has invalid capabilities string instead of list
    client = RegistryClient(registry_file)
    # Should not crash
    results = client.query_capabilities(["invalid"])
    # Should treat it as empty list
    matching_legacy = [r for r in results if r["pack_id"] == "legacy-pack"]
    assert len(matching_legacy) == 0
