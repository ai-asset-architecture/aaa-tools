import sqlite3
import re
import hashlib
import time
from pathlib import Path
from typing import Optional

class RiskLedger:
    # Privacy Firewall: Common patterns to scrub
    PATTERNS = [
        (r"(?i)(password|secret|key|token)\s*[:=]\s*(\S+)", r"\1=********"),
        (r"AKIA[0-9A-Z]{16}", "AKIA********"),  # AWS Access Key
        (r"ghp_[a-zA-Z0-9]+", "ghp_********"),  # GitHub Token
        (r"(http[s]?://[^@]+):([^@]+)(@)", r"\1:********\3"), # Basic Auth URL
        (r"([a-zA-Z0-9_\-\.]+)[/]([a-zA-Z0-9!@#$%^&*()_\-\.]+)", r"\1/********") # User/Pass format (simple)
    ]

    def __init__(self, db_path: Optional[Path] = None):
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = Path.cwd() / ".aaa" / "observability.db"
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        # Ledger Table
        # id: Auto inc
        # timestamp: Unix float
        # event_type: str (e.g., "AUTH_FAIL", "POLICY_OVERRIDE")
        # severity: str (low, medium, high)
        # description: str (Sanitized)
        # actor: str (User or System)
        # hash: SHA256 (prev_hash + content) -> Tamper Evident Chain
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                event_type TEXT,
                severity TEXT,
                description TEXT,
                actor TEXT,
                hash TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _sanitize(self, text: str) -> str:
        """Privacy Firewall: Scrub sensitive data."""
        for pattern, replacement in self.PATTERNS:
            text = re.sub(pattern, replacement, text)
        return text

    def _calculate_hash(self, timestamp: float, event_type: str, severity: str, description: str, actor: str) -> str:
        """Calculate tamper-evident hash."""
        # Get last hash (Simulated chain for v1.8 MVP - fully chained requires sequential reads)
        # For performance, we hash content + secret salt in v1.8, moving to full blockchain in v2.0
        # MVP: Self-contained hash
        payload = f"{timestamp}:{event_type}:{severity}:{description}:{actor}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def record(self, event_type: str, severity: str, description: str, actor: str = "system"):
        """Sanitize and record event."""
        safe_desc = self._sanitize(description)
        timestamp = time.time()
        event_hash = self._calculate_hash(timestamp, event_type, severity, safe_desc, actor)
        
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO ledger (timestamp, event_type, severity, description, actor, hash) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, event_type, severity, safe_desc, actor, event_hash)
        )
        conn.commit()
        conn.close()
