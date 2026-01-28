import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Violation:
    code: str
    severity: str
    message: str
    rule_reference: Optional[str] = None
    fix_suggestion: Optional[str] = None
    details: Optional[List[str]] = None

@dataclass
class SemanticResult:
    status: str
    command: str
    violations: List[Violation]
    agent_context: Optional[str] = None
    summary: Optional[str] = None
    exit_code: int = 0

class OutputFormatter(ABC):
    @abstractmethod
    def format(self, result: SemanticResult) -> str:
        pass

class HumanFormatter(OutputFormatter):
    def format(self, result: SemanticResult) -> str:
        # For simplicity in this initial version, we output human-readable text
        # Future enhancement: Use Rich or similar for better CLI UI
        lines = []
        status_icon = "✅" if result.status == "success" else "❌"
        lines.append(f"{status_icon} AAA {result.command.upper()} Result: {result.status.upper()}")
        
        if result.violations:
            lines.append("\nViolations Found:")
            for v in result.violations:
                lines.append(f"  - [{v.severity.upper()}] {v.code}: {v.message}")
                if v.fix_suggestion:
                    lines.append(f"    Suggestion: {v.fix_suggestion}")
        
        if result.summary:
            lines.append(f"\nSummary: {result.summary}")
            
        return "\n".join(lines)

class JSONFormatter(OutputFormatter):
    def format(self, result: SemanticResult) -> str:
        return json.dumps(asdict(result), indent=2, ensure_ascii=True)

class LLMFormatter(OutputFormatter):
    def format(self, result: SemanticResult) -> str:
        lines = []
        lines.append(f"# AAA {result.command.upper()} Technical Report")
        lines.append(f"Status: **{result.status.upper()}**")
        
        if result.summary:
            lines.append(f"\n## Summary\n{result.summary}")
            
        if result.violations:
            lines.append("\n## Violations")
            for v in result.violations:
                lines.append(f"\n### <RULE_ID>{v.code}</RULE_ID>")
                lines.append(f"- **Severity**: {v.severity}")
                if v.rule_reference:
                    lines.append(f"- **Policy Reference**: [{v.rule_reference}]({v.rule_reference})")
                lines.append(f"\n#### <VIOLATION_DETAIL>\n{v.message}\n</VIOLATION_DETAIL>")
                if v.fix_suggestion:
                    lines.append(f"\n#### <EXEC_SUGGESTION>\n{v.fix_suggestion}\n</EXEC_SUGGESTION>")
        
        if result.agent_context:
            lines.append(f"\n## Agent Context\n{result.agent_context}")
            
        return "\n".join(lines)

def get_formatter(format_type: str) -> OutputFormatter:
    format_map = {
        "human": HumanFormatter(),
        "json": JSONFormatter(),
        "llm": LLMFormatter()
    }
    return format_map.get(format_type, HumanFormatter())

# Semantic Map for transforming raw errors into Enriched Results
ERROR_MAP = {
    "missing_gate_workflow": {
        "severity": "blocking",
        "message": "Missing mandatory reusable-gate.yaml workflow in .github/workflows/.",
        "rule_reference": "internal/development/policy/CI_ENFORCEMENT.md",
        "fix_suggestion": "aaa init repo-checks"
    },
    "check_failed:readme": {
        "severity": "blocking",
        "message": "README.md is missing mandatory sections (Purpose, Ownership, etc.) or CODEOWNERS is absent.",
        "rule_reference": "aaa-tpl-docs/docs/README_SPEC.md",
        "fix_suggestion": "aaa pack fix readme"
    },
    "check_failed:workflow": {
        "severity": "blocking",
        "message": "GitHub Workflows must use versioned AAA actions (@vX).",
        "rule_reference": "internal/development/policy/WORKFLOW_POLICY.md",
        "fix_suggestion": "Update workflow 'uses' statements to @v1"
    },
    "check_failed:test_policy_compliance": {
        "severity": "blocking",
        "message": "Milestone completion report violates the 1+2+1 Test Coverage Policy.",
        "rule_reference": "internal/development/policies/test-coverage-policy.md",
        "fix_suggestion": "Audit the completion report for 'Test Coverage Appendix' and valid evidence."
    },
    "check_failed:orphaned_assets": {
        "severity": "high",
        "message": "Found assets (Markdown files) not registered in index.json.",
        "rule_reference": "internal/development/architecture/aaa-architecture.md",
        "fix_suggestion": "aaa governance update-index"
    }
}

def enrich_result(command: str, raw_result: Dict[str, Any]) -> SemanticResult:
    violations = []
    errors = raw_result.get("errors", [])
    details_map = raw_result.get("details", {})
    
    # Also handle 'audit' specific format where checks are list of dicts
    if command == "audit" and "repos" in raw_result:
        for repo in raw_result["repos"]:
            for check in repo.get("checks", []):
                if check.get("status") == "fail":
                    err_id = f"check_failed:{check['id']}" if check['id'] != "runner" else "runner"
                    errors.append(err_id)
    
    for err in errors:
        mapping = ERROR_MAP.get(err, {
            "severity": "high",
            "message": f"Policy violation detected: {err}",
            "rule_reference": None,
            "fix_suggestion": "Review requirements and run 'aaa check' for details."
        })
        violations.append(Violation(
            code=err,
            severity=mapping["severity"],
            message=mapping["message"],
            rule_reference=mapping["rule_reference"],
            fix_suggestion=mapping["fix_suggestion"],
            details=details_map.get(err, [])
        ))
        
    status = "success" if not violations else "failure"
    exit_code = raw_result.get("exit_code", 0)
    
    return SemanticResult(
        status=status,
        command=command,
        violations=violations,
        exit_code=exit_code,
        summary=f"Found {len(violations)} violations during {command}." if violations else "Command completed successfully."
    )
