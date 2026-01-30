import unittest
from unittest.mock import patch

from aaa import init_commands


class InitPlanPresetsTest(unittest.TestCase):
    def _preset_plan(self, include_legacy=False, include_dot_github=True):
        repos = [
            {"name": ".github", "required_checks": ["lint", "test", "eval"]},
            {"name": "org-docs", "required_checks": ["lint", "test", "eval"]},
        ]
        if not include_dot_github:
            repos = [
                {"name": "org-docs", "required_checks": ["lint", "test", "eval"]}
            ]
        plan = {
            "plan_version": "2.0",
            "aaa": {"org": "ai-asset-architecture"},
            "target": {"project_slug": "demo", "org": "demo"},
            "steps": [],
            "reporting": {},
            "default_preset": "governance_native",
            "presets": {
                "governance_native": {"repos": repos},
            },
        }
        if include_legacy:
            plan["repos"] = [{"name": "legacy-repo", "required_checks": ["lint", "test", "eval"]}]
        return plan

    def test_presets_resolution_warns_on_mixed(self):
        plan = self._preset_plan(include_legacy=True)
        notices = []

        def capture_notice(message):
            notices.append(message)

        with patch.object(init_commands, "_emit_notice", side_effect=capture_notice):
            repos = init_commands._resolve_repos_from_plan(
                plan,
                preset=None,
                jsonl=False,
                command="aaa init",
                step_id="run_plan",
            )

        self.assertEqual(repos[0]["name"], ".github")
        self.assertIn("WARN legacy_repos_ignored=true", notices)

    def test_legacy_mode_emits_notice(self):
        plan = {
            "plan_version": "0.7",
            "aaa": {"org": "ai-asset-architecture"},
            "target": {"project_slug": "demo", "org": "demo"},
            "repos": [{"name": "legacy", "required_checks": ["lint", "test", "eval"]}],
            "steps": [],
            "reporting": {},
        }
        notices = []

        def capture_notice(message):
            notices.append(message)

        with patch.object(init_commands, "_emit_notice", side_effect=capture_notice):
            repos = init_commands._resolve_repos_from_plan(
                plan,
                preset=None,
                jsonl=False,
                command="aaa init",
                step_id="run_plan",
            )

        self.assertEqual(repos[0]["name"], "legacy")
        self.assertIn("MODE=legacy", notices)

    def test_missing_default_preset_fails(self):
        plan = self._preset_plan()
        plan.pop("default_preset")
        with self.assertRaises(init_commands.typer.Exit):
            init_commands._resolve_repos_from_plan(
                plan,
                preset=None,
                jsonl=False,
                command="aaa init",
                step_id="run_plan",
            )

    def test_missing_dot_github_fails(self):
        plan = self._preset_plan(include_dot_github=False)
        with self.assertRaises(init_commands.typer.Exit):
            init_commands._resolve_repos_from_plan(
                plan,
                preset=None,
                jsonl=False,
                command="aaa init",
                step_id="run_plan",
            )


if __name__ == "__main__":
    unittest.main()
