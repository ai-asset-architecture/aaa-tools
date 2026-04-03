import json
from pathlib import Path, PurePosixPath
from typing import Any


ALLOWED_VALIDATOR_RULES = {
    "require_canonical_repo_root",
    "reject_workspace_root_as_repo_target",
    "reject_unknown_worktree_target",
}

ALLOWED_RUNTIME_GUARDS = {
    "canonical_root_guard",
    "worktree_target_guard",
    "target_scope_guard",
}


def load_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    return json.loads(path.read_text(encoding="utf-8"))


def _looks_like_workspace_root(path: str) -> bool:
    lowered = PurePosixPath(path).name.lower()
    return "workspace" in lowered


def validate_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[dict[str, str]] = []

    canonical_repo_root = str(bundle.get("canonical_repo_root", "")).strip()
    worktree_instances = [str(item).strip() for item in bundle.get("worktree_instances", [])]
    validator_rules = [str(item).strip() for item in bundle.get("validator_rules", [])]
    runtime_guards = [str(item).strip() for item in bundle.get("runtime_guards", [])]

    if bundle.get("version") != "v0.1":
        errors.append({"code": "version", "message": "unsupported bundle version"})

    if not canonical_repo_root:
        errors.append({"code": "canonical_repo_root", "message": "canonical_repo_root is required"})

    unknown_validator_rules = [rule for rule in validator_rules if rule not in ALLOWED_VALIDATOR_RULES]
    if unknown_validator_rules:
        errors.append(
            {
                "code": "validator_rules",
                "message": f"unknown validator rules: {', '.join(unknown_validator_rules)}",
            }
        )

    unknown_runtime_guards = [guard for guard in runtime_guards if guard not in ALLOWED_RUNTIME_GUARDS]
    if unknown_runtime_guards:
        errors.append(
            {
                "code": "runtime_guards",
                "message": f"unknown runtime guards: {', '.join(unknown_runtime_guards)}",
            }
        )

    if not worktree_instances:
        errors.append({"code": "worktree_instances", "message": "at least one worktree instance is required"})

    if canonical_repo_root and "reject_workspace_root_as_repo_target" in validator_rules:
        if _looks_like_workspace_root(canonical_repo_root):
            errors.append(
                {
                    "code": "canonical_repo_root",
                    "message": "workspace root cannot be used as canonical repo target",
                }
            )

    if "reject_unknown_worktree_target" in validator_rules:
        if not canonical_repo_root:
            errors.append(
                {
                    "code": "worktree_instances",
                    "message": "cannot validate worktree target without canonical_repo_root",
                }
            )
        else:
            expected_prefix = f"{canonical_repo_root}/.worktrees/"
            invalid_instances = [item for item in worktree_instances if not item.startswith(expected_prefix)]
            if invalid_instances:
                errors.append(
                    {
                        "code": "worktree_instances",
                        "message": f"worktree targets must live under {expected_prefix}: {', '.join(invalid_instances)}",
                    }
                )

    if canonical_repo_root:
        duplicate_targets = [item for item in worktree_instances if item == canonical_repo_root]
        if duplicate_targets:
            errors.append(
                {
                    "code": "worktree_instances",
                    "message": "worktree instance cannot equal canonical repo root",
                }
            )

    valid = not errors
    return {
        "status": "ok" if valid else "error",
        "valid": valid,
        "canonical_repo_root": canonical_repo_root,
        "resolved_validator_rules": validator_rules,
        "resolved_runtime_guards": runtime_guards,
        "worktree_instances": worktree_instances,
        "error_codes": [item["code"] for item in errors],
        "errors": errors,
    }


def validate_bundle_file(bundle_path: str | Path) -> dict[str, Any]:
    bundle = load_bundle(bundle_path)
    result = validate_bundle(bundle)
    result["bundle_path"] = str(Path(bundle_path))
    return result
