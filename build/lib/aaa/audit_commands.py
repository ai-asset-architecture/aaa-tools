import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .check_commands import CHECKS, _load_repo_type


def _run_checks(repo_root: Path) -> list[dict[str, Any]]:
    evals_root = Path(os.environ.get("AAA_EVALS_ROOT", repo_root.parent / "aaa-evals"))
    runner = evals_root / "runner" / "run_repo_checks.py"
    checks: list[dict[str, Any]] = []
    repo_type = _load_repo_type(repo_root) or "unknown"
    manifest_path = os.environ.get(
        "AAA_CHECKS_MANIFEST",
        str(repo_root.parent / "aaa-actions" / "checks.manifest.json"),
    )
    if not runner.exists():
        return [{"id": "runner", "status": "error"}]
    for check in CHECKS:
        args = [sys.executable, str(runner), "--check", check, "--repo", str(repo_root)]
        if repo_type:
            args.extend(["--repo-type", repo_type])
        if check == "checks_manifest_alignment":
            args.extend(["--manifest-path", manifest_path])
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        status = "pass" if result.returncode == 0 else "fail"
        try:
            payload = json.loads(result.stdout) if result.stdout else {}
            if payload.get("pass") is not True:
                status = "fail"
        except json.JSONDecodeError:
            status = "error"
        checks.append({"id": check, "status": status})
    return checks


def run_local_audit(repo_root: Path) -> dict[str, Any]:
    repo_type = _load_repo_type(repo_root) or "unknown"
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repos": [
            {
                "name": repo_root.name,
                "repo_type": repo_type,
                "archived": False,
                "checks": _run_checks(repo_root),
            }
        ],
    }
    return payload
