from __future__ import annotations

import re
from typing import Iterable

from src.common.text import slugify, split_blocks


SEMINAR_HEADERS = [
    "Course Description",
    "Course Objectives",
    "Who should attend?",
    "Course Contents",
    "Facts",
]


def _section_positions(text: str, headers: list[str]) -> list[tuple[int, str, int]]:
    positions: list[tuple[int, str, int]] = []
    lowered = text.lower()
    for header in headers:
        idx = lowered.find(header.lower())
        if idx >= 0:
            positions.append((idx, header, idx + len(header)))
    return sorted(positions)


def split_seminar_sections(text: str) -> dict[str, str]:
    positions = _section_positions(text, SEMINAR_HEADERS)
    if not positions:
        return {"body": text.strip()}
    sections: dict[str, str] = {}
    for idx, (start, header, end) in enumerate(positions):
        next_start = positions[idx + 1][0] if idx + 1 < len(positions) else len(text)
        sections[header.lower().replace(" ", "_").replace("?", "")] = text[end:next_start].strip()
    intro = text[: positions[0][0]].strip()
    if intro:
        sections["body"] = intro
    return sections


def extract_summary(text: str, max_blocks: int = 2) -> str:
    blocks = split_blocks(text)
    return " ".join(blocks[:max_blocks]).strip()


def extract_entities(text: str) -> list[str]:
    entities = sorted(
        {
            token
            for token in re.findall(r"\b[A-Z][A-Z0-9.+/-]{1,}\b", text)
            if len(token) > 2
        }
    )
    return entities[:25]


def _seminar_entry(page: dict) -> dict:
    fields = split_seminar_sections(page["text"])
    return {
        "document_id": page["document_id"],
        "entry_id": f"sc2026_p{page['pdf_page']:03d}_{slugify(page['title'])}",
        "entry_bundle_id": f"bundle_p{page['pdf_page']:03d}_{slugify(page['title'])}",
        "entry_type": "seminar",
        "title": page["title"],
        "subtitle": None,
        "is_new": "new" in page["text"].lower(),
        "section_l1": page["section_l1"],
        "summary": extract_summary(page["text"]),
        "source_pages": [page["pdf_page"]],
        "printed_pages": [page["printed_page"]] if page["printed_page"] is not None else [],
        "fields": {
            "course_description": fields.get("course_description", fields.get("body")),
            "course_objectives": fields.get("course_objectives"),
            "who_should_attend": fields.get("who_should_attend"),
            "course_contents": fields.get("course_contents"),
            "facts": fields.get("facts"),
        },
        "facts": {
            "partner": "Seminars by our Partner" if "seminars by our partner" in page["text"].lower() else None
        },
    }


def _event_entry(page: dict) -> dict:
    return {
        "document_id": page["document_id"],
        "entry_id": f"sc2026_p{page['pdf_page']:03d}_{slugify(page['title'])}",
        "entry_bundle_id": f"bundle_p{page['pdf_page']:03d}_{slugify(page['title'])}",
        "entry_type": "event",
        "title": page["title"],
        "subtitle": None,
        "is_new": "new" in page["text"].lower(),
        "section_l1": page["section_l1"],
        "summary": extract_summary(page["text"], max_blocks=3),
        "source_pages": [page["pdf_page"]],
        "printed_pages": [page["printed_page"]] if page["printed_page"] is not None else [],
        "fields": {
            "description": extract_summary(page["text"], max_blocks=4),
            "contents": None,
        },
        "facts": {},
    }


def _knowledge_entry(page: dict) -> dict:
    lines = [line for line in page["text"].splitlines() if line.strip()]
    table_headers = lines[1:4]
    return {
        "document_id": page["document_id"],
        "entry_id": f"sc2026_p{page['pdf_page']:03d}_{slugify(page['title'])}",
        "entry_bundle_id": f"bundle_p{page['pdf_page']:03d}_{slugify(page['title'])}",
        "entry_type": "knowledge",
        "title": page["title"],
        "subtitle": None,
        "is_new": "new" in page["text"].lower(),
        "section_l1": page["section_l1"],
        "summary": extract_summary(page["text"], max_blocks=2),
        "source_pages": [page["pdf_page"]],
        "printed_pages": [page["printed_page"]] if page["printed_page"] is not None else [],
        "fields": {
            "knowledge_topic": page["title"],
            "table_headers": table_headers,
            "key_points": lines[4:14],
            "page_summary": extract_summary(page["text"], max_blocks=2),
            "mentioned_entities": extract_entities(page["text"]),
        },
        "facts": {},
    }


def extract_entries(page_manifest: Iterable[dict]) -> list[dict]:
    records: list[dict] = []
    for page in page_manifest:
        if page["page_type"] == "seminar":
            records.append(_seminar_entry(page))
        elif page["page_type"] == "event":
            records.append(_event_entry(page))
        elif page["page_type"] == "knowledge":
            records.append(_knowledge_entry(page))
    return records


def build_extraction_quality_report(entries: list[dict]) -> str:
    total = len(entries)
    by_type: dict[str, int] = {}
    missing_summary = 0
    for entry in entries:
        by_type[entry["entry_type"]] = by_type.get(entry["entry_type"], 0) + 1
        if not entry.get("summary"):
            missing_summary += 1
    lines = [
        "# Extraction Quality Report",
        "",
        f"- total entries: {total}",
        f"- entries without summary: {missing_summary}",
        "",
        "## Entries by Type",
    ]
    for key in sorted(by_type):
        lines.append(f"- {key}: {by_type[key]}")
    return "\n".join(lines) + "\n"
