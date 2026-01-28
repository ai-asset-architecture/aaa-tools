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
        milestone_ids = [m["id"] if isinstance(m, dict) else m for m in index_data["milestones"]]
        self.assertIn(milestone_id, milestone_ids)

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

    def test_complete_milestone_evidence_collection(self):
        """
        驗證 complete-milestone 能否自動蒐集 git 證據並更新 index.json
        """
        milestone_id = "v1.1"
        
        # 1. 先執行初始化 (Pre-condition)
        init_milestone(milestone_id, self.workspace)
        
        # 2. 模擬一些開發活動 (這裡 mock subprocess 模擬 git log)
        # 我們將在實作中調用 git log，所以測試時需要確保環境能運行或 mock 它
        # 這裡我們先測試基本結構和狀態更新
        
        from aaa.ops.milestone_manager import complete_milestone
        result = complete_milestone(milestone_id, self.workspace)
        
        self.assertEqual(result["status"], "success")
        
        # 3. 驗證報告內容
        report_path = self.workspace / "internal/development/milestones" / milestone_id / "completion_report.md"
        self.assertTrue(report_path.exists())
        content = report_path.read_text()
        
        # Assert: 報告應包含 Evidence Collection 標題
        self.assertIn("## Evidence Collection", content)
        
        # Assert: Index 狀態更新
        index_file = self.workspace / "internal" / "index.json"
        index_data = json.loads(index_file.read_text())
        
        milestone_entry = next((m for m in index_data["milestones"] if isinstance(m, dict) and m["id"] == milestone_id), None)
        self.assertIsNotNone(milestone_entry)
        self.assertEqual(milestone_entry["status"], "completed")

if __name__ == "__main__":
    unittest.main()
