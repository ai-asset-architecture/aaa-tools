import json
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

LOCKS_FILE = Path(".aaa/locks.json")
DEFAULT_TTL_MINUTES = 5

@dataclass
class LockInfo:
    owner: str
    acquired_at: str
    expires_at: str

class LockManager:
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.locks_file = workspace_root / LOCKS_FILE
        self._ensure_locks_file()

    def _ensure_locks_file(self):
        if not self.locks_file.parent.exists():
            self.locks_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.locks_file.exists():
            self._write_locks({})

    def _read_locks(self) -> Dict[str, dict]:
        try:
            content = self.locks_file.read_text(encoding="utf-8")
            return json.loads(content).get("locks", {})
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_locks(self, locks: Dict[str, dict]):
        data = {"locks": locks}
        self.locks_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _clean_stale_locks(self, locks: Dict[str, dict]) -> Dict[str, dict]:
        """Remove locks that have expired."""
        now = datetime.now(timezone.utc)
        active_locks = {}
        for path, info in locks.items():
            expires_at = datetime.fromisoformat(info["expires_at"])
            if now < expires_at:
                active_locks[path] = info
        return active_locks

    def acquire(self, rel_path: str, owner: str, ttl_minutes: int = DEFAULT_TTL_MINUTES) -> bool:
        """Attempt to acquire a lock on a file."""
        locks = self._read_locks()
        locks = self._clean_stale_locks(locks) # Auto-cleanup before acquiring logic

        if rel_path in locks:
            # Already locked by someone else (or same owner, but we strictly block re-acquire for simplicity now)
            return False

        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=ttl_minutes)
        
        lock_info = LockInfo(
            owner=owner,
            acquired_at=now.isoformat(),
            expires_at=expires.isoformat()
        )
        
        locks[rel_path] = asdict(lock_info)
        self._write_locks(locks)
        return True

    def release(self, rel_path: str, owner: str) -> bool:
        """Release a lock if owned by the caller."""
        locks = self._read_locks()
        # Note: We don't clean stale locks here immediately to allow explicit release logic to work normally, 
        # but technically stale locks are already invalid.
        
        if rel_path not in locks:
            return False # Not locked
            
        if locks[rel_path]["owner"] != owner:
            return False # Not your lock
            
        del locks[rel_path]
        self._write_locks(locks)
        return True

    @contextmanager
    def lock(self, rel_path: str, owner: str, ttl_minutes: int = DEFAULT_TTL_MINUTES):
        """Context manager for acquiring and releasing a lock."""
        acquired = self.acquire(rel_path, owner, ttl_minutes)
        if not acquired:
            raise RuntimeError(f"Could not acquire lock on {rel_path} for {owner}")
        try:
            yield
        finally:
            self.release(rel_path, owner)

    def check_lock(self, rel_path: str) -> Optional[LockInfo]:
        """Check if a file is active locked. Returns None if free."""
        locks = self._read_locks()
        locks = self._clean_stale_locks(locks) # Clean on read
        
        # If we cleaned it, write back? Ideally yes to keep file clean.
        # But for read operation safety, maybe just return cleaned view.
        # Let's perform lazy write-back if cleanup happened? 
        # For simplicity in v1, just read-clean-return. The acquire/release cycle handles writes.
        
        if rel_path in locks:
            data = locks[rel_path]
            return LockInfo(**data)
        return None

    def clear_all(self):
        """Emergency clear all locks."""
        self._write_locks({})
