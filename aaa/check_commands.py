import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .cmd import verify_ci


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GATE = "ai-asset-architecture/aaa-actions/.github/workflows/reusable-gate.yaml"
CHECKS = [
    "readme",
    "workflow",
    "repo_type_consistency",
    "checks_manifest_alignment",
    "orphaned_assets",
]


def _load_repo_type(repo_root: Path) -> str:
    metadata_path = repo_root / ".aaa" / "metadata.json"
    if not metadata_path.exists():
        return ""
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ""
    return str(payload.get("repo_type") or "").strip()


def _run_repo_checks(repo_root: Path) -> list[str]:
    evals_root = Path(os.environ.get("AAA_EVALS_ROOT", REPO_ROOT.parent / "aaa-evals"))
    runner = evals_root / "runner" / "run_repo_checks.py"
    errors: list[str] = []
    if not runner.exists():
        return ["evals_runner_missing"]

    repo_type = _load_repo_type(repo_root)
    manifest_path = os.environ.get(
        "AAA_CHECKS_MANIFEST",
        str(REPO_ROOT.parent / "aaa-actions" / "checks.manifest.json"),
    )
    for check in CHECKS:
        args = [sys.executable, str(runner), "--check", check, "--repo", str(repo_root)]
        if repo_type:
            args.extend(["--repo-type", repo_type])
        if check == "checks_manifest_alignment":
            args.extend(["--manifest-path", manifest_path])
        run_result = subprocess.run(args, capture_output=True, text=True, check=False)
        result = run_result.stdout.strip()
        try:
            payload = json.loads(result) if result else {}
        except json.JSONDecodeError:
            payload = {}
        if run_result.returncode != 0 or payload.get("pass") is not True:
            errors.append(f"check_failed:{check}")
    return errors


def run_blocking_check(repo_root: Path) -> dict[str, Any]:
    workflow_ref = os.environ.get("AAA_GATE_WORKFLOW", DEFAULT_GATE)
    errors: list[str] = []
    if not verify_ci.has_reusable_gate(repo_root, workflow_ref):
        errors.append("missing_gate_workflow")

    errors.extend(_run_repo_checks(repo_root))
    exit_code = 0 if not errors else 1
    return {"exit_code": exit_code, "errors": errors}
