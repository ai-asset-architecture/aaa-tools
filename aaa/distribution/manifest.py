import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class PolicyVersion(BaseModel):
    url: str
    hash: str
    dependencies: list[str] = Field(default_factory=list)

class PolicyEntry(BaseModel):
    versions: Dict[str, PolicyVersion]
    latest: str

class RegistryManifest(BaseModel):
    last_updated: str
    registry_version: str = "1.0"
    policies: Dict[str, PolicyEntry]

class ManifestGenerator:
    """
    Zone Zero Component: Generates the policies.json manifest.
    Target Coverage: 100%
    """
    
    @staticmethod
    def generate(root_dir: Path) -> RegistryManifest:
        policies_dir = root_dir / "policies"
        if not policies_dir.exists():
            return RegistryManifest(
                last_updated=datetime.now(timezone.utc).isoformat(),
                policies={}
            )
            
        policies_map = {}
        
        # Walk policies/ directory
        # Structure: policies/<id>/<version>/check_<id>.py
        for policy_id_path in policies_dir.iterdir():
            if not policy_id_path.is_dir() or policy_id_path.name.startswith('.'):
                continue
                
            policy_id = policy_id_path.name
            versions_map = {}
            versions = []
            
            for version_path in policy_id_path.iterdir():
                if not version_path.is_dir() or version_path.name.startswith('.'):
                    continue
                    
                version = version_path.name
                # Check for compiled script
                script_name = f"check_{policy_id.replace('-', '_')}.py"
                script_path = version_path / script_name
                
                if not script_path.exists():
                    # Fallback or Skip? For Zone Zero, we skip invalid entries to ensure stability
                    continue
                    
                # Calculate Hash
                file_hash = ManifestGenerator._calculate_hash(script_path)
                rel_path = script_path.relative_to(root_dir).as_posix()
                
                versions_map[version] = PolicyVersion(
                    url=rel_path,
                    hash=f"sha256:{file_hash}"
                )
                versions.append(version)
            
            if versions:
                # Simple semantic version sort (naive implementation for now, assuming strictly X.Y.Z)
                # For robustness, we could use semver lib, but let's keep dependencies low for Zone Zero if possible
                # or just string sort if format is consistent.
                versions.sort(key=lambda s: list(map(int, s.split('.'))) if all(p.isdigit() for p in s.split('.')) else s)
                latest = versions[-1]
                
                policies_map[policy_id] = PolicyEntry(
                    versions=versions_map,
                    latest=latest
                )
                
        return RegistryManifest(
            last_updated=datetime.now(timezone.utc).isoformat(),
            policies=policies_map
        )

    @staticmethod
    def _calculate_hash(path: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
