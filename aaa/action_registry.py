from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ActionSpec:
    name: str
    handler: Callable[[Any], dict[str, Any]]
    scopes: list[str]


class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, ActionSpec] = {}

    def register(self, name: str, handler: Callable[[Any], dict[str, Any]], scopes: list[str]) -> None:
        self._actions[name] = ActionSpec(name=name, handler=handler, scopes=scopes)

    def execute(self, name: str, args: Any, allowed_scopes: list[str]) -> dict[str, Any]:
        spec = self._actions.get(name)
        if spec is None:
            raise ValueError(f"unsupported action: {name}")
        missing = [scope for scope in spec.scopes if scope not in allowed_scopes]
        if missing:
            raise PermissionError(f"missing scopes: {', '.join(missing)}")
        return spec.handler(args)
