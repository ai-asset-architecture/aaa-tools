import pathlib
import unittest


class PackageIncludeTests(unittest.TestCase):
    def test_pyproject_includes_subpackages(self):
        pyproject = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
        text = pyproject.read_text(encoding="utf-8")
        self.assertIn('include = ["aaa", "aaa.*"]', text)


if __name__ == "__main__":
    unittest.main()
