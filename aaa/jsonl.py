import json
from datetime import datetime, timezone
from typing import Any, Optional


def _rfc3339_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def emit_jsonl(
    enabled: bool,
    *,
    event: str,
    status: str,
    command: str,
    step_id: str,
    code: Optional[int] = None,
    message: Optional[str] = None,
    data: Optional[dict[str, Any]] = None,
) -> None:
    if not enabled:
        return
    payload: dict[str, Any] = {
        "event": event,
        "ts": _rfc3339_now(),
        "command": command,
        "step_id": step_id,
        "status": status,
    }
    if code is not None:
        payload["code"] = code
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    print(json.dumps(payload, ensure_ascii=True), flush=True)
