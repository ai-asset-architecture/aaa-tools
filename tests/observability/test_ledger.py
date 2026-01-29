import sqlite3
import pytest
from pathlib import Path
from aaa.observability.ledger import RiskLedger

class TestRiskLedger:
    @pytest.fixture
    def db_path(self, tmp_path):
        return tmp_path / "test_observability.db"

    def test_privacy_firewall_scrubber(self, db_path):
        """Verify secrets are sanitized before writing to disk."""
        ledger = RiskLedger(db_path=db_path)
        
        # Sensitive Data (AKIA + 16 chars = 20 total)
        sensitive_msg = "Connection failed for user admin/P@ssw0rd123! and key AKIA1234567890123456"
        ledger.record("AUTH_FAIL", "high", sensitive_msg, actor="system")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT description FROM ledger")
        stored_msg = cursor.fetchone()[0]
        
        # Assertions
        assert "P@ssw0rd123!" not in stored_msg
        assert "admin/********" in stored_msg
        assert "AKIA********" in stored_msg
        conn.close()
        
    def test_ledger_hashing(self, db_path):
        """Verify each record has a hash."""
        ledger = RiskLedger(db_path=db_path)
        ledger.record("EVENT_1", "low", "desc", "actor")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM ledger")
        row = cursor.fetchone()
        
        assert row[0] is not None
        assert len(row[0]) == 64  # SHA256 hex digest length
        conn.close()
