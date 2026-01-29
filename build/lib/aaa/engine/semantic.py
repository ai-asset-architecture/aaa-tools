from typing import List, Optional

class SemanticCheckResult:
    def __init__(self, passed: bool, reason: str, cost: int = 0):
        self.passed = passed
        self.reason = reason
        self.cost = cost  # 0 = Local, 1 = LLM

class SemanticChecker:
    """
    Zone One Component: Semantic verification with Hybrid Filter.
    Target Coverage: 100%
    """
    
    def check(self, content: str, rule_description: str, keywords: Optional[List[str]] = None) -> SemanticCheckResult:
        """
        Verify content against a natural language rule.
        
        Args:
            content: The text/code to check.
            rule_description: Natural language description of the rule.
            keywords: List of keywords to pre-filter (Hybrid Strategy).
            
        Returns:
            SemanticCheckResult
        """
        # 1. Hybrid Filter (Regex/String First)
        if keywords:
            # If NO keywords match, we assume the rule is irrelevant/passed.
            # E.g., Rule: "Check for password leaks". Keywords: ["password", "secret"].
            # If no "password" in text, we don't need to ask LLM.
            if not any(k.lower() in content.lower() for k in keywords):
                return SemanticCheckResult(True, "Hybrid Filter: No keywords found", cost=0)
        
        # 2. LLM Escalation (Simulated for v1.5 MVP)
        # In a real scenario, this would call self._ask_llm(content, rule_description)
        # For now, we simulate "If we reached here, we flag it for manual review" 
        # or we accept it if it's just a test. 
        # To make it testable, we'll allow injection of an LLM provider.
        
        return self._simulate_llm_check(content, rule_description)

    def _simulate_llm_check(self, content: str, rule: str) -> SemanticCheckResult:
        """
        Simulate LLM check. In v1.5, we just log that we WOULD call LLM.
        """
        # Feature Flag: Real LLM integration deferred to v1.6
        return SemanticCheckResult(False, f"LLM Escalation Triggered (Simulated): Verifying '{rule}'", cost=1)
