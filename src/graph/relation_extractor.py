from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from src.graph.catalog import (
    canonical_topic,
    entry_fulltext,
    extract_dummy_families,
    extract_organizations,
    extract_standards,
    slugify,
)


def _base_edge(
    entry: dict,
    edge_type: str,
    target_id: str,
    source_field: str,
    provenance_text: str,
    confidence: float,
) -> dict:
    return {
        "edge_id": f"{entry['entry_id']}__{edge_type.lower()}__{slugify(target_id)}",
        "edge_type": edge_type,
        "source_id": f"entry:{entry['entry_id']}",
        "target_id": target_id,
        "source_entry_id": entry["entry_id"],
        "source_page": (entry.get("source_pages") or [None])[0],
        "source_field": source_field,
        "provenance_text": provenance_text[:500],
        "extraction_method": "heuristic",
        "confidence": confidence,
    }


def extract_relations(entries: list[dict]) -> list[dict]:
    edges: list[dict] = []
    shared_entities: defaultdict[tuple[str, str], list[str]] = defaultdict(list)

    for entry in entries:
        text = entry_fulltext(entry)
        topic = canonical_topic(entry.get("section_l1"))
        if topic:
            edges.append(
                _base_edge(
                    entry,
                    "BELONGS_TO_TOPIC",
                    f"topic:{slugify(topic)}",
                    "section_l1",
                    topic,
                    0.95,
                )
            )

        for dummy in extract_dummy_families(text):
            target_id = f"dummy:{slugify(dummy)}"
            edges.append(
                _base_edge(
                    entry,
                    "MENTIONS_DUMMY",
                    target_id,
                    "summary",
                    dummy,
                    0.9,
                )
            )
            shared_entities[("dummy", dummy)].append(entry["entry_id"])

        for standard in extract_standards(text):
            target_id = f"standard:{slugify(standard)}"
            edges.append(
                _base_edge(
                    entry,
                    "MENTIONS_STANDARD",
                    target_id,
                    "summary",
                    standard,
                    0.88,
                )
            )
            shared_entities[("standard", standard)].append(entry["entry_id"])

        for org in extract_organizations(text):
            target_id = f"org:{slugify(org)}"
            edges.append(
                _base_edge(
                    entry,
                    "MENTIONS_ORG",
                    target_id,
                    "summary",
                    org,
                    0.84,
                )
            )
            shared_entities[("org", org)].append(entry["entry_id"])

    for (entity_type, canonical_name), entry_ids in shared_entities.items():
        unique_entries = sorted(set(entry_ids))
        if len(unique_entries) < 2:
            continue
        for source_entry_id, target_entry_id in combinations(unique_entries, 2):
            edges.append(
                {
                    "edge_id": f"entry:{source_entry_id}__related_to_entry__entry:{target_entry_id}__{slugify(canonical_name)}",
                    "edge_type": "RELATED_TO_ENTRY",
                    "source_id": f"entry:{source_entry_id}",
                    "target_id": f"entry:{target_entry_id}",
                    "source_entry_id": source_entry_id,
                    "source_page": None,
                    "source_field": entity_type,
                    "provenance_text": canonical_name,
                    "extraction_method": "heuristic",
                    "confidence": 0.72,
                }
            )

    return edges
