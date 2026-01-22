import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest import mock

from aaa import runbook_runtime


class TestRunbookActionsMisc(unittest.TestCase):
    def test_notify_stdout_structured(self):
        runbook = {
            "metadata": {"id": "ops/test", "version": "1.0.0"},
            "contract": {
                "inputs": [],
                "preconditions": [],
                "outputs": [],
                "required_scopes": ["notify:send", "gov:index", "eval:run"],
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
            "steps": [
                {"name": "notify", "action": "notify", "args": ["message", "Milestone v0.5 completed"]}
            ],
        }

        buffer = StringIO()
        with redirect_stdout(buffer):
            runbook_runtime.execute_runbook(runbook, inputs={})
        payload = json.loads(buffer.getvalue().strip())
        self.assertEqual(payload["action"], "notify")
        self.assertIn("Milestone v0.5", payload["message"])

    def test_governance_update_index_action(self):
        runbook = {
            "metadata": {"id": "ops/test", "version": "1.0.0"},
            "contract": {
                "inputs": [],
                "preconditions": [],
                "outputs": [],
                "required_scopes": ["gov:index"],
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
            "steps": [
                {
                    "name": "index",
                    "action": "governance.update_index",
                    "args": [
                        "--target-dir",
                        "/tmp/docs",
                        "--pattern",
                        "*.md",
                        "--template",
                        "## Index\n",
                        "--index-output",
                        "index.json",
                    ],
                }
            ],
        }

        with mock.patch("aaa.runbook_runtime.governance_index.update_index") as update_index:
            runbook_runtime.execute_runbook(runbook, inputs={})
            update_index.assert_called_once()

    def test_aaa_evals_run_action(self):
        runbook = {
            "metadata": {"id": "ops/test", "version": "1.0.0"},
            "contract": {
                "inputs": [],
                "preconditions": [],
                "outputs": [],
                "required_scopes": ["eval:run"],
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
            "steps": [
                {"name": "evals", "action": "aaa_evals.run", "args": ["suite", "milestones/v0.5"]}
            ],
        }

        with mock.patch("aaa.runbook_runtime.subprocess.run") as runner:
            runner.return_value = mock.Mock(returncode=0, stdout="ok", stderr="")
            runbook_runtime.execute_runbook(runbook, inputs={})
            runner.assert_called_once()


if __name__ == "__main__":
    unittest.main()
