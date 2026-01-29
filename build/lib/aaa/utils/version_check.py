import atexit
import json
import os
import re
import threading
import time
import sys
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Callable, Optional
from urllib import request

CACHE_TTL_SECONDS = 24 * 60 * 60
DEFAULT_TIMEOUT_SECONDS = 2
DEFAULT_SOURCE_URL = "https://api.github.com/repos/ai-asset-architecture/aaa-tools/releases/latest"


@dataclass(frozen=True)
class UpdateResult:
    local_version: str
    remote_version: str
    release_url: str
    source: str


def schedule_update_hint() -> None:
    if _is_disabled():
        return
    state: dict[str, Optional[str]] = {"message": None}

    def worker() -> None:
        state["message"] = check_for_update()

    thread = threading.Thread(target=worker, name="aaa-update-check", daemon=True)
    thread.start()

    def emit() -> None:
        thread.join(timeout=0.1)
        message = state.get("message")
        if message:
            print(message, file=sys.stderr)

    atexit.register(emit)


def check_for_update(
    *,
    now: Optional[float] = None,
    fetch_remote: Optional[Callable[[], Optional[UpdateResult]]] = None,
    cache_path: Optional[Path] = None,
    local_version: Optional[str] = None,
) -> Optional[str]:
    if _is_disabled():
        return None
    now = time.time() if now is None else now
    cache_path = cache_path or _default_cache_path()
    local_version = local_version or _get_local_version()

    cached = _read_cache(cache_path, now)
    if cached:
        return _format_hint_if_needed(cached, local_version)

    fetch_remote = fetch_remote or _fetch_remote_version
    result = fetch_remote()
    if result is None:
        return None
    _write_cache(cache_path, now, result)
    return _format_hint_if_needed(result, local_version)


def _is_disabled() -> bool:
    return os.environ.get("AAA_DISABLE_UPDATE_HINT") == "1"


def _get_local_version() -> str:
    try:
        return metadata.version("aaa-tools")
    except metadata.PackageNotFoundError:
        return "0.0.0"


def _default_cache_path() -> Path:
    override = os.environ.get("AAA_VERSION_CHECK_CACHE")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".aaa" / "cache" / "version_check.json"


def _read_cache(path: Path, now: float) -> Optional[UpdateResult]:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    checked_at = payload.get("checked_at")
    if not isinstance(checked_at, (int, float)):
        return None
    if now - checked_at > CACHE_TTL_SECONDS:
        return None
    return UpdateResult(
        local_version=str(payload.get("local_version", "0.0.0")),
        remote_version=str(payload.get("remote_version", "0.0.0")),
        release_url=str(payload.get("release_url", "")),
        source=str(payload.get("source", "cache")),
    )


def _write_cache(path: Path, now: float, result: UpdateResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "checked_at": now,
        "local_version": result.local_version,
        "remote_version": result.remote_version,
        "release_url": result.release_url,
        "source": result.source,
    }
    path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")


def _fetch_remote_version() -> Optional[UpdateResult]:
    override = os.environ.get("AAA_UPDATE_REMOTE_VERSION")
    if override:
        return UpdateResult(
            local_version="0.0.0",
            remote_version=override.strip(),
            release_url="",
            source="env",
        )
    url = os.environ.get("AAA_UPDATE_SOURCE_URL", DEFAULT_SOURCE_URL)
    try:
        with request.urlopen(url, timeout=DEFAULT_TIMEOUT_SECONDS) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None
    tag = str(payload.get("tag_name", ""))
    release_url = str(payload.get("html_url", ""))
    if not tag:
        return None
    return UpdateResult(
        local_version="0.0.0",
        remote_version=tag,
        release_url=release_url,
        source=url,
    )


def _format_hint_if_needed(result: UpdateResult, local_version: str) -> Optional[str]:
    local_norm = _normalize_version(local_version)
    remote_norm = _normalize_version(result.remote_version)
    if local_norm is None or remote_norm is None:
        return None
    if local_norm >= remote_norm:
        return None
    return _format_hint(local_version, result.remote_version, result.release_url)


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


def _format_hint(local_version: str, remote_version: str, release_url: str) -> str:
    arrow = "\u2192"
    lines = [
        "",
        "\u256d" + "\u2500" * 62 + "\u256e",
        "\u2502" + " " * 62 + "\u2502",
        f"\u2502   Update available {local_version} {arrow} {remote_version}".ljust(63) + "\u2502",
        "\u2502   Run \"pip install --upgrade aaa-tools\" to update.".ljust(63) + "\u2502",
    ]
    if release_url:
        url_line = f"\u2502   See changes: {release_url}"[:63].ljust(63) + "\u2502"
        lines.append(url_line)
    lines.append("\u2502" + " " * 62 + "\u2502")
    lines.append("\u2570" + "\u2500" * 62 + "\u256f")
    lines.append("")
    return "\n".join(lines)
