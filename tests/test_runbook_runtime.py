import io
import json
import unittest
from contextlib import redirect_stdout

from aaa import runbook_runtime


class TestRunbookRuntime(unittest.TestCase):
    def test_runtime_renders_inputs_and_dispatches_notify(self):
        runbook = {
            "metadata": {"id": "ops/test", "version": "1.0.0"},
            "contract": {
                "inputs": [],
                "preconditions": [],
                "outputs": [],
                "required_scopes": ["notify:send"],
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
                    "name": "notify",
                    "action": "notify",
                    "args": ["message", "Milestone {{inputs.id}} completed"],
                }
            ],
        }

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            payload = runbook_runtime.execute_runbook(runbook, inputs={"id": "v0.5"})
        message = json.loads(buffer.getvalue().strip())["message"]
        self.assertEqual(message, "Milestone v0.5 completed")
        self.assertEqual(payload["steps"][0]["name"], "notify")


if __name__ == "__main__":
    unittest.main()
