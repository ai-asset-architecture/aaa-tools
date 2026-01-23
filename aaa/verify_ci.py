import json
from pathlib import Path


def load_checks_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_checks(actual_names: list[str], manifest: dict, repo_type: str) -> tuple[bool, list[str]]:
    required = []
    for item in manifest.get("checks", []):
        applies_to = set(item.get("applies_to", []))
        if "all" in applies_to or repo_type in applies_to:
            required.append(item["name"])
    missing = [name for name in required if name not in actual_names]
    return len(missing) == 0, missing
