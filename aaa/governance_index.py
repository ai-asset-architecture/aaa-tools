import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class IndexedFile:
    path: str
    title: str
    hash: str
    last_modified: str
    metadata: dict[str, Any]


def _parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    if not content.startswith("---\n"):
        return {}, content
    lines = content.splitlines()
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return {}, content
    meta_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    metadata: dict[str, Any] = {}
    for line in meta_lines:
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        key = key.strip()
        raw = raw.strip()
        metadata[key] = _parse_frontmatter_value(raw)
    return metadata, body


def _parse_frontmatter_value(raw: str) -> Any:
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        parts = [item.strip() for item in inner.split(",")]
        return [item for item in (part.strip("'\"") for part in parts) if item]
    return raw.strip("'\"")


def _extract_title(body: str, metadata: dict[str, Any], fallback: str) -> str:
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip() or fallback
    return fallback


def _file_hash(path: Path, algo: str) -> str:
    if algo not in {"sha256", "sha1"}:
        raise ValueError(f"unsupported hash_algo: {algo}")
    hasher = hashlib.new(algo)
    hasher.update(path.read_bytes())
    return hasher.hexdigest()


def _iso_utc(dt: datetime) -> str:
    value = dt.astimezone(timezone.utc).isoformat(timespec="seconds")
    return value.replace("+00:00", "Z")


def _render_template(template: str, files: Iterable[IndexedFile]) -> str:
    start_tag = "{{ range files }}"
    end_tag = "{{ end }}"
    if start_tag not in template or end_tag not in template:
        return template
    prefix, rest = template.split(start_tag, 1)
    block, suffix = rest.split(end_tag, 1)
    rendered = "".join(_render_block(block, entry) for entry in files)
    return f"{prefix}{rendered}{suffix}"


def _render_block(block: str, entry: IndexedFile) -> str:
    value = block
    value = re.sub(r"{{\s*\.Path\s*}}", entry.path, value)
    value = re.sub(r"{{\s*\.Title\s*}}", entry.title, value)

    def replace_metadata(match: re.Match[str]) -> str:
        key = match.group(1)
        return str(entry.metadata.get(key, ""))

    value = re.sub(r"{{\s*\.Metadata\.([A-Za-z0-9_-]+)\s*}}", replace_metadata, value)
    return value


def update_index(
    *,
    target_dir: Path | str,
    pattern: str,
    readme_template: str,
    index_output: str = "index.json",
    metadata_fields: list[str] | None = None,
    include_frontmatter: bool = True,
    sort_by: str = "filename",
    hash_algo: str = "sha256",
    dry_run: bool = False,
    allow_empty: bool = False,
) -> dict[str, Any]:
    directory = Path(target_dir)
    if not directory.exists() or not directory.is_dir():
        raise ValueError("target_dir must be an existing directory")
    files = sorted(directory.glob(pattern))
    if not files and not allow_empty:
        raise ValueError("no files matched pattern")
    readme = next((path for path in files if path.name == "README.md"), None)
    files = [path for path in files if path.name != "README.md"]
    if not files and readme is not None:
        files = [readme]
    if not files and not allow_empty:
        raise ValueError("no files matched pattern")

    metadata_fields = metadata_fields or []
    indexed: list[IndexedFile] = []
    for path in files:
        content = path.read_text(encoding="utf-8")
        metadata: dict[str, Any] = {}
        body = content
        if include_frontmatter:
            metadata, body = _parse_frontmatter(content)
        selected_metadata = {field: metadata.get(field) for field in metadata_fields if field in metadata}
        title = _extract_title(body, metadata, path.stem)
        last_modified = metadata.get("date")
        if not last_modified:
            last_modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).date().isoformat()
        indexed.append(
            IndexedFile(
                path=path.relative_to(directory).as_posix(),
                title=title,
                hash=_file_hash(path, hash_algo),
                last_modified=str(last_modified),
                metadata=selected_metadata,
            )
        )

    indexed = _sort_indexed(indexed, sort_by)
    payload = {
        "generated_at": _iso_utc(datetime.now(timezone.utc)),
        "source_dir": str(directory),
        "hash_algo": hash_algo,
        "files": [entry.__dict__ for entry in indexed],
    }

    readme_content = _render_template(readme_template, indexed)
    if not dry_run:
        (directory / "README.md").write_text(readme_content, encoding="utf-8")
        (directory / index_output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _sort_indexed(entries: list[IndexedFile], sort_by: str) -> list[IndexedFile]:
    if sort_by == "filename":
        return sorted(entries, key=lambda item: item.path)
    if sort_by == "last_modified":
        return sorted(entries, key=lambda item: item.last_modified)
    if sort_by.startswith("frontmatter:"):
        key = sort_by.split("frontmatter:", 1)[1]
        return sorted(entries, key=lambda item: str(item.metadata.get(key, "")))
    return entries
