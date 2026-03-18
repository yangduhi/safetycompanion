from __future__ import annotations


def extract_entities(entries: list[dict]) -> list[dict]:
    nodes: list[dict] = []
    for entry in entries:
        nodes.append(
            {
                "node_id": entry["entry_id"],
                "node_type": entry["entry_type"].title(),
                "name": entry["title"],
                "source_pages": entry.get("source_pages", []),
            }
        )
    return nodes
