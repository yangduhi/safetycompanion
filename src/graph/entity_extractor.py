from __future__ import annotations

from src.graph.catalog import (
    aggregate_node_sources,
    canonical_topic,
    entry_fulltext,
    extract_dummy_families,
    extract_organizations,
    extract_standards,
    slugify,
)


def _entry_node(entry: dict) -> dict:
    return {
        "node_id": f"entry:{entry['entry_id']}",
        "node_type": "Entry",
        "name": entry["title"],
        "canonical_name": entry["title"],
        "source_entry_ids": [entry["entry_id"]],
        "source_pages": entry.get("source_pages", []),
        "source_fields": ["summary"],
        "confidence": 1.0,
    }


def extract_entities(entries: list[dict]) -> list[dict]:
    nodes: list[dict] = []
    topic_sources = aggregate_node_sources()
    dummy_sources = aggregate_node_sources()
    standard_sources = aggregate_node_sources()
    org_sources = aggregate_node_sources()

    for entry in entries:
        nodes.append(_entry_node(entry))
        fulltext = entry_fulltext(entry)
        source_page = (entry.get("source_pages") or [None])[0]

        topic = canonical_topic(entry.get("section_l1"))
        if topic:
            key = f"topic:{slugify(topic)}"
            topic_sources[key]["name"] = topic
            topic_sources[key]["source_entry_ids"].add(entry["entry_id"])
            if source_page is not None:
                topic_sources[key]["source_pages"].add(source_page)
            topic_sources[key]["source_fields"].add("section_l1")

        for dummy in extract_dummy_families(fulltext):
            key = f"dummy:{slugify(dummy)}"
            dummy_sources[key]["name"] = dummy
            dummy_sources[key]["source_entry_ids"].add(entry["entry_id"])
            if source_page is not None:
                dummy_sources[key]["source_pages"].add(source_page)
            dummy_sources[key]["source_fields"].add("summary")

        for standard in extract_standards(fulltext):
            key = f"standard:{slugify(standard)}"
            standard_sources[key]["name"] = standard
            standard_sources[key]["source_entry_ids"].add(entry["entry_id"])
            if source_page is not None:
                standard_sources[key]["source_pages"].add(source_page)
            standard_sources[key]["source_fields"].add("summary")

        for org in extract_organizations(fulltext):
            key = f"org:{slugify(org)}"
            org_sources[key]["name"] = org
            org_sources[key]["source_entry_ids"].add(entry["entry_id"])
            if source_page is not None:
                org_sources[key]["source_pages"].add(source_page)
            org_sources[key]["source_fields"].add("summary")

    for node_id, payload in topic_sources.items():
        nodes.append(
            {
                "node_id": node_id,
                "node_type": "Topic",
                "name": payload["name"],
                "canonical_name": payload["name"],
                "source_entry_ids": sorted(payload["source_entry_ids"]),
                "source_pages": sorted(payload["source_pages"]),
                "source_fields": sorted(payload["source_fields"]),
                "confidence": 0.9,
            }
        )
    for node_id, payload in dummy_sources.items():
        nodes.append(
            {
                "node_id": node_id,
                "node_type": "DummyFamily",
                "name": payload["name"],
                "canonical_name": payload["name"],
                "source_entry_ids": sorted(payload["source_entry_ids"]),
                "source_pages": sorted(payload["source_pages"]),
                "source_fields": sorted(payload["source_fields"]),
                "confidence": 0.9,
            }
        )
    for node_id, payload in standard_sources.items():
        nodes.append(
            {
                "node_id": node_id,
                "node_type": "Standard",
                "name": payload["name"],
                "canonical_name": payload["name"],
                "source_entry_ids": sorted(payload["source_entry_ids"]),
                "source_pages": sorted(payload["source_pages"]),
                "source_fields": sorted(payload["source_fields"]),
                "confidence": 0.85,
            }
        )
    for node_id, payload in org_sources.items():
        nodes.append(
            {
                "node_id": node_id,
                "node_type": "Organization",
                "name": payload["name"],
                "canonical_name": payload["name"],
                "source_entry_ids": sorted(payload["source_entry_ids"]),
                "source_pages": sorted(payload["source_pages"]),
                "source_fields": sorted(payload["source_fields"]),
                "confidence": 0.85,
            }
        )

    return nodes
