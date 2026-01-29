import json
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib

class RemoteVerifier:
    """
    Verifies compliance of remote repositories.
    Implements IO-heavy logic (Network Fetch, Caching).
    """
    
    CACHE_TTL = 3600 * 24  # 24 Hours

    def __init__(self, cache_dir: Optional[Path] = None):
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = Path.home() / ".aaa" / "cache"
        self.audit_cache_dir = self.cache_dir / "remote_audits"
        self.audit_cache_dir.mkdir(parents=True, exist_ok=True)

    def verify(self, url: str) -> Dict[str, Any]:
        """
        Verify a remote repository URL.
        1. Check Cache.
        2. Fetch unique audit URL (assuming standard AAA location).
        3. Validate signature (Stub for v1.7 logic-first).
        """
        cache_key = self._get_cache_key(url)
        cached = self._read_cache(cache_key)
        if cached:
            return cached

        # Construct raw URL for the latest audit (Convention over Configuration)
        # Assuming GitHub-like URL structure for raw content:
        # User input: https://github.com/org/repo
        # Target: https://raw.githubusercontent.com/org/repo/main/aaa-tpl-docs/internal/development/audits/latest.json
        # For MVP: Just fetch the URL provided if it ends in .json, else assume convention
        
        target_url = self._resolve_target_url(url)
        
        try:
            with urllib.request.urlopen(target_url, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                
            self._write_cache(cache_key, data)
            return data
        except Exception as e:
            raise Exception(f"Failed to fetch remote audit from {target_url}: {str(e)}")

    def _resolve_target_url(self, url: str) -> str:
        """Resolve the actual raw JSON URL."""
        if url.endswith(".json"):
            return url
        
        # Simple heuristic for GitHub
        if "github.com" in url and "raw.githubusercontent.com" not in url:
            # defined convention: .aaa/audit_report.json
            return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/") + "/main/.aaa/audit_report.json"
            
        return url

    def _get_cache_key(self, url: str) -> str:
        """Generate safe filename for cache."""
        return hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json"

    def _read_cache(self, key: str) -> Optional[Dict[str, Any]]:
        path = self.audit_cache_dir / key
        if not path.exists():
            return None
            
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if time.time() - data.get("fetched_at", 0) < self.CACHE_TTL:
                return data
        except Exception:
            return None
        return None

    def _write_cache(self, key: str, data: Dict[str, Any]):
        path = self.audit_cache_dir / key
        data["fetched_at"] = time.time()
        path.write_text(json.dumps(data), encoding="utf-8")
