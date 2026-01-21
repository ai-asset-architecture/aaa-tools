import unittest
from unittest import mock

from aaa import cli
from aaa import runbook_registry
from aaa import runbook_runtime


class TestRunbookCliExec(unittest.TestCase):
    def test_cli_runbook_exec(self):
        fake_runbook = {
            "metadata": {"id": "ops/complete-milestone", "version": "1.0.0"},
            "contract": {
                "inputs": [],
                "preconditions": [],
                "outputs": [],
                "required_scopes": [],
                "timeout_seconds": 30,
                "idempotency_check": {"command": "true", "expect_exit_code": 0},
                "error_codes": [],
            },
            "observability": {
                "emit_events": True,
                "audit_artifacts": [],
                "failure_modes": [],
                "declared_side_effects": [],
            },
            "steps": [],
        }

        with mock.patch.object(runbook_registry, "resolve_runbook", return_value=("path", fake_runbook)):
            with mock.patch.object(runbook_runtime, "execute_runbook") as executor:
                cli.run_runbook_impl("ops/complete-milestone@1.0.0", inputs=["milestone_id=v0.5"])
                executor.assert_called_once()


if __name__ == "__main__":
    unittest.main()
