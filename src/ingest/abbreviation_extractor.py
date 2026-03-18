from __future__ import annotations

import re
from typing import Iterable


def looks_like_abbreviation(token: str) -> bool:
    token = token.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9+./-]{1,15}", token):
        return False
    upper_count = sum(1 for char in token if char.isupper())
    lower_count = sum(1 for char in token if char.islower())
    digit_count = sum(1 for char in token if char.isdigit())
    if upper_count == 0:
        return False
    if token[0].isupper() and lower_count > 0 and upper_count == 1 and digit_count == 0:
        return False
    if lower_count > upper_count + digit_count and token[0].isupper():
        return False
    return True


def extract_abbreviations(page_manifest: Iterable[dict]) -> list[dict]:
    items: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for page in page_manifest:
        if page["page_type"] != "abbreviations":
            continue
        raw_text = page.get("raw_text", page["text"])
        for raw_line in raw_text.splitlines():
            segments = [segment.strip() for segment in re.split(r"\s{4,}", raw_line) if segment.strip()]
            for segment in segments:
                match = re.match(r"^(?P<abbr>[A-Za-z0-9][A-Za-z0-9+./-]{1,15})\s+(?P<exp>.+)$", segment)
                if not match:
                    continue
                abbr = match.group("abbr").strip()
                expansion = match.group("exp").strip()
                if not looks_like_abbreviation(abbr):
                    continue
                if len(expansion) < 3 or expansion.lower() == abbr.lower():
                    continue
                key = (abbr, page["pdf_page"])
                if key in seen:
                    continue
                seen.add(key)
                items.append(
                    {
                        "abbr": abbr,
                        "expansion": expansion,
                        "aliases": [abbr.lower()],
                        "section_hint": page["section_l1"],
                        "pdf_page": page["pdf_page"],
                        "printed_page": page["printed_page"],
                        "title": page["title"],
                    }
                )
    return items
