from pathlib import Path


def has_reusable_gate(repo_root: Path, workflow_ref: str) -> bool:
    workflows_dir = repo_root / ".github" / "workflows"
    if not workflows_dir.exists():
        return False
    for path in workflows_dir.glob("*.yml"):
        if workflow_ref in path.read_text(encoding="utf-8", errors="ignore"):
            return True
    for path in workflows_dir.glob("*.yaml"):
        if workflow_ref in path.read_text(encoding="utf-8", errors="ignore"):
            return True
    return False
