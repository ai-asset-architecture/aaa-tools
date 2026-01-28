from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

class ObjectType(BaseModel):
    """
    Defines a governance template for a specific type of project (e.g., service, library).
    """
    display_name: str = Field(..., description="Human-readable name of the object type")
    description: str = Field(..., description="Purpose and governance scope")
    inherited_packs: List[str] = Field(default_factory=list, description="List of pack IDs automatically applied")
    recommended_evals: List[str] = Field(default_factory=list, description="List of eval IDs recommended for this type")

class RegistryPack(BaseModel):
    """
    Represents a governance asset pack with semantic capabilities.
    """
    version: str
    capabilities: List[str] = Field(default_factory=list, description="Natural language descriptors of what this pack does")
    object_type_compatibility: List[str] = Field(default_factory=list, description="List of object types this pack supports")
    source: str
    dependencies: Optional[List[str]] = Field(None, description="Other packs this pack depends on")

class RegistryIndexV2(BaseModel):
    """
    v2.0 Schema for registry_index.json, supporting Object-Centric Governance.
    """
    schema_version: str = Field("2.0", const=True)
    min_cli_version: str = Field(..., description="Minimum AAA CLI version required to parse this registry")
    last_updated: datetime
    comment: Optional[str] = None
    
    object_types: Dict[str, ObjectType] = Field(..., description="Definitions of governed object types")
    packs: Dict[str, RegistryPack] = Field(..., description="Available governance packs")

    @validator('min_cli_version')
    def check_min_version_format(cls, v):
        # Basic check, could use packaging.version in real usage
        parts = v.split('.')
        if len(parts) < 3:
            raise ValueError("min_cli_version must be semantic version (X.Y.Z)")
        return v
