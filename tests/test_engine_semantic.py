import unittest
from aaa.engine.semantic import SemanticChecker

class TestSemanticChecker(unittest.TestCase):
    def setUp(self):
        self.checker = SemanticChecker()

    def test_hybrid_filter_pass(self):
        """Test that missing keywords avoid LLM cost."""
        content = "def hello(): print('hi')"
        # Rule: check for passwords
        result = self.checker.check(content, "No passwords", keywords=["password", "secret"])
        
        self.assertTrue(result.passed)
        self.assertEqual(result.cost, 0)
        self.assertIn("Hybrid Filter", result.reason)

    def test_hybrid_filter_trigger(self):
        """Test that present keywords trigger LLM escalation."""
        content = "password = '1234'"
        result = self.checker.check(content, "No passwords", keywords=["password"])
        
        # In sim mode, checking returns False (Flagged) and cost=1
        self.assertFalse(result.passed)
        self.assertEqual(result.cost, 1)
        self.assertIn("LLM Escalation Triggered", result.reason)

    def test_no_keywords_direct_escalation(self):
        """Test that providing no keywords goes straight to LLM."""
        content = "something"
        result = self.checker.check(content, "General check")
        
        self.assertEqual(result.cost, 1)

if __name__ == '__main__':
    unittest.main()
