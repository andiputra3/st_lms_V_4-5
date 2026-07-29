"""
ST-LMS v3 — Configuration Manager
Foundation Core — Phase 1

Manages BOUNDED parameters. Reference: LAW-MASTER-14.
"""

from typing import Any, Optional
from ..core.constants import BOUNDED_REGISTRY
from ..core.validators import validate_bounded
from ..core.exceptions import BoundedRangeError

class ConfigurationManager:
    def __init__(self):
        self._params: dict = {}
        for key, (default, _, _) in BOUNDED_REGISTRY.items():
            self._params[key] = default

    def get(self, key: str) -> float:
        if key not in BOUNDED_REGISTRY:
            raise KeyError(f"Unknown parameter: {key}")
        return self._params[key]

    def set(self, key: str, value: float) -> tuple[bool, str]:
        ok, msg = validate_bounded(key, value)
        if not ok:
            return False, msg
        self._params[key] = value
        return True, "OK"

    def valid(self, key: str, value: float) -> bool:
        ok, _ = validate_bounded(key, value)
        return ok

    def all_params(self) -> list[dict]:
        result = []
        for key, (default, lo, hi) in BOUNDED_REGISTRY.items():
            result.append({
                "key": key,
                "current": self._params[key],
                "default": default,
                "min": lo,
                "max": hi,
            })
        return result

    def reset(self) -> None:
        for key, (default, _, _) in BOUNDED_REGISTRY.items():
            self._params[key] = default

    def snapshot(self) -> dict:
        return dict(self._params)

    def restore(self, snapshot: dict) -> None:
        for key, value in snapshot.items():
            if key in BOUNDED_REGISTRY:
                self._params[key] = value
