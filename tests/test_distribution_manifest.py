import pytest
import json
from pathlib import Path
from aaa.distribution.manifest import ManifestGenerator

def test_manifest_generation_snapshot(tmp_path):
    # Setup Mock Registry Structure
    root = tmp_path / "registry"
    policies_dir = root / "policies"
    policies_dir.mkdir(parents=True)
    
    # Policy 1: safety (v1.0.0, v1.1.0)
    (policies_dir / "safety" / "1.0.0").mkdir(parents=True)
    (policies_dir / "safety" / "1.1.0").mkdir(parents=True)
    
    # Create dummy check scripts
    p1_v1 = policies_dir / "safety" / "1.0.0" / "check_safety.py"
    p1_v1.write_text("print('v1')", encoding='utf-8')
    
    p1_v2 = policies_dir / "safety" / "1.1.0" / "check_safety.py"
    p1_v2.write_text("print('v2')", encoding='utf-8')
    
    # Policy 2: security (v2.0.0)
    (policies_dir / "security" / "2.0.0").mkdir(parents=True)
    p2_v1 = policies_dir / "security" / "2.0.0" / "check_security.py"
    p2_v1.write_text("print('sec')", encoding='utf-8')
    
    # Generate Manifest
    manifest = ManifestGenerator.generate(root)
    
    # Verification
    # 1. Structure
    assert "safety" in manifest.policies
    assert "security" in manifest.policies
    
    # 2. Versions
    safety = manifest.policies["safety"]
    assert "1.0.0" in safety.versions
    assert "1.1.0" in safety.versions
    assert safety.latest == "1.1.0"
    
    # 3. Hashes
    # sha256 of "print('v1')"
    # echo -n "print('v1')" | shasum -a 256
    # 86d4...
    # Let's verify expected hash calculation consistency
    expected_hash_v1 = "sha256:64865337ce1f39669f27b60dbc887254cfee37f927548270d2b05357b36193b3"
    assert safety.versions["1.0.0"].hash == expected_hash_v1
    
    # 4. URL
    assert safety.versions["1.0.0"].url == "policies/safety/1.0.0/check_safety.py"
    
    # 5. Missing Scripts should be ignored
    (policies_dir / "broken" / "1.0.0").mkdir(parents=True)
    # No script created
    manifest_broken = ManifestGenerator.generate(root)
    assert "broken" not in manifest_broken.policies

def test_empty_registry(tmp_path):
    manifest = ManifestGenerator.generate(tmp_path)
    assert manifest.policies == {}
    assert manifest.registry_version == "1.0"
