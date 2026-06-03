import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from aaa.action_registry import ActionRegistry, RuntimeSecurityError
from aaa.runbook_runtime import RunbookExecutionError, execute_runbook


def test_action_registry_blocks_missing_scope():
    registry = ActionRegistry()
    registry.register("notify", lambda args: {"ok": True}, scopes=["notify:send"])

    with pytest.raises(RuntimeSecurityError) as exc:
        registry.execute("notify", {"message": "hi"}, allowed_scopes=["repo:read"])

    assert exc.value.code == "SCOPE_VIOLATION"
    assert exc.value.details["required_any_of"] == ["notify:send"]


def test_execute_runbook_reports_unsupported_action_as_step_failure():
    runbook = {
        "contract": {"required_scopes": ["notify:send"]},
        "steps": [{"name": "bad-step", "action": "unknown.action", "args": []}],
    }

    with pytest.raises(RunbookExecutionError) as exc:
        execute_runbook(runbook, inputs={})

    assert exc.value.details["step"] == "bad-step"
    assert exc.value.details["action"] == "unknown.action"
    assert exc.value.details["error_type"] == "ValueError"
