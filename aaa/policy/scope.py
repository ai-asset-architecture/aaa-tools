import os
from typing import List

class ScopeEnforcer:
    """
    Path-based recursion blocking for Agents (v2.0.1).
    """
    def __init__(self, allowed_paths: List[str]):
        # Normalize paths
        self.allowed_paths = [os.path.abspath(p) for p in allowed_paths]

    def is_allowed(self, target_path: str) -> bool:
        abs_target = os.path.abspath(target_path)
        for allowed in self.allowed_paths:
            # Check if target is same as or subdirectory of allowed
            if abs_target == allowed or abs_target.startswith(allowed + os.sep):
                return True
        return False
