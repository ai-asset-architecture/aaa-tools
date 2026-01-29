import pytest
import json
from aaa.output_formatter import (
    SemanticResult,
    Violation,
    HumanFormatter,
    JSONFormatter,
    LLMFormatter,
    get_formatter,
    enrich_result
)

@pytest.fixture
def sample_result():
    return SemanticResult(
        status="failure",
        command="check",
        violations=[
            Violation(
                code="test_code",
                severity="high",
                message="Test Violation",
                fix_suggestion="Fix it"
            )
        ],
        summary="Test Summary"
    )

def test_human_formatter(sample_result):
    formatter = HumanFormatter()
    output = formatter.format(sample_result)
    assert "❌ AAA CHECK Result: FAILURE" in output
    assert "Test Violation" in output
    assert "Suggestion: Fix it" in output

def test_json_formatter(sample_result):
    formatter = JSONFormatter()
    output = formatter.format(sample_result)
    data = json.loads(output)
    assert data["status"] == "failure"
    assert data["violations"][0]["code"] == "test_code"

def test_llm_formatter(sample_result):
    formatter = LLMFormatter()
    output = formatter.format(sample_result)
    assert "# AAA CHECK Technical Report" in output
    assert "<RULE_ID>test_code</RULE_ID>" in output
    assert "<EXEC_SUGGESTION>" in output
    assert "Fix it" in output

def test_get_formatter():
    assert isinstance(get_formatter("json"), JSONFormatter)
    assert isinstance(get_formatter("llm"), LLMFormatter)
    assert isinstance(get_formatter("human"), HumanFormatter)
    assert isinstance(get_formatter("unknown"), HumanFormatter)

def test_enrich_result_known_error():
    raw = {
        "errors": ["missing_gate_workflow"],
        "exit_code": 1
    }
    enriched = enrich_result("check", raw)
    assert enriched.status == "failure"
    assert len(enriched.violations) == 1
    v = enriched.violations[0]
    assert v.code == "missing_gate_workflow"
    assert v.severity == "blocking"
    assert "reusable-gate.yaml" in v.message

def test_enrich_result_unknown_error():
    raw = {
        "errors": ["unknown_error"],
        "exit_code": 1
    }
    enriched = enrich_result("check", raw)
    assert enriched.status == "failure"
    v = enriched.violations[0]
    assert v.code == "unknown_error"
    assert v.severity == "high" # Default

def test_enrich_result_audit_format():
    # Test special handling for audit command structure
    raw = {
        "repos": [
            {
                "checks": [
                    {"id": "readme", "status": "fail"}
                ]
            }
        ]
    }
    enriched = enrich_result("audit", raw)
    assert len(enriched.violations) == 1
    assert enriched.violations[0].code == "check_failed:readme"
