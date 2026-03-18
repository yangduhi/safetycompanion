from __future__ import annotations

import re
from typing import Iterable


CALENDAR_PATTERN = re.compile(
    r"^(?P<date>\d{1,2}.*?\d{4})\s*\|\s*(?P<location>[^|]+?)\s*\|\s*.*?p\.\s*(?P<page>\d+)\s*(?P<title>.*)$",
    re.IGNORECASE,
)


def _column_lines(raw_text: str, width: int = 62) -> tuple[list[str], list[str]]:
    left: list[str] = []
    right: list[str] = []
    for raw_line in raw_text.splitlines():
        if not raw_line.strip():
            continue
        left_col = raw_line[:width].strip()
        right_col = raw_line[width:].strip()
        if left_col:
            left.append(left_col)
        if right_col:
            right.append(right_col)
    return left, right


def _extract_from_column(lines: list[str], source_pdf_page: int) -> list[dict]:
    items: list[dict] = []
    idx = 0
    while idx < len(lines):
        line = lines[idx].replace("", "p.")
        match = CALENDAR_PATTERN.search(line)
        if not match:
            idx += 1
            continue
        title = match.group("title").strip()
        if not title and idx + 1 < len(lines):
            next_line = lines[idx + 1].strip()
            if "|" not in next_line and "Seminar Calendar" not in next_line:
                title = next_line
                idx += 1
        items.append(
            {
                "date": match.group("date").strip(),
                "location": match.group("location").strip(),
                "title": title or "Untitled Calendar Entry",
                "target_page": int(match.group("page")),
                "source_pdf_page": source_pdf_page,
            }
        )
        idx += 1
    return items


def extract_calendar_entries(page_manifest: Iterable[dict]) -> list[dict]:
    items: list[dict] = []
    for page in page_manifest:
        if page["page_type"] != "calendar":
            continue
        left, right = _column_lines(page.get("raw_text", page["text"]))
        items.extend(_extract_from_column(left, page["pdf_page"]))
        items.extend(_extract_from_column(right, page["pdf_page"]))
    return items
