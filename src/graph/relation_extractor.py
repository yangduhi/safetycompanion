from __future__ import annotations


def extract_relations(entries: list[dict]) -> list[dict]:
    edges: list[dict] = []
    for entry in entries:
        section = entry.get("section_l1")
        if not section:
            continue
        edges.append(
            {
                "edge_id": f"{entry['entry_id']}__section",
                "source_id": entry["entry_id"],
                "target_id": section,
                "edge_type": "BELONGS_TO_TOPIC",
                "source_page": entry.get("source_pages", [None])[0],
                "provenance_text": entry.get("summary"),
                "confidence": 0.5,
            }
        )
    return edges
