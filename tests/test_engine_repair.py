import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from aaa.engine.repair import AutoFixEngine

class TestAutoFixEngine(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.engine = AutoFixEngine(max_retries=2)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_fix_success(self):
        f = self.root / "test.py"
        f.write_text("a = 1", encoding='utf-8')
        
        def good_fixer(content):
            return content.replace("1", "2")
            
        result = self.engine.apply_fix(f, good_fixer)
        self.assertTrue(result.success)
        self.assertTrue(result.changed)
        self.assertEqual(f.read_text(), "a = 2")

    def test_fix_no_change(self):
        f = self.root / "test.txt"
        f.write_text("hello", encoding='utf-8')
        
        def identity_fixer(content):
            return content
            
        result = self.engine.apply_fix(f, identity_fixer)
        self.assertTrue(result.success)
        self.assertFalse(result.changed)
        self.assertEqual(f.read_text(), "hello")

    def test_fix_rollback_on_syntax_error(self):
        f = self.root / "broken.py"
        original = "print('hello')"
        f.write_text(original, encoding='utf-8')
        
        def bad_fixer(content):
            # Introduce syntax error (missing paren)
            return "print('hello'" 
            
        result = self.engine.apply_fix(f, bad_fixer)
        self.assertFalse(result.success)
        self.assertFalse(result.changed)
        self.assertIn("Rollback applied", result.message)
        # Verify rollback
        self.assertEqual(f.read_text(), original)

    def test_fix_rollback_on_exception(self):
        f = self.root / "crash.txt"
        original = "safe"
        f.write_text(original, encoding='utf-8')
        
        def crashing_fixer(content):
            raise ValueError("Boom")
            
        result = self.engine.apply_fix(f, crashing_fixer)
        self.assertFalse(result.success)
        self.assertIn("Exception during fix", result.message)
        # Verify rollback
        self.assertEqual(f.read_text(), original)

if __name__ == '__main__':
    unittest.main()
