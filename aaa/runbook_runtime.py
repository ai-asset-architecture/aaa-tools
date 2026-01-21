import json
import re
from datetime import datetime, timezone
from typing import Any


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


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
