import hashlib
import json
from pathlib import Path
from typing import Dict, Tuple


class RunbookError(Exception):
    pass


def parse_runbook_spec(spec: str) -> Tuple[str, str]:
    if "@" not in spec:
        raise RunbookError("runbook spec must be <id>@<version>")
    runbook_id, version = spec.split("@", 1)
    if not runbook_id or not version:
        raise RunbookError("runbook spec must be <id>@<version>")
    return runbook_id, version


def resolve_runbook_path(repo_root: Path, runbook_id: str) -> Path:
    return repo_root / "runbooks" / f"{runbook_id}.yaml"


def _load_runbook(path: Path) -> Dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RunbookError(f"runbook is not valid JSON/YAML: {exc}") from exc
    return payload


def _compute_checksum(payload: Dict) -> str:
    checksum_payload = dict(payload)
    metadata = dict(checksum_payload.get("metadata", {}))
    metadata["checksum"] = ""
    checksum_payload["metadata"] = metadata
    normalized = json.dumps(checksum_payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def resolve_runbook(spec: str, repo_root: Path) -> Tuple[Path, Dict]:
    runbook_id, version = parse_runbook_spec(spec)
    path = resolve_runbook_path(repo_root, runbook_id)
    if not path.is_file():
        raise RunbookError(f"runbook not found: {path}")

    payload = _load_runbook(path)
    metadata = payload.get("metadata", {})
    if metadata.get("version") != version:
        raise RunbookError("runbook version mismatch")

    expected_checksum = metadata.get("checksum")
    if not expected_checksum:
        raise RunbookError("runbook checksum missing")

    actual_checksum = _compute_checksum(payload)
    if actual_checksum != expected_checksum:
        raise RunbookError("runbook checksum mismatch")

    return path, payload
