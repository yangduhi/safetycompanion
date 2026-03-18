from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.common.config import LoadedConfig


def load_route_policy(root: Path, config: LoadedConfig) -> dict[str, Any]:
    rel_path = config.get("paths", "route_field_priority", default="configs/route_field_priority.yaml")
    path = root / rel_path
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("routes", {})


def route_policy_for(route_policy: dict[str, Any], route_name: str) -> dict[str, Any]:
    return route_policy.get(route_name, route_policy.get("fallback_general", {}))


def normalize_abbreviation_key(text: str) -> str:
    return "".join(char.lower() for char in text if char.isascii() and char.isalnum())
