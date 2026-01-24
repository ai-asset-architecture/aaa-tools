import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from aaa import outdated as outdated_module


class TestOutdated(unittest.TestCase):
    def test_tools_outdated_when_local_older(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            registry = _registry_payload(
                tools="v1.0.0",
                actions="v1.0.0",
                evals="v1.0.0",
                templates="v1.0.0",
                prompts="v1.0.0",
            )
            registry_path = repo_root / "registry_index.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with mock.patch.object(outdated_module.metadata, "version", return_value="v0.9.0"):
                with _env({"AAA_REGISTRY_INDEX_PATH": str(registry_path)}):
                    report = outdated_module.build_outdated_report(repo_root)

            tools = _get_component(report, "tools")
            self.assertEqual(tools["status"], "outdated")
            self.assertEqual(tools["local_version"], "v0.9.0")
            self.assertEqual(tools["remote_version"], "v1.0.0")

    def test_templates_up_to_date_when_local_newer(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            metadata_path = repo_root / ".aaa" / "metadata.json"
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            metadata_path.write_text(
                json.dumps({"template_version": "v1.2.0"}),
                encoding="utf-8",
            )
            registry = _registry_payload(
                tools="v1.0.0",
                actions="v1.0.0",
                evals="v1.0.0",
                templates="v1.0.0",
                prompts="v1.0.0",
            )
            registry_path = repo_root / "registry_index.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with _env({"AAA_REGISTRY_INDEX_PATH": str(registry_path)}):
                report = outdated_module.build_outdated_report(repo_root)

            templates = _get_component(report, "templates")
            self.assertEqual(templates["status"], "up-to-date")
            self.assertEqual(templates["local_version"], "v1.2.0")
            self.assertEqual(templates["remote_version"], "v1.0.0")

    def test_untracked_template_reports_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            registry = _registry_payload(
                tools="v1.0.0",
                actions="v1.0.0",
                evals="v1.0.0",
                templates="v1.0.0",
                prompts="v1.0.0",
            )
            registry_path = repo_root / "registry_index.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            with _env({"AAA_REGISTRY_INDEX_PATH": str(registry_path)}):
                report = outdated_module.build_outdated_report(repo_root)

            templates = _get_component(report, "templates")
            self.assertEqual(templates["status"], "unknown")
            self.assertEqual(templates["local_version"], "untracked")
            self.assertEqual(templates["remote_version"], "v1.0.0")

    def test_timeout_returns_unknown_remote(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            with mock.patch.object(outdated_module, "load_registry_index", side_effect=TimeoutError):
                with mock.patch.object(outdated_module.metadata, "version", return_value="v1.0.0"):
                    report = outdated_module.build_outdated_report(repo_root)

            tools = _get_component(report, "tools")
            self.assertEqual(tools["remote_version"], "unknown")
            self.assertEqual(tools["status"], "unknown")

    def test_actions_multi_version_detection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            workflows = repo_root / ".github" / "workflows"
            workflows.mkdir(parents=True, exist_ok=True)
            (workflows / "ci.yml").write_text(
                "uses: ai-asset-architecture/aaa-actions@v0.9.1\n"
                "uses: ai-asset-architecture/aaa-actions@v1.0.0\n",
                encoding="utf-8",
            )
            registry = _registry_payload(
                tools="v1.0.0",
                actions="v1.0.0",
                evals="v1.0.0",
                templates="v1.0.0",
                prompts="v1.0.0",
            )
            registry_path = repo_root / "registry_index.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            env = {
                "AAA_REGISTRY_INDEX_PATH": str(registry_path),
            }
            with _env(env):
                report = outdated_module.build_outdated_report(repo_root)

            actions = _get_component(report, "actions")
            self.assertEqual(actions["status"], "multi")
            self.assertIn("v0.9.1", actions.get("details", {}).get("versions", []))
            self.assertIn("v1.0.0", actions.get("details", {}).get("versions", []))


def _registry_payload(**latest):
    return {
        "components": {
            "tools": {"latest": latest.get("tools", "")},
            "actions": {"latest": latest.get("actions", "")},
            "evals": {"latest": latest.get("evals", "")},
            "templates": {"latest": latest.get("templates", "")},
            "prompts": {"latest": latest.get("prompts", "")},
        }
    }


def _get_component(report, name):
    return next(item for item in report["components"] if item["name"] == name)


class _env:
    def __init__(self, mapping):
        self.mapping = mapping
        self.original = {}

    def __enter__(self):
        for key, value in self.mapping.items():
            self.original[key] = os.environ.get(key)
            os.environ[key] = value

    def __exit__(self, exc_type, exc, tb):
        for key, value in self.original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
