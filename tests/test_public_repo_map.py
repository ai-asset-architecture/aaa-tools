import json
from pathlib import Path


def test_public_repo_map_exists_and_is_machine_readable():
    repo_root = Path(__file__).resolve().parents[1]
    repo_map_path = repo_root / "docs" / "repo-map.json"

    payload = json.loads(repo_map_path.read_text(encoding="utf-8"))

    assert payload["entry_repo"] == "aaa-tools"
    assert payload["public_status"] == "Public Preview"
    assert any(repo["name"] == "aaa-tools" for repo in payload["repositories"])


def test_public_repo_map_paths_exist_and_readme_points_to_it():
    repo_root = Path(__file__).resolve().parents[1]
    repo_map_path = repo_root / "docs" / "repo-map.json"
    payload = json.loads(repo_map_path.read_text(encoding="utf-8"))
    readme = (repo_root / "README.md").read_text(encoding="utf-8")

    for repo in payload["repositories"]:
        assert repo["name"]
        assert repo["role"]
        if repo["local_path"]:
            assert (repo_root / repo["local_path"]).exists()

    assert "docs/repo-map.json" in readme
