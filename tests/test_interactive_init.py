import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from aaa.init_commands import interactive
from aaa.compiler.schema import Policy

def test_interactive_init(tmp_path):
    # Mock typer interactions
    with patch("aaa.init_commands.typer") as mock_typer:
        # User inputs sequence:
        # Name: my-policy
        # Version: 1.0
        # Add rule? Yes (True)
        # ID: rule1
        # Desc: desc1
        # Type: file_exists
        # Path: README.md
        # Severity: high
        # Add rule? No (False)
        # Compile? Yes (True)
        
        mock_typer.prompt.side_effect = [
            "my-policy", # Name
            "1.0",       # Version
            "rule1",     # ID
            "desc1",     # Desc
            "file_exists", # Type
            "README.md",   # Path
            "high",        # Severity
        ]
        
        mock_typer.confirm.side_effect = [
            True,  # Add rule?
            False, # Add another rule?
            True   # Compile?
        ]
        
        output_dir = tmp_path / "out"
        interactive(output_dir=output_dir)
        
        # Verify files created
        yaml_path = output_dir / "my-policy.yaml"
        py_path = output_dir / "check_my_policy.py"
        
        assert yaml_path.exists()
        assert py_path.exists()
        
        content = yaml_path.read_text()
        assert "rule1" in content
        assert "README.md" in content
        
        py_content = py_path.read_text()
        assert "def main():" in py_content
        assert "check_file_exists('README.md')" in py_content

def test_interactive_init_json_match(tmp_path):
    with patch("aaa.init_commands.typer") as mock_typer:
         # Sequence: Name, Version, ID, Desc, Type=json_match, Path, Key, Expected, Severity
        mock_typer.prompt.side_effect = [
            "json-policy",
            "0.1",
            "json_rule",
            "check json",
            "json_match",
            "package.json",
            "version",
            "1.0.0",
            "blocking"
        ]
        mock_typer.confirm.side_effect = [True, False, True]
        
        output_dir = tmp_path / "out_json"
        interactive(output_dir=output_dir)
        
        py_path = output_dir / "check_json_policy.py"
        assert py_path.exists()
        py_content = py_path.read_text()
        assert "check_json_match('package.json', 'version', '1.0.0')" in py_content
