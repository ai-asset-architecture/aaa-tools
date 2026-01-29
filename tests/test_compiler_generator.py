import pytest
from aaa.compiler.generator import Generator
from aaa.compiler.schema import Policy, PolicyMetadata, Rule, Severity, FileExistsCheck, ContentContainsCheck, JsonMatchCheck

def test_generator_all_types():
    policy = Policy(
        metadata=PolicyMetadata(name="test-policy", version="1.0"),
        rules=[
            Rule(
                id="file_exist",
                description="desc",
                severity=Severity.BLOCKING,
                check=FileExistsCheck(path="README.md")
            ),
            Rule(
                id="content_match",
                description="desc",
                severity=Severity.HIGH,
                check=ContentContainsCheck(path="README.md", pattern="Start")
            ),
            Rule(
                id="json_match",
                description="desc",
                severity=Severity.LOW,
                check=JsonMatchCheck(path="pkg.json", key_path="ver", expected_value=1)
            )
        ]
    )
    
    code = Generator.generate(policy)
    
    assert "check_file_exists('README.md')" in code
    assert "check_content_contains('README.md', r'Start')" in code
    assert "check_json_match('pkg.json', 'ver', 1)" in code
    assert "Policy: test-policy (v1.0)" in code
    assert "if violations:" in code
    assert "sys.exit(1)" in code
