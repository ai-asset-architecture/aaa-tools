import pytest
from pathlib import Path
from aaa.compiler.parser import Parser, CompilerError, ValidationError
from aaa.compiler.schema import Policy

def test_load_yaml_success(tmp_path):
    f = tmp_path / "policy.yaml"
    f.write_text("""
metadata:
  name: test
  version: "1.0"
rules:
  - id: rule1
    description: desc
    severity: high
    check:
      type: file_exists
      path: README.md
""", encoding="utf-8")
    
    policy = Parser.load(f)
    assert policy.metadata.name == "test"
    assert len(policy.rules) == 1
    assert policy.rules[0].id == "rule1"

def test_load_json_success(tmp_path):
    f = tmp_path / "policy.json"
    f.write_text("""
{
    "metadata": {"name": "test", "version": "1.0"},
    "rules": [
        {
            "id": "rule1",
            "description": "desc",
            "severity": "high",
            "check": {
                "type": "file_exists",
                "path": "README.md"
            }
        }
    ]
}
""", encoding="utf-8")
    
    policy = Parser.load(f)
    assert isinstance(policy, Policy)

def test_load_file_not_found():
    with pytest.raises(CompilerError, match="Policy file not found"):
        Parser.load("nonexistent.yaml")

def test_parse_invalid_yaml(tmp_path):
    f = tmp_path / "bad.yaml"
    f.write_text(":", encoding="utf-8")
    with pytest.raises(CompilerError):
        Parser.load(f)

def test_validation_error(tmp_path):
    f = tmp_path / "invalid_schema.yaml"
    f.write_text("""
metadata:
  name: test
rules: [] 
""", encoding="utf-8") # Missing version in metadata
    
    with pytest.raises(ValidationError, match="Schema validation failed"):
        Parser.load(f)

def test_unknown_extension_defaults_to_yaml(tmp_path):
    f = tmp_path / "policy.txt"
    f.write_text("""
metadata:
    name: test
    version: "1.0"
rules: []
""", encoding="utf-8")
    policy = Parser.load(f)
    assert policy.metadata.name == "test"
