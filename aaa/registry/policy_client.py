import hashlib
import json
import os
from pathlib import Path
from typing import Optional, Dict
from pydantic import ValidationError
from ..distribution.manifest import RegistryManifest, PolicyEntry

class RegistryClientError(Exception):
    pass

class RegistryClient:
    """
    Zone One Component: Fetches and verifies policies.
    Target Coverage: 95%
    """
    def __init__(self, registry_url: str, cache_dir: Optional[Path] = None):
        self.registry_url = registry_url.rstrip('/')
        self.cache_dir = cache_dir or Path.home() / ".aaa" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest: Optional[RegistryManifest] = None

    def fetch_manifest(self) -> RegistryManifest:
        """Fetch policies.json from registry."""
        # TODO: Implement HTTP fetch (using requests/httpx if available, or error)
        # For now, support local file protocol for testing or direct file access
        if self.registry_url.startswith("file://"):
            try:
                path = Path(self.registry_url.replace("file://", "")) / "policies.json"
                content = path.read_text(encoding="utf-8")
                self.manifest = RegistryManifest.model_validate_json(content)
                return self.manifest
            except Exception as e:
                raise RegistryClientError(f"Failed to load local manifest: {e}")
        else:
            raise RegistryClientError("Only file:// protocol supported in MVP")

    def get_policy_url(self, policy_id: str, version: Optional[str] = None) -> str:
        if not self.manifest:
            self.fetch_manifest()
            
        if policy_id not in self.manifest.policies:
            raise RegistryClientError(f"Policy '{policy_id}' not found")
            
        entry = self.manifest.policies[policy_id]
        if not version:
            version = entry.latest
            
        if version not in entry.versions:
            raise RegistryClientError(f"Version '{version}' not found for policy '{policy_id}'")
            
        return entry.versions[version].url

    def get_policy_hash(self, policy_id: str, version: str) -> str:
         if not self.manifest: self.fetch_manifest()
         return self.manifest.policies[policy_id].versions[version].hash

    def download_policy(self, policy_id: str, version: Optional[str] = None) -> Path:
        """Downloads signed policy script and verifies hash."""
        if not self.manifest:
            self.fetch_manifest()
            
        if not version:
            version = self.manifest.policies[policy_id].latest
            
        rel_url = self.get_policy_url(policy_id, version)
        expected_hash = self.get_policy_hash(policy_id, version)
        
        # Local protocol logic
        if self.registry_url.startswith("file://"):
           base_path = Path(self.registry_url.replace("file://", ""))
           src_path = base_path / rel_url
           
           if not src_path.exists():
               raise RegistryClientError(f"Remote file not found: {src_path}")
               
           content = src_path.read_bytes()
        else:
            raise RegistryClientError("HTTP download not implemented yet")
            
        # Verify Hash
        if not self._verify_hash(content, expected_hash):
             raise RegistryClientError(f"Hash mismatch for {policy_id}@{version}")
             
        # Save to Cache
        dest_path = self.cache_dir / f"{policy_id}_{version}.py"
        dest_path.write_bytes(content)
        return dest_path

    def _verify_hash(self, content: bytes, expected: str) -> bool:
        algo, hash_val = expected.split(':')
        if algo != 'sha256':
            return False # Only support sha256 for now
            
        calc = hashlib.sha256(content).hexdigest()
        return calc == hash_val
