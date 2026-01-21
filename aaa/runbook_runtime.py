import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import governance_index


def execute_runbook(runbook: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    steps_output = []
    for step in runbook.get("steps", []):
        rendered_args = _render_args(step.get("args", []), inputs, steps_output)
        output = _dispatch_action(step.get("action", ""), rendered_args)
        steps_output.append({"name": step.get("name", ""), "output": output})
    return {"steps": steps_output}


def _dispatch_action(action: str, args: list[str]) -> dict[str, Any]:
    if action == "notify":
        payload = _notify_stdout(args)
        return {"payload": payload}
    if action == "fs_write":
        return _fs_write(args)
    if action == "fs_update_frontmatter":
        return _fs_update_frontmatter(args)
    if action == "governance.update_index":
        return _governance_update_index(args)
    if action == "aaa_evals.run":
        return _aaa_evals_run(args)
    raise ValueError(f"unsupported action: {action}")


def _notify_stdout(args: list[str]) -> dict[str, Any]:
    payload = _args_to_dict(args)
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


def _fs_write(args: list[str]) -> dict[str, Any]:
    payload = _args_to_dict(args)
    path = Path(payload.get("path", ""))
    content = payload.get("content", "")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return {"path": str(path)}


def _fs_update_frontmatter(args: list[str]) -> dict[str, Any]:
    path, updates = _parse_frontmatter_args(args)
    content = path.read_text(encoding="utf-8")
    metadata, body = _parse_frontmatter(content)
    metadata.update(updates)
    updated = _render_frontmatter(metadata, body)
    path.write_text(updated, encoding="utf-8")
    return {"path": str(path), "updated_keys": sorted(updates.keys())}


def _governance_update_index(args: list[str]) -> dict[str, Any]:
    options = _parse_flag_args(args)
    payload = governance_index.update_index(
        target_dir=options.get("target-dir", ""),
        pattern=options.get("pattern", "*.md"),
        readme_template=options.get("template", ""),
        index_output=options.get("index-output", "index.json"),
        metadata_fields=options.get("metadata-field", []),
    )
    return {"payload": payload}


def _aaa_evals_run(args: list[str]) -> dict[str, Any]:
    payload = _args_to_dict(args)
    suite = payload.get("suite", "")
    command = ["python3", "-m", "aaa.cli", "eval", suite]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def _render_args(args: list[str], inputs: dict[str, Any], steps: list[dict[str, Any]]) -> list[str]:
    rendered = []
    for item in args:
        if not isinstance(item, str):
            rendered.append(item)
            continue
        rendered.append(_render_template(item, inputs, steps))
    return rendered


def _render_template(value: str, inputs: dict[str, Any], steps: list[dict[str, Any]]) -> str:
    def replace(match: re.Match[str]) -> str:
        expr = match.group(1).strip()
        if expr.startswith("inputs."):
            key = expr.split(".", 1)[1]
            return str(inputs.get(key, ""))
        return ""

    return re.sub(r"\{\{\s*([^}]+)\s*\}\}", replace, value)


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


def _parse_flag_args(args: list[str]) -> dict[str, Any]:
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


def _parse_frontmatter_args(args: list[str]) -> tuple[Path, dict[str, str]]:
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
