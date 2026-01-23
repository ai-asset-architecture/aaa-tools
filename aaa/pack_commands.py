import json
from pathlib import Path
from typing import Any


def list_packs(repo_root: Path) -> dict[str, Any]:
    installed_path = repo_root / ".aaa" / "packs" / "installed.json"
    if not installed_path.exists():
        return {"installed": []}
    try:
        payload = json.loads(installed_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"installed": []}
    if not isinstance(payload, dict) or "installed" not in payload:
        return {"installed": []}
    return payload
