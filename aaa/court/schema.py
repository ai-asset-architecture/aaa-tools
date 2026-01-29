from datetime import datetime
from enum import Enum
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

class Ruling(str, Enum):
    APPROVE = "approve"
    DENY = "deny"
    MODIFY = "modify"
    WAIVE = "waive"  # Legalizes rule exemptions

class CaseStatus(str, Enum):
    PENDING = "pending"
    ADJUDICATED = "adjudicated"
    DISMISSED = "dismissed"

class Verdict(BaseModel):
    ruling: Ruling
    reasoning: str
    judge_id: str
    ruled_at: datetime = Field(default_factory=datetime.utcnow)

class CaseFile(BaseModel):
    case_id: str
    plaintiff: str
    status: CaseStatus = CaseStatus.PENDING
    facts: Dict[str, Any]
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    verdict: Optional[Verdict] = None
