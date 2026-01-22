import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from aaa import init_commands


class ApplyTemplatesNoopTest(unittest.TestCase):
    def test_noop_apply_templates_creates_empty_commit(self):
        with TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            plan_path = repo_root / "plan.json"
            plan = {
                "plan_version": "0.1",
                "aaa": {"org": "ai-asset-architecture"},
                "target": {"project_slug": "aaa-sandbox-20260122"},
                "repos": [{"name": "sample-docs", "template": "aaa-tpl-docs"}],
                "steps": [],
                "reporting": {},
            }
            plan_path.write_text(json.dumps(plan), encoding="utf-8")

            calls: list[list[str]] = []

            def fake_run(cmd, cwd=None, input_data=None):
                if cmd[:2] == ["git", "clone"]:
                    Path(cmd[-1]).mkdir(parents=True, exist_ok=True)
                elif cmd[:3] == ["gh", "repo", "clone"]:
                    Path(cmd[-1]).mkdir(parents=True, exist_ok=True)
                elif cmd[:2] == ["git", "status"]:
                    return init_commands.CommandResult(code=0, stdout="", stderr="")
                calls.append(cmd)
                return init_commands.CommandResult(code=0, stdout="", stderr="")

            with patch.object(init_commands, "REPO_ROOT", repo_root), patch.object(
                init_commands, "_run_command", side_effect=fake_run
            ), patch.object(init_commands, "_require_tool", return_value=None):
                init_commands.apply_templates(
                    org="ai-asset-architecture",
                    from_plan=plan_path,
                    aaa_tag="v0.1.0",
                    jsonl=False,
                    log_dir=None,
                    dry_run=False,
                )

            commit_calls = [cmd for cmd in calls if cmd[:2] == ["git", "commit"]]
            self.assertTrue(commit_calls, "expected an empty commit on noop")
            self.assertIn("--allow-empty", commit_calls[0])

            push_calls = [cmd for cmd in calls if cmd[:2] == ["git", "push"]]
            self.assertTrue(push_calls, "expected push on noop")


if __name__ == "__main__":
    unittest.main()
