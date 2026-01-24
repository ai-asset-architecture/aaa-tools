import json
import os
import re
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any, Optional
from urllib import request

DEFAULT_REGISTRY_URL = "https://raw.githubusercontent.com/ai-asset-architecture/ai-asset-architecture-registry/main/registry_index.json"


@dataclass(frozen=True)
class ComponentStatus:
    name: str
    local_version: str
    remote_version: str
    status: str
    source: str
    details: dict[str, Any] | None = None


def load_registry_index() -> dict[str, Any]:
    path_override = os.environ.get("AAA_REGISTRY_INDEX_PATH")
    if path_override:
        path = Path(path_override).expanduser()
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    url = os.environ.get("AAA_REGISTRY_INDEX_URL", DEFAULT_REGISTRY_URL)
    with request.urlopen(url, timeout=2) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_remote_versions(index: dict[str, Any]) -> dict[str, str]:
    components = index.get("components", {})
    result: dict[str, str] = {}
    for key, entry in components.items():
        if not isinstance(entry, dict):
            continue
        latest = entry.get("latest")
        if isinstance(latest, str):
            result[key] = latest
    return result


def detect_local_versions(repo_root: Path) -> dict[str, Any]:
    return {
        "tools": _local_tools_version(),
        "actions": _local_actions_versions(repo_root),
        "evals": _local_repo_versions(repo_root, "aaa-evals"),
        "templates": _local_templates_version(repo_root),
        "prompts": "untracked",
    }


def build_outdated_report(repo_root: Path) -> dict[str, Any]:
    try:
        index = load_registry_index()
    except Exception:
        index = {}
    remote = get_remote_versions(index)
    local = detect_local_versions(repo_root)

    statuses = [
        _compare_versions("tools", local.get("tools"), remote.get("tools"), "registry"),
        _compare_actions(local.get("actions"), remote.get("actions")),
        _compare_versions("evals", local.get("evals"), remote.get("evals"), "registry"),
        _compare_versions("templates", local.get("templates"), remote.get("templates"), "registry"),
        _compare_versions("prompts", local.get("prompts"), remote.get("prompts"), "registry"),
    ]
    return {
        "source": index.get("registries", {}).get("official", {}).get("url", "registry"),
        "components": [status.__dict__ for status in statuses],
    }


def render_outdated_report(report: dict[str, Any]) -> str:
    lines = ["AAA Outdated Report", ""]
    header = "{:<10} {:<14} {:<14} {:<10}".format("Component", "Local", "Remote", "Status")
    lines.append(header)
    lines.append("-" * len(header))
    for item in report.get("components", []):
        lines.append(
            "{:<10} {:<14} {:<14} {:<10}".format(
                item.get("name", "-"),
                item.get("local_version", "-"),
                item.get("remote_version", "-"),
                item.get("status", "-"),
            )
        )
        details = item.get("details") or {}
        versions = details.get("versions")
        if versions:
            lines.append(f"  - versions: {', '.join(versions)}")
    return "\n".join(lines)


def _local_tools_version() -> str:
    try:
        return metadata.version("aaa-tools")
    except metadata.PackageNotFoundError:
        return "untracked"


def _local_actions_versions(repo_root: Path) -> dict[str, Any]:
    versions = _collect_uses_versions(repo_root, "aaa-actions")
    return _summarize_versions(versions)


def _local_repo_versions(repo_root: Path, repo_name: str) -> str:
    versions = _collect_uses_versions(repo_root, repo_name)
    if not versions:
        return "untracked"
    if len(set(versions)) == 1:
        return versions[0]
    return "multi"


def _local_templates_version(repo_root: Path) -> str:
    metadata_path = repo_root / ".aaa" / "metadata.json"
    if not metadata_path.exists():
        return "untracked"
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "untracked"
    value = payload.get("template_version") or payload.get("template_ref")
    if isinstance(value, str) and value:
        return value
    return "untracked"


def _collect_uses_versions(repo_root: Path, repo_name: str) -> list[str]:
    workflows = list((repo_root / ".github" / "workflows").glob("*.yml"))
    workflows.extend((repo_root / ".github" / "workflows").glob("*.yaml"))
    pattern = re.compile(r"uses:\s*[^\s]*/" + re.escape(repo_name) + r"@([A-Za-z0-9._-]+)")
    versions: list[str] = []
    for path in workflows:
        content = path.read_text(encoding="utf-8")
        for match in pattern.findall(content):
            versions.append(match)
    return versions


def _summarize_versions(versions: list[str]) -> dict[str, Any]:
    if not versions:
        return {"value": "untracked", "versions": []}
    unique = sorted(set(versions))
    if len(unique) == 1:
        return {"value": unique[0], "versions": unique}
    return {"value": "multi", "versions": unique}


def _compare_versions(name: str, local_value: Any, remote_value: Optional[str], source: str) -> ComponentStatus:
    local_version = _normalize_local_value(local_value)
    remote_version = remote_value or "unknown"
    status = _compare_version_strings(local_version, remote_version)
    return ComponentStatus(
        name=name,
        local_version=local_version,
        remote_version=remote_version,
        status=status,
        source=source,
    )


def _compare_actions(local_payload: Any, remote_version: Optional[str]) -> ComponentStatus:
    details = {}
    local_version = "untracked"
    if isinstance(local_payload, dict):
        local_version = local_payload.get("value", "untracked")
        versions = local_payload.get("versions") or []
        if versions:
            details["versions"] = versions
    remote_version = remote_version or "unknown"
    status = _compare_version_strings(local_version, remote_version)
    if local_version == "multi":
        status = "multi"
    return ComponentStatus(
        name="actions",
        local_version=local_version,
        remote_version=remote_version,
        status=status,
        source="registry",
        details=details or None,
    )


def _normalize_local_value(value: Any) -> str:
    if isinstance(value, dict):
        return value.get("value", "untracked")
    if isinstance(value, str):
        return value
    return "untracked"


def _compare_version_strings(local_version: str, remote_version: str) -> str:
    if local_version in {"untracked", "unknown", "multi"}:
        return "unknown"
    if remote_version in {"unknown", "untracked", ""}:
        return "unknown"
    local_norm = _normalize_version(local_version)
    remote_norm = _normalize_version(remote_version)
    if local_norm is None or remote_norm is None:
        return "unknown"
    if local_norm >= remote_norm:
        return "up-to-date"
    return "outdated"


def _normalize_version(value: str) -> Optional[tuple[int, ...]]:
    cleaned = value.strip()
    if cleaned.startswith("v"):
        cleaned = cleaned[1:]
    cleaned = re.sub(r"[^0-9\.]", "", cleaned)
    if not cleaned:
        return None
    try:
        return tuple(int(part or 0) for part in cleaned.split("."))
    except ValueError:
        return None
