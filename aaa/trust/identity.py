import hashlib
import json
import os
from abc import ABC, abstractmethod

class Identity(ABC):
    @abstractmethod
    def sign(self, message: str) -> str:
        pass

    @abstractmethod
    def verify(self, message: str, signature: str) -> bool:
        pass

class AgentIdentity(Identity):
    """
    Minimal Sovereign Identity for v2.0.1.
    Uses SHA256 hashing for simulation in this prototype phase, 
    designed to be replaced by full RSA in production.
    """
    def __init__(self, agent_id: str, secret_key: str):
        self.agent_id = agent_id
        self.secret_key = secret_key

    def sign(self, message: str) -> str:
        # v2.0.1 Signature: HMAC-like SHA256
        data = f"{self.agent_id}:{message}:{self.secret_key}"
        return hashlib.sha256(data.encode()).hexdigest()

    def verify(self, message: str, signature: str) -> bool:
        return self.sign(message) == signature

    def __repr__(self):
        return f"AgentIdentity(id={self.agent_id})"
