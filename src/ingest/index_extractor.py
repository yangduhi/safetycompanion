from __future__ import annotations

import re
from typing import Iterable


INDEX_PATTERN = re.compile(r"^(?P<keyword>.+?)\s+(?P<pages>\d+(?:,\s*\d+)*)$")


def extract_back_index(page_manifest: Iterable[dict]) -> list[dict]:
    items: list[dict] = []
    for page in page_manifest:
        if page["page_type"] != "index":
            continue
        for raw_line in page["text"].splitlines():
            line = raw_line.strip()
            match = INDEX_PATTERN.match(line)
            if not match:
                continue
            pages = [int(part.strip()) for part in match.group("pages").split(",")]
            items.append(
                {
                    "keyword": match.group("keyword").strip(),
                    "target_printed_pages": pages,
                    "target_pdf_pages": pages,
                    "source_pdf_page": page["pdf_page"],
                }
            )
    return items


def build_page_links(back_index: list[dict], calendar_entries: list[dict]) -> list[dict]:
    links: list[dict] = []
    for item in back_index:
        for target in item["target_pdf_pages"]:
            links.append(
                {
                    "link_type": "index",
                    "source": item["keyword"],
                    "target_pdf_page": target,
                }
            )
    for item in calendar_entries:
        links.append(
            {
                "link_type": "calendar",
                "source": item["title"],
                "target_pdf_page": item["target_page"],
            }
        )
    return links
