from pathlib import Path
from typing import Any

from . import governance_index


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
