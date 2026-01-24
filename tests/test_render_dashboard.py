import unittest

from aaa.ops.render_dashboard import compute_compliance


class TestRenderDashboard(unittest.TestCase):
    def test_metrics_compute_drift_and_health(self):
        from aaa.ops import render_dashboard

        payload = {
            "repos": [
                {"name": "a", "archived": False, "checks": [{"id": "orphaned_assets", "status": "fail"}]},
                {"name": "b", "archived": False, "checks": [{"id": "orphaned_assets", "status": "pass"}]},
                {"name": "c", "archived": True, "checks": [{"id": "orphaned_assets", "status": "fail"}]},
            ]
        }
        metrics = render_dashboard.compute_metrics(payload)
        self.assertAlmostEqual(metrics["drift_rate"], 0.5)
        self.assertAlmostEqual(metrics["repo_health"], 0.5)
    def test_compliance_rate_excludes_archived(self):
        payload = {
            "repos": [
                {"name": "a", "archived": False, "checks": [{"id": "x", "status": "pass"}]},
                {"name": "b", "archived": True, "checks": [{"id": "x", "status": "fail"}]},
                {"name": "c", "archived": False, "checks": [{"id": "x", "status": "error"}]},
            ]
        }
        rate, rows, summary = compute_compliance(payload)
        self.assertAlmostEqual(rate, 0.5)
        self.assertEqual(rows[0]["compliant"], True)
        self.assertEqual(rows[1]["compliant"], None)
        self.assertEqual(rows[2]["compliant"], False)
        self.assertEqual(summary["total_repos"], 3)

    def test_render_outputs_include_repo_rows(self):
        from aaa.ops.render_dashboard import render_markdown, render_html

        rows = [
            {"name": "a", "repo_type": "docs", "compliant": True, "checks": [{"id": "x", "status": "pass"}]},
        ]
        summary = {
            "total_repos": 1,
            "eligible_repos": 1,
            "compliant_repos": 1,
            "failing_repos": 0,
            "archived_repos": 0,
        }
        metrics = {"drift_rate": 0.0, "repo_health": 1.0}
        thresholds = {"compliance": 0.8, "drift": 0.05, "health": 0.9}
        md = render_markdown("2026-01-24", 1.0, rows, summary, metrics)
        html = render_html("2026-01-24", 1.0, rows, summary, metrics, thresholds)
        self.assertIn("a", md)
        self.assertIn("a", html)
        self.assertIn("Governance Compliance Dashboard", html)

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
        self.assertTrue((tmp_dir / "dashboard.css").exists())
        self.assertTrue((tmp_dir / "dashboard.js").exists())
        self.assertTrue((tmp_dir / "trends.json").exists())
        self.assertTrue((tmp_dir / "metrics.json").exists())

    def test_cli_render_dashboard_thresholds(self):
        import json
        from pathlib import Path
        try:
            from typer.testing import CliRunner
            from aaa.cli import app
        except ModuleNotFoundError:
            self.skipTest("typer not installed")

        runner = CliRunner()
        tmp_dir = Path(f"{self._testMethodName}_thresholds")
        tmp_dir.mkdir(exist_ok=True)
        input_path = tmp_dir / "nightly.json"
        md_path = tmp_dir / "out.md"
        html_path = tmp_dir / "index.html"
        payload = {
            "generated_at": "2026-01-24",
            "repos": [
                {"name": "a", "archived": False, "checks": [{"id": "orphaned_assets", "status": "fail"}]},
            ],
        }
        input_path.write_text(json.dumps(payload))

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
                "--threshold",
                "0.0",
                "--drift-threshold",
                "0.1",
                "--health-threshold",
                "0.0",
            ],
        )
        self.assertEqual(result.exit_code, 1)
        self.assertTrue(md_path.exists())
        self.assertTrue(html_path.exists())


if __name__ == "__main__":
    unittest.main()
