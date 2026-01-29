import pytest
from pathlib import Path
from aaa.court.judge import CourtJudge
from aaa.court.clerk import CourtClerk
from aaa.court.schema import CaseFile, CaseStatus, Ruling

@pytest.fixture
def clerk(tmp_path):
    return CourtClerk(data_dir=tmp_path)

@pytest.fixture
def judge(clerk):
    return CourtJudge(clerk=clerk)

def test_judge_initialization(judge):
    assert judge.clerk is not None

def test_judge_display_docket(judge, clerk):
    # Test internal display logic
    case_id = clerk.file_case(
        plaintiff="Agent-001",
        facts={"test": "data"}
    )
    case = clerk.get_case(case_id)
    # This just ensures no crash during display
    judge._display_docket(case)
