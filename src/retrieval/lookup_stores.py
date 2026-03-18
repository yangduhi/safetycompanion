from __future__ import annotations

from collections import defaultdict


def build_abbreviation_lookup(items: list[dict]) -> dict[str, list[dict]]:
    lookup: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        keys = {item["abbr"].lower(), *item.get("aliases", [])}
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
