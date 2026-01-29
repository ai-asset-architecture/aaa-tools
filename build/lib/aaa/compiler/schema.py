from enum import Enum
from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, ConfigDict

# --- Enums ---

class Severity(str, Enum):
    BLOCKING = "blocking"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class CheckType(str, Enum):
    FILE_EXISTS = "file_exists"
    CONTENT_CONTAINS = "content_contains"
    JSON_MATCH = "json_match"

# --- Check Definitions (Discriminated Unions for Type Safety) ---

class BaseCheck(BaseModel):
    model_config = ConfigDict(extra="forbid") # Strict schema

class FileExistsCheck(BaseCheck):
    type: Literal[CheckType.FILE_EXISTS] = CheckType.FILE_EXISTS
    path: str = Field(..., description="Path to the file, relative to workspace root.")

class ContentContainsCheck(BaseCheck):
    type: Literal[CheckType.CONTENT_CONTAINS] = CheckType.CONTENT_CONTAINS
    path: str
    pattern: str = Field(..., description="String or Regex to search for.")
    must_exist: bool = True

class JsonMatchCheck(BaseCheck):
    type: Literal[CheckType.JSON_MATCH] = CheckType.JSON_MATCH
    path: str
    key_path: str = Field(..., description="Dot-notation path to the key (e.g. 'milestone.id').")
    expected_value: Union[str, int, bool]

# Strict Union for Validation
CheckConfig = Union[FileExistsCheck, ContentContainsCheck, JsonMatchCheck]

# --- Rule & Policy Definitions ---

class FixSuggestion(BaseModel):
    description: str
    command: Optional[str] = None
    auto_fixable: bool = False

class Rule(BaseModel):
    id: str = Field(..., pattern=r"^[a-z0-9_]+$")
    description: str
    severity: Severity
    check: CheckConfig
    fix: Optional[FixSuggestion] = None

class PolicyMetadata(BaseModel):
    name: str
    version: str
    author: Optional[str] = None

class Policy(BaseModel):
    """
    Root object for a Governance Policy DSL file.
    Example: repo_structure_policy.yaml
    """
    metadata: PolicyMetadata
    rules: List[Rule]
