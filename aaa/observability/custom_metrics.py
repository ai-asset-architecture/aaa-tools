import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

class MetricStore:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path:
            self.db_path = db_path
        else:
            # Default to .aaa/observability.db
            self.db_path = Path.cwd() / ".aaa" / "observability.db"
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
        self._init_db()
        self._auto_prune()

    def _init_db(self):
        """Initialize DB tables and schema version."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Metadata Schema Table
        cursor.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        
        # 2. Check/Set Schema Version
        cursor.execute("SELECT value FROM metadata WHERE key='schema_version'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO metadata (key, value) VALUES ('schema_version', '1')")
            
        # 3. Metrics Table
        # timestamp: Unix float
        # metric_name: str
        # value: float
        # tags: JSON string
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                timestamp REAL,
                metric_name TEXT,
                value REAL,
                tags TEXT
            )
        """)
        # Index for faster range queries (retention & plotting)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON metrics(timestamp)")
        
        conn.commit()
        conn.close()

    def _auto_prune(self, days: int = 90):
        """Data Retention Policy: Delete data older than X days."""
        cutoff = time.time() - (days * 24 * 3600)
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff,))
        conn.commit()
        conn.close()

    def record(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record a metric point."""
        if tags is None:
            tags = {}
            
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO metrics (timestamp, metric_name, value, tags) VALUES (?, ?, ?, ?)",
            (time.time(), metric_name, value, json.dumps(tags))
        )
        conn.commit()
        conn.close()
