import pytest
from typer.testing import CliRunner
from aaa.cli import app

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_help(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.output

def test_cli_os_status(runner):
    # 'os status' is a valid command in os_commands.py
    result = runner.invoke(app, ["os", "status"])
    assert result.exit_code in [0, 1]

def test_cli_court_docket(runner):
    # 'court docket' exists in court_commands.py
    result = runner.invoke(app, ["court", "docket"])
    assert result.exit_code in [0, 1]
