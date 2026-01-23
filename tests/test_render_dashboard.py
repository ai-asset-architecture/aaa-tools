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


if __name__ == "__main__":
    unittest.main()
