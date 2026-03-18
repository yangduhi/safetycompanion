from __future__ import annotations

from typing import Any, Iterable


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(str(item) for item in value if item)
    return str(value)


def build_chunks(
    entries: Iterable[dict],
    abbreviations: Iterable[dict],
    back_index: Iterable[dict],
    calendar_entries: Iterable[dict],
) -> list[dict]:
    chunks: list[dict] = []
    for entry in entries:
        base = {
            "entry_id": entry["entry_id"],
            "entry_bundle_id": entry["entry_bundle_id"],
            "title": entry["title"],
            "pdf_page": entry["source_pages"][0],
            "printed_page": entry["printed_pages"][0] if entry["printed_pages"] else None,
            "section_l1": entry["section_l1"],
            "entry_type": entry["entry_type"],
        }
        overview_text = entry.get("summary") or entry["title"]
        chunks.append(
            {
                **base,
                "chunk_id": f"{entry['entry_id']}_overview",
                "chunk_type": "entry_overview_chunk",
                "field_name": "overview",
                "text": overview_text,
                "is_primary_corpus": True,
            }
        )
        for field_name, raw_value in entry.get("fields", {}).items():
            text = _as_text(raw_value).strip()
            if not text:
                continue
            chunk_type = "knowledge_table_chunk" if entry["entry_type"] == "knowledge" and field_name == "table_headers" else "field_chunk"
            chunks.append(
                {
                    **base,
                    "chunk_id": f"{entry['entry_id']}_{field_name}",
                    "chunk_type": chunk_type,
                    "field_name": field_name,
                    "text": text,
                    "is_primary_corpus": True,
                }
            )
    for item in abbreviations:
        chunks.append(
            {
                "chunk_id": f"abbr_{item['abbr'].lower()}_{item['pdf_page']}",
                "entry_id": None,
                "entry_bundle_id": None,
                "title": item["abbr"],
                "pdf_page": item["pdf_page"],
                "printed_page": item["printed_page"],
                "section_l1": item.get("section_hint"),
                "entry_type": "abbreviation",
                "chunk_type": "abbreviation_chunk",
                "field_name": "expansion",
                "text": f"{item['abbr']} = {item['expansion']}",
                "is_primary_corpus": True,
            }
        )
    for item in back_index:
        chunks.append(
            {
                "chunk_id": f"index_{item['keyword']}",
                "entry_id": None,
                "entry_bundle_id": None,
                "title": item["keyword"],
                "pdf_page": item["source_pdf_page"],
                "printed_page": None,
                "section_l1": "Index",
                "entry_type": "index",
                "chunk_type": "index_lookup_chunk",
                "field_name": "keyword",
                "text": f"{item['keyword']} -> {item['target_pdf_pages']}",
                "is_primary_corpus": True,
            }
        )
    for item in calendar_entries:
        chunks.append(
            {
                "chunk_id": f"calendar_{item['source_pdf_page']}_{item['target_page']}_{item['title']}",
                "entry_id": None,
                "entry_bundle_id": None,
                "title": item["title"],
                "pdf_page": item["source_pdf_page"],
                "printed_page": None,
                "section_l1": "Seminar Calendar",
                "entry_type": "calendar",
                "chunk_type": "calendar_chunk",
                "field_name": "schedule",
                "text": f"{item['date']} | {item['location']} | p. {item['target_page']} | {item['title']}",
                "is_primary_corpus": False,
            }
        )
    return chunks
