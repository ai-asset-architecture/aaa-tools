import shutil
import tempfile
import time
from pathlib import Path
from unittest import TestCase
from aaa.engine.locking import LockManager

class TestLockManager(TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.lock_mgr = LockManager(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_acquire_lock_success(self):
        result = self.lock_mgr.acquire("README.md", "agent-1")
        self.assertTrue(result)
        
        lock_info = self.lock_mgr.check_lock("README.md")
        self.assertIsNotNone(lock_info)
        self.assertEqual(lock_info.owner, "agent-1")

    def test_acquire_lock_fail_already_locked(self):
        self.lock_mgr.acquire("README.md", "agent-1")
        result = self.lock_mgr.acquire("README.md", "agent-2")
        self.assertFalse(result)

    def test_release_lock_success(self):
        self.lock_mgr.acquire("README.md", "agent-1")
        result = self.lock_mgr.release("README.md", "agent-1")
        self.assertTrue(result)
        self.assertIsNone(self.lock_mgr.check_lock("README.md"))

    def test_release_lock_fail_wrong_owner(self):
        self.lock_mgr.acquire("README.md", "agent-1")
        result = self.lock_mgr.release("README.md", "agent-2")
        self.assertFalse(result)
        self.assertIsNotNone(self.lock_mgr.check_lock("README.md"))

    def test_auto_expiry(self):
        # Acquire with very short TTL
        # Note: time.sleep might be flaky, but for unit test ensuring logic is robust
        # Let's mock datetime? Or just rely on 0.1 min TTL?
        # Actually, passing 0 TTL or negative TTL simulates immediate expiry
        
        # Test immediate expiry (-1 min TTL)
        self.lock_mgr.acquire("stale.md", "agent-1", ttl_minutes=-1)
        
        # Should be None immediately upon check
        lock_info = self.lock_mgr.check_lock("stale.md")
        self.assertIsNone(lock_info)
        
        # Should be acquirable by someone else immediately
        result = self.lock_mgr.acquire("stale.md", "agent-2")
        self.assertTrue(result)
