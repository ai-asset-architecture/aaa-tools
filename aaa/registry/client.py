import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from packaging import version
import sys

# Assume these are available in the package distribution, or passed in config
CURRENT_CLI_VERSION = "2.0.0" 

logger = logging.getLogger(__name__)

class RegistryClientError(Exception):
    pass

class VersionIncompatibilityError(RegistryClientError):
    pass

class RegistryClient:
    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self._data: Dict[str, Any] = {}
        self._schema_version: str = "1.0"
        self.load()

    def load(self):
        if not self.registry_path.exists():
            raise RegistryClientError(f"Registry file not found at {self.registry_path}")
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except json.JSONDecodeError as e:
            raise RegistryClientError(f"Invalid JSON in registry file: {e}")

        # Version Handshake
        self._check_version_compatibility()

    def _check_version_compatibility(self):
        """
        Implements the Fail Fast Version Handshake.
        """
        min_cli_version = self._data.get("min_cli_version")
        self._schema_version = self._data.get("schema_version", "1.0")

        if min_cli_version:
            if version.parse(CURRENT_CLI_VERSION) < version.parse(min_cli_version):
                error_msg = (
                    f"CRITICAL: Registry requires CLI version >= {min_cli_version}, "
                    f"but you are running {CURRENT_CLI_VERSION}.\n"
                    f"Please upgrade aaa-tools: pip install --upgrade aaa-tools"
                )
                logger.error(error_msg)
                raise VersionIncompatibilityError(error_msg)

    def get_packs(self) -> Dict[str, Any]:
        """Returns the raw packs dictionary."""
        return self._data.get("packs", {})

    def query_capabilities(self, query_terms: List[str]) -> List[Dict[str, Any]]:
        """
        Basic semantic query implementation.
        In v1.2 this is keyword-based; v1.5 will introduce embeddings.
        """
        results = []
        packs = self.get_packs()
        
        query_terms = [t.lower() for t in query_terms]

        for pack_id, pack_data in packs.items():
            capabilities = pack_data.get("capabilities", [])
            # If v1 schema, capabilities might not exist or be different
            if not isinstance(capabilities, list):
                capabilities = []
            
            # Simple keyword matching score
            score = 0
            matched_caps = []
            
            # Search in capabilities
            for cap in capabilities:
                cap_lower = cap.lower()
                for term in query_terms:
                    if term in cap_lower:
                        score += 1
                        matched_caps.append(cap)
            
            # Search in pack_id (heuristic)
            pack_id_lower = pack_id.lower()
            for term in query_terms:
                if term in pack_id_lower:
                    score += 5 # Higher weight for ID match
                    matched_caps.append(f"ID: {pack_id}")
            
            # Search in description if available (v2 pack model) or fallbacks
            # ... (omitted for brevity)

            if score > 0:
                results.append({
                    "pack_id": pack_id,
                    "score": score,
                    "matched_capabilities": matched_caps,
                    "pack_data": pack_data
                })
        
        # Sort by score desc
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def get_object_type(self, type_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves Object Type definition (v2 only)."""
        object_types = self._data.get("object_types", {})
        return object_types.get(type_name)
