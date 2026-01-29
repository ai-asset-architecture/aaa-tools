import sqlite3
import time
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from aaa.observability.custom_metrics import MetricStore

class TestMetricStore:
    
    @pytest.fixture
    def db_path(self, tmp_path):
        return tmp_path / "test_observability.db"

    def test_init_creates_db_and_metadata(self, db_path):
        store = MetricStore(db_path=db_path)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check metadata
        cursor.execute("SELECT value FROM metadata WHERE key='schema_version'")
        assert cursor.fetchone()[0] == "1"
        
        # Check metrics table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metrics'")
        assert cursor.fetchone() is not None
        conn.close()

    def test_record_metric(self, db_path):
        store = MetricStore(db_path=db_path)
        store.record("test_metric", 42.0, tags={"env": "prod"})
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT metric_name, value, tags FROM metrics")
        row = cursor.fetchone()
        
        assert row[0] == "test_metric"
        assert row[1] == 42.0
        assert json.loads(row[2]) == {"env": "prod"}
        conn.close()

    def test_auto_prune_retention(self, db_path):
        """Verify data older than 90 days is deleted on init."""
        # 1. Manually insert old data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS metrics (timestamp REAL, metric_name TEXT, value REAL, tags TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT)")
        
        old_time = time.time() - (91 * 24 * 3600)  # 91 days ago
        recent_time = time.time()
        
        cursor.execute("INSERT INTO metrics VALUES (?, 'old_metric', 1, '{}')", (old_time,))
        cursor.execute("INSERT INTO metrics VALUES (?, 'new_metric', 1, '{}')", (recent_time,))
        conn.commit()
        conn.close()
        
        # 2. Init MetricStore (should trigger prune)
        store = MetricStore(db_path=db_path)
        
        # 3. Verify
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT metric_name FROM metrics")
        rows = cursor.fetchall()
        
        names = [r[0] for r in rows]
        assert "new_metric" in names
        assert "old_metric" not in names
        conn.close()
