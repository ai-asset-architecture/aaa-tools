import yaml
import json
from pathlib import Path
from typing import Union, Dict, Any
from .schema import Policy

class CompilerError(Exception):
    pass

class ValidationError(CompilerError):
    pass

class Parser:
    """
    Parses Governance Policy DSL files (YAML/JSON) into Pydantic models.
    """
    
    @staticmethod
    def load(path: Union[str, Path]) -> Policy:
        path = Path(path)
        if not path.exists():
            raise CompilerError(f"Policy file not found: {path}")
            
        try:
            content = path.read_text(encoding="utf-8")
            if path.suffix in [".yaml", ".yml"]:
                data = yaml.safe_load(content)
            elif path.suffix == ".json":
                data = json.loads(content)
            else:
                # Default to YAML if unknown extension, or raise?
                # Let's try YAML as it's a superset of JSON often
                data = yaml.safe_load(content)
        except Exception as e:
            raise CompilerError(f"Failed to parse policy file: {e}")
            
        return Parser.parse_obj(data)
    
    @staticmethod
    def parse_obj(data: Dict[str, Any]) -> Policy:
        try:
            return Policy.model_validate(data)
        except Exception as e:
            raise ValidationError(f"Schema validation failed: {e}")
