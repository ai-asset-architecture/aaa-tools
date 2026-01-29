import unittest
import shutil
import tempfile
from pathlib import Path
from aaa.court.clerk import CourtClerk
from aaa.court.schema import CaseStatus, Ruling

class TestCourtClerk(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.clerk = CourtClerk(root_path=Path(self.test_dir))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_file_case(self):
        """Test filing a new case."""
        case_id = self.clerk.file_case(
            plaintiff="agent-007",
            facts={"issue": "test_waiver"}
        )
        self.assertIsNotNone(case_id)
        
        # Verify file exists
        files = list(self.clerk.case_dir.glob("*.json"))
        self.assertEqual(len(files), 1)

    def test_get_pending_cases(self):
        """Test listing pending cases."""
        self.clerk.file_case("agent-A", {"x": 1})
        self.clerk.file_case("agent-B", {"y": 2})
        
        pending = self.clerk.list_pending_cases()
        self.assertEqual(len(pending), 2)

    def test_ruling_update(self):
        """Test applying a ruling."""
        case_id = self.clerk.file_case("agent-C", {"z": 3})
        updated_case = self.clerk.apply_ruling(
            case_id,
            ruling=Ruling.WAIVE,
            reasoning="Special Exception",
            judge_id="human-boss"
        )
        self.assertEqual(updated_case.status, CaseStatus.ADJUDICATED)
        self.assertEqual(updated_case.verdict.ruling, Ruling.WAIVE)
