from __future__ import annotations

from collections import defaultdict

from src.common.policy import normalize_abbreviation_key


def build_abbreviation_lookup(items: list[dict]) -> dict[str, list[dict]]:
    lookup: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        keys = {item["abbr"].lower(), normalize_abbreviation_key(item["abbr"]), *item.get("aliases", [])}
        for key in keys:
            lookup[key].append(item)
    return dict(lookup)


def build_index_lookup(items: list[dict]) -> dict[str, list[dict]]:
    lookup: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        lookup[item["keyword"].lower()].append(item)
    return dict(lookup)


def build_calendar_lookup(items: list[dict]) -> dict[str, list[dict]]:
    lookup: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        lookup[item["title"].lower()].append(item)
        lookup[item["date"].lower()].append(item)
        lookup[item["location"].lower()].append(item)
    return dict(lookup)
