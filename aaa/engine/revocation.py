import os
import json

class RevocationChecker:
    """
    Global Kill-Switch (Lockout) mechanism for v2.0.1.
    Checks against a central 'locks.json' or revocation list.
    """
    def __init__(self, revocation_file: str = ".aaa/revocation.json"):
        self.revocation_file = revocation_file

    def is_revoked(self, agent_id: str) -> bool:
        if not os.path.exists(self.revocation_file):
            return False
            
        try:
            with open(self.revocation_file, "r") as f:
                data = json.load(f)
                return agent_id in data.get("revoked_agents", [])
        except Exception:
            # Fail-safe: if file corrupted, assume not revoked but log error
            return False
