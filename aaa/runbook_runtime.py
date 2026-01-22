import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import governance_index
from .action_registry import ActionRegistry, RuntimeSecurityError


def execute_runbook(
    runbook: dict[str, Any],
    inputs: dict[str, Any],
    registry: ActionRegistry | None = None,
) -> dict[str, Any]:
    registry = registry or _default_registry()
    allowed_scopes = runbook.get("contract", {}).get("required_scopes")
    steps_output = []
    for step in runbook.get("steps", []):
        rendered_args = _render_args(step.get("args", []), inputs, steps_output)
        output = registry.execute(step.get("action", ""), rendered_args, allowed_scopes)
        steps_output.append({"name": step.get("name", ""), "output": output})
    return {"steps": steps_output}


def _default_registry() -> ActionRegistry:
    registry = ActionRegistry()
    registry.register("notify", _notify_stdout, scopes=["notify:send"])
    registry.register("fs_write", _fs_write, scopes=["fs:write"])
    registry.register("fs_update_frontmatter", _fs_update_frontmatter, scopes=["fs:write"])
    registry.register("governance.update_index", _governance_update_index, scopes=["gov:index"])
    registry.register("aaa_evals.run", _aaa_evals_run, scopes=["eval:run"])
    return registry


def _notify_stdout(args: Any) -> dict[str, Any]:
    payload = _payload_from_args(args)
    message = payload.get("message", "")
    structured = {
        "level": "INFO",
        "source": "runbook_runtime",
        "action": "notify",
        "timestamp": _iso_now(),
        "message": message,
        "payload": payload,
    }
    print(json.dumps(structured, ensure_ascii=True))
    return structured


def _fs_write(args: Any) -> dict[str, Any]:
    payload = _payload_from_args(args)
    path = _resolve_safe_path(payload.get("path", ""))
    content = payload.get("content", "")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"path": str(path)}


def _fs_update_frontmatter(args: Any) -> dict[str, Any]:
    path, updates = _parse_frontmatter_args(args)
    content = path.read_text(encoding="utf-8")
    metadata, body = _parse_frontmatter(content)
    metadata.update(updates)
    updated = _render_frontmatter(metadata, body)
    path.write_text(updated, encoding="utf-8")
    return {"path": str(path), "updated_keys": sorted(updates.keys())}


def _governance_update_index(args: Any) -> dict[str, Any]:
    options = _parse_flag_args(args)
    payload = governance_index.update_index(
        target_dir=options.get("target-dir", ""),
        pattern=options.get("pattern", "*.md"),
        readme_template=options.get("template", ""),
        index_output=options.get("index-output", "index.json"),
        metadata_fields=options.get("metadata-field", []),
    )
    return {"payload": payload}


def _aaa_evals_run(args: Any) -> dict[str, Any]:
    payload = _payload_from_args(args)
    suite = payload.get("suite", "")
    command = ["python3", "-m", "aaa.cli", "eval", suite]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def _render_args(args: Any, inputs: dict[str, Any], steps: list[dict[str, Any]]) -> Any:
    if isinstance(args, dict):
        return {key: _render_value(value, inputs, steps) for key, value in args.items()}
    if isinstance(args, list):
        return [_render_value(item, inputs, steps) for item in args]
    return args


def _render_value(value: Any, inputs: dict[str, Any], steps: list[dict[str, Any]]) -> Any:
    if isinstance(value, str):
        return _render_template(value, inputs, steps)
    if isinstance(value, list):
        return [_render_value(item, inputs, steps) for item in value]
    return value


def _render_template(value: str, inputs: dict[str, Any], steps: list[dict[str, Any]]) -> str:
    def replace(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        if expr.startswith("inputs."):
            key = expr.split(".", 1)[1]
            return str(inputs.get(key, ""))
        return ""

    return re.sub(r"\{\{\s*([^}]+)\s*\}\}", replace, value)


def _resolve_safe_path(path_value: str | Path) -> Path:
    if not path_value:
        raise RuntimeSecurityError("PATH_TRAVERSAL", "empty path not allowed")
    base = Path.cwd().resolve()
    raw = Path(path_value).expanduser()
    target = raw if raw.is_absolute() else (base / raw)
    target = target.resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise RuntimeSecurityError(
            "PATH_TRAVERSAL",
            "path escapes repo root",
            {"base": str(base), "path": str(target)},
        ) from exc
    return target


def _payload_from_args(args: Any) -> dict[str, Any]:
    if isinstance(args, dict):
        return args
    if isinstance(args, list):
        return _args_to_dict(args)
    return {}


def _args_to_dict(args: list[str]) -> dict[str, Any]:
    it = iter(args)
    result = {}
    for key in it:
        try:
            value = next(it)
        except StopIteration:
            value = ""
        result[key] = value
    return result


def _parse_flag_args(args: Any) -> dict[str, Any]:
    if isinstance(args, dict):
        return args
    if not isinstance(args, list):
        return {}
    result: dict[str, Any] = {}
    it = iter(range(len(args)))
    idx = 0
    while idx < len(args):
        token = args[idx]
        if token.startswith("--"):
            key = token[2:]
            value = ""
            if idx + 1 < len(args):
                value = args[idx + 1]
            if key == "metadata-field":
                result.setdefault(key, []).append(value)
            else:
                result[key] = value
            idx += 2
            continue
        idx += 1
    return result


def _parse_frontmatter_args(args: Any) -> tuple[Path, dict[str, str]]:
    if isinstance(args, dict):
        path_value = args.get("path", "")
        updates: dict[str, str] = {}
        raw_updates = args.get("set", {})
        if isinstance(raw_updates, dict):
            updates = {key: str(value) for key, value in raw_updates.items()}
        elif isinstance(raw_updates, list):
            for item in raw_updates:
                if isinstance(item, str) and "=" in item:
                    key, value = item.split("=", 1)
                    updates[key] = value
        elif isinstance(raw_updates, str) and "=" in raw_updates:
            key, value = raw_updates.split("=", 1)
            updates[key] = value
        if not path_value:
            raise ValueError("fs_update_frontmatter requires path")
        return Path(path_value), updates
    path_value = ""
    set_index = None
    for idx, item in enumerate(args):
        if item == "path" and idx + 1 < len(args):
            path_value = args[idx + 1]
        if item == "set":
            set_index = idx + 1
            break
    if not path_value:
        raise ValueError("fs_update_frontmatter requires path")
    updates = {}
    if set_index is not None:
        for item in args[set_index:]:
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            updates[key] = value
    return Path(path_value), updates


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
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
    metadata: dict[str, str] = {}
    for line in meta_lines:
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        metadata[key.strip()] = raw.strip()
    return metadata, body


def _render_frontmatter(metadata: dict[str, str], body: str) -> str:
    lines = ["---"]
    for key, value in metadata.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
