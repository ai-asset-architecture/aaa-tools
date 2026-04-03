from pathlib import Path
from typing import Any

from . import context_runtime_preflight
from . import governance_index
from . import multi_repo_worktree_identity
from . import tool_command_adoption


def update_index_cli(
    *,
    target_dir: str,
    pattern: str,
    readme_template: str,
    index_output: str = "index.json",
    metadata_fields: list[str] | None = None,
    include_frontmatter: bool = True,
    sort_by: str = "filename",
    hash_algo: str = "sha256",
    dry_run: bool = False,
) -> dict[str, Any]:
    return governance_index.update_index(
        target_dir=Path(target_dir),
        pattern=pattern,
        readme_template=readme_template,
        index_output=index_output,
        metadata_fields=metadata_fields,
        include_frontmatter=include_frontmatter,
        sort_by=sort_by,
        hash_algo=hash_algo,
        dry_run=dry_run,
    )


def validate_tool_command_adoption_cli(*, bundle: str) -> dict[str, Any]:
    return tool_command_adoption.validate_bundle_file(bundle)


def validate_multi_repo_worktree_identity_cli(*, bundle: str) -> dict[str, Any]:
    return multi_repo_worktree_identity.validate_bundle_file(bundle)


def validate_context_runtime_preflight_cli(*, bundle: str) -> dict[str, Any]:
    return context_runtime_preflight.validate_bundle_file(bundle)
