from __future__ import annotations

from src.graph.entity_extractor import extract_entities
from src.graph.relation_extractor import extract_relations


def build_graph(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    return extract_entities(entries), extract_relations(entries)
