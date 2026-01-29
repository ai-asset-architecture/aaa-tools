import unittest
from datetime import datetime
from uuid import uuid4
from aaa.court.schema import CaseFile, Ruling, CaseStatus, Verdict

class TestCourtSchema(unittest.TestCase):
    def test_ruling_enum_has_waive(self):
        """Verify the 'WAIVE' option exists for Case #001."""
        self.assertEqual(Ruling.WAIVE, "waive")
        self.assertEqual(Ruling.APPROVE, "approve")
        self.assertEqual(Ruling.DENY, "deny")
        self.assertEqual(Ruling.MODIFY, "modify")

    def test_case_file_model(self):
        """Verify CaseFile model structure."""
        case_id = str(uuid4())
        case = CaseFile(
            case_id=case_id,
            plaintiff="aaa-agent",
            status=CaseStatus.PENDING,
            facts={"violation": "missing_workflow", "reason": "debt_check_failed"},
            submitted_at=datetime.utcnow()
        )
        self.assertEqual(case.status, CaseStatus.PENDING)
        self.assertEqual(case.plaintiff, "aaa-agent")

    def test_verdict_model(self):
        """Verify Verdict model structure."""
        verdict = Verdict(
            ruling=Ruling.WAIVE,
            reasoning="Bootstrapping Case #001",
            judge_id="human-01",
            ruled_at=datetime.utcnow()
        )
        self.assertEqual(verdict.ruling, Ruling.WAIVE)
