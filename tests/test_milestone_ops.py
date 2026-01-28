import unittest
import os
import shutil
import json
from pathlib import Path
from aaa.ops.milestone_manager import init_milestone

class TestMilestoneOps(unittest.TestCase):
    def setUp(self):
        self.workspace = Path("/tmp/aaa_test_milestone_ops")
        if self.workspace.exists():
            shutil.rmtree(self.workspace)
        self.workspace.mkdir(parents=True)
        
        # Create a mock templates directory
        self.templates_dir = self.workspace / "templates"
        self.templates_dir.mkdir()
        self.prd_template = self.templates_dir / "PRD-template.md"
        self.prd_template.write_text("# PRD Template\n\nAuthor: <AUTHOR>\nDate: <DATE>\nStatus: <STATUS>")

    def tearDown(self):
        if self.workspace.exists():
            shutil.rmtree(self.workspace)

    def test_init_milestone_creates_structure(self):
        milestone_id = "v1.1"
        result = init_milestone(milestone_id, self.workspace)
        
        self.assertEqual(result["status"], "success")
        
        milestone_path = self.workspace / "internal/development/milestones" / milestone_id
        self.assertTrue(milestone_path.is_dir())
        self.assertTrue((milestone_path / "PRD.md").exists())
        
        # Check if it was registered to index.json
        index_file = self.workspace / "internal/index.json"
        self.assertTrue(index_file.exists())
        index_data = json.loads(index_file.read_text())
        self.assertIn(milestone_id, index_data["milestones"])

    def test_init_milestone_is_idempotent(self):
        milestone_id = "v1.1"
        # First run
        init_milestone(milestone_id, self.workspace)
        
        # Second run - should not crash, should return status skipped_or_warned
        result = init_milestone(milestone_id, self.workspace)
        self.assertEqual(result["status"], "skipped_or_warned")
        self.assertIn("already exists", result["message"])

    def test_context_injection(self):
        milestone_id = "v1.1"
        init_milestone(milestone_id, self.workspace)
        
        content = (self.workspace / "internal/development/milestones" / milestone_id / "PRD.md").read_text()
        
        # These should be injected (assuming git config user.name is available or mocked)
        self.assertNotIn("<AUTHOR>", content)
        self.assertNotIn("<DATE>", content)
        self.assertIn("Status: Draft", content)
        # Check for actual date format or at least that it's not the placeholder
        import datetime
        today = datetime.date.today().isoformat()
        self.assertIn(today, content)

if __name__ == "__main__":
    unittest.main()
