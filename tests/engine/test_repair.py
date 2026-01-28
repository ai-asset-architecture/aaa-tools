import unittest
import tempfile
from pathlib import Path
from aaa.engine.repair import AutoFixEngine

class TestAutoFixEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AutoFixEngine(max_retries=3)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_apply_fix_success(self):
        """Test that a valid fix is applied and saved."""
        file_path = self.temp_path / "test_success.txt"
        file_path.write_text("Hello World", encoding="utf-8")
        
        # Fixer: Replace World with Python
        def fixer(content):
            return content.replace("World", "Python")
            
        result = self.engine.apply_fix(file_path, fixer)
        
        self.assertTrue(result.success)
        self.assertTrue(result.changed)
        self.assertEqual(file_path.read_text(), "Hello Python")

    def test_apply_fix_no_change(self):
        """Test that no change is reported if fixer returns same content."""
        file_path = self.temp_path / "test_no_change.txt"
        file_path.write_text("Hello World", encoding="utf-8")
        
        def fixer(content):
            return content
            
        result = self.engine.apply_fix(file_path, fixer)
        
        self.assertTrue(result.success)
        self.assertFalse(result.changed)
        self.assertEqual(file_path.read_text(), "Hello World")

    def test_apply_fix_rollback_on_syntax_error(self):
        """Test that changes are rolled back if stability check fails (SyntaxError)."""
        file_path = self.temp_path / "test_syntax.py"
        original_code = "print('Hello')\n"
        file_path.write_text(original_code, encoding="utf-8")
        
        # Fixer: Introduce syntax error
        def fixer(content):
            return "print('Hello'  # Missing closing parenthesis"
            
        result = self.engine.apply_fix(file_path, fixer)
        
        self.assertFalse(result.success)
        self.assertFalse(result.changed)
        # Content should be rolled back to original
        self.assertEqual(file_path.read_text(), original_code)
        self.assertIn("syntax errors", result.message)

    def test_file_not_found(self):
        """Test handling of missing file."""
        file_path = self.temp_path / "non_existent.txt"
        result = self.engine.apply_fix(file_path, lambda x: x)
        self.assertFalse(result.success)
        self.assertIn("File not found", result.message)

if __name__ == '__main__':
    unittest.main()
