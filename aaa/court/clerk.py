import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import uuid4
from aaa.court.schema import CaseFile, CaseStatus, Ruling, Verdict

class CourtClerk:
    def __init__(self, root_path: Optional[Path] = None):
        if root_path:
            self.root_path = root_path
        else:
            self.root_path = Path.cwd() / ".aaa"
        
        self.case_dir = self.root_path / "court" / "cases"
        self.case_dir.mkdir(parents=True, exist_ok=True)

    def file_case(self, plaintiff: str, facts: Dict[str, Any]) -> str:
        """Submit a new case to the court."""
        case_id = str(uuid4())
        case = CaseFile(
            case_id=case_id,
            plaintiff=plaintiff,
            facts=facts,
            status=CaseStatus.PENDING
        )
        self._save(case)
        return case_id

    def list_pending_cases(self) -> List[CaseFile]:
        """List all pending cases."""
        pending = []
        for file_path in self.case_dir.glob("*.json"):
            try:
                case = self._load(file_path)
                if case.status == CaseStatus.PENDING:
                    pending.append(case)
            except Exception:
                continue # Skip corrupted files
        return sorted(pending, key=lambda c: c.submitted_at)

    def get_case(self, case_id: str) -> Optional[CaseFile]:
        """Retrieve a specific case."""
        file_path = self.case_dir / f"{case_id}.json"
        if not file_path.exists():
            return None
        return self._load(file_path)

    def apply_ruling(self, case_id: str, ruling: Ruling, reasoning: str, judge_id: str) -> CaseFile:
        """Apply a verdict to a case."""
        case = self.get_case(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Create verdict
        verdict = Verdict(
            ruling=ruling,
            reasoning=reasoning,
            judge_id=judge_id
        )
        
        # Update case
        case.verdict = verdict
        case.status = CaseStatus.ADJUDICATED
        self._save(case)
        return case

    def _save(self, case: CaseFile):
        file_path = self.case_dir / f"{case.case_id}.json"
        file_path.write_text(case.model_dump_json(indent=2), encoding="utf-8")

    def _load(self, file_path: Path) -> CaseFile:
        return CaseFile.model_validate_json(file_path.read_text(encoding="utf-8"))
