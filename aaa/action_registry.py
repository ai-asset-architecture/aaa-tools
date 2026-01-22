from dataclasses import dataclass
from typing import Any, Callable


class RuntimeSecurityError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


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

    def execute(self, name: str, args: Any, allowed_scopes: list[str] | None) -> dict[str, Any]:
        spec = self._actions.get(name)
        if spec is None:
            raise ValueError(f"unsupported action: {name}")
        if allowed_scopes is not None:
            missing = [scope for scope in spec.scopes if scope not in allowed_scopes]
            if missing:
                raise RuntimeSecurityError(
                    "SCOPE_VIOLATION",
                    f"missing scopes: {', '.join(missing)}",
                    {"missing": missing, "allowed": allowed_scopes},
                )
        return spec.handler(args)
