import unittest

from aaa.ops.render_dashboard import compute_compliance


class TestRenderDashboard(unittest.TestCase):
    def test_compliance_rate_excludes_archived(self):
        payload = {
            "repos": [
                {"name": "a", "archived": False, "checks": [{"id": "x", "status": "pass"}]},
                {"name": "b", "archived": True, "checks": [{"id": "x", "status": "fail"}]},
                {"name": "c", "archived": False, "checks": [{"id": "x", "status": "error"}]},
            ]
        }
        rate, rows = compute_compliance(payload)
        self.assertAlmostEqual(rate, 0.5)
        self.assertEqual(rows[0]["compliant"], True)
        self.assertEqual(rows[1]["compliant"], None)
        self.assertEqual(rows[2]["compliant"], False)

    def test_render_outputs_include_repo_rows(self):
        from aaa.ops.render_dashboard import render_markdown, render_html

        rows = [
            {"name": "a", "repo_type": "docs", "compliant": True, "checks": [{"id": "x", "status": "pass"}]},
        ]
        md = render_markdown("2026-01-24", 1.0, rows)
        html = render_html("2026-01-24", 1.0, rows)
        self.assertIn("a", md)
        self.assertIn("a", html)
        self.assertIn("Compliance Rate", html)

    def test_cli_render_dashboard(self):
        import json
        from pathlib import Path
        try:
            from typer.testing import CliRunner
            from aaa.cli import app
        except ModuleNotFoundError:
            self.skipTest("typer not installed")

        runner = CliRunner()
        tmp_dir = Path(self._testMethodName)
        tmp_dir.mkdir(exist_ok=True)
        input_path = tmp_dir / "nightly.json"
        md_path = tmp_dir / "out.md"
        html_path = tmp_dir / "index.html"
        input_path.write_text(json.dumps({"generated_at": "2026-01-24", "repos": []}))

        result = runner.invoke(
            app,
            [
                "ops",
                "render-dashboard",
                "--input",
                str(input_path),
                "--md-out",
                str(md_path),
                "--html-out",
                str(html_path),
            ],
        )
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(md_path.exists())
        self.assertTrue(html_path.exists())


if __name__ == "__main__":
    unittest.main()
