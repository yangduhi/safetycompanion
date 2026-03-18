from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.common.runtime import sha256_file


@dataclass
class LoadedConfig:
    path: Path
    data: dict[str, Any]

    @property
    def hash(self) -> str:
        return sha256_file(self.path)

    def get(self, *keys: str, default: Any = None) -> Any:
        current: Any = self.data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current


def _merge_dicts(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_dicts(result[key], value)
        else:
            result[key] = value
    return result


def load_config(path: str | Path) -> LoadedConfig:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    parent = raw.pop("extends", None)
    if parent:
        parent_path = (path.parent / parent).resolve()
        base = load_config(parent_path)
        data = _merge_dicts(base.data, raw)
    else:
        data = raw
    return LoadedConfig(path=path.resolve(), data=data)
