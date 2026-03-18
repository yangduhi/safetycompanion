from __future__ import annotations

import re
from dataclasses import dataclass

from src.common.text import compact_lines


SECTION_KEYWORDS = {
    "Dummy & Crash Testing": ["dummy | crash test", "dummy & crash test"],
    "Active Safety & Automated Driving": [
        "active safety | automated driving",
        "driver assistance",
        "automated driving",
    ],
    "Simulation & Engineering": ["simulation|engineering", "simulation & engineering"],
    "Passive Safety": ["passive safety"],
}

FIELD_HEADERS = {
    "course description",
    "course objectives",
    "who should attend?",
    "who should attend",
    "course contents",
    "facts",
}


@dataclass
class ClassifiedPage:
    page_type: str
    section_l1: str | None
    title: str
    extraction_quality: str
    is_primary_corpus: bool
    page_bundle_role: str


def detect_section(text: str) -> str | None:
    lower = text.lower()
    for section, keywords in SECTION_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return section
    if "important abbreviations" in lower:
        return "Important Abbreviations"
    if "\nindex" in lower or lower.startswith("index"):
        return "Index"
    if "seminar calendar 2026" in lower:
        return "Seminar Calendar"
    return None


def classify_page(pdf_page: int, text: str, word_count: int) -> str:
    lower = text.lower()
    head = "\n".join(compact_lines(text.splitlines())[:8]).lower()
    if "table of contents" in lower:
        return "toc"
    if "seminar guide" in lower or "safetywissen navigator" in lower:
        return "navigator_or_guide"
    if "preface" in lower or "your benefits" in lower or "in-house seminars" in lower:
        return "preface_or_meta"
    if "important abbreviations" in lower:
        return "abbreviations"
    if lower.startswith("index") or "\nindex" in lower:
        return "index"
    if "advertisers directory" in lower:
        return "advertisers_directory"
    if "general terms for the participation in seminars and events" in lower:
        return "terms"
    if "seminar calendar 2026" in lower:
        return "calendar"
    if "latest info about" in lower and "seminar" in lower:
        return "seminar"
    if "safetywissen.com" in lower and "wissen" in lower:
        return "knowledge"
    if re.search(r"\bevent\b", head):
        return "event"
    if pdf_page in {1, 2, 3, 4, 5, 224} or word_count <= 10:
        return "cover_or_brand"
    if word_count <= 25:
        return "low_text_image"
    if "www." in lower or "info@" in lower:
        return "advertisement"
    return "advertisement"


def extract_title(page_type: str, lines: list[str]) -> str:
    cleaned = compact_lines(lines)
    skip_contains = {
        "latest info about",
        "this course",
        "safetywissen.com",
        "wissen",
        "update",
        "new",
        "seminar guide",
        "table of contents",
        "event",
        "seminar",
    }
    filtered: list[str] = []
    for line in cleaned:
        lower = line.lower()
        if lower in skip_contains:
            continue
        if any(token in lower for token in ["passive safety", "dummy | crash test", "active safety | automated driving", "simulation|engineering"]):
            continue
        if lower in FIELD_HEADERS:
            break
        filtered.append(line)

    if not filtered:
        return f"{page_type.title()} page {lines[0] if lines else ''}".strip()

    if page_type in {"seminar", "event", "knowledge"}:
        return " ".join(filtered[:2]).strip()
    return filtered[0]


def detect_bundle_role(page_type: str, text: str) -> str:
    lower = text.lower()
    if page_type not in {"seminar", "event", "knowledge"}:
        return "non_retrieval"
    if "seminars by our partner" in lower:
        return "multi_entry"
    if "continued" in lower:
        return "continuation"
    return "single_entry"


def classify_page_record(pdf_page: int, text: str) -> ClassifiedPage:
    lines = text.splitlines()
    word_count = len(re.findall(r"\b\w+\b", text))
    page_type = classify_page(pdf_page, text, word_count)
    section_l1 = detect_section(text)
    title = extract_title(page_type, lines)
    extraction_quality = "low" if word_count < 20 else "medium"
    if page_type in {"seminar", "event", "knowledge", "abbreviations", "index"}:
        extraction_quality = "high" if word_count > 60 else "medium"
    is_primary_corpus = page_type in {"seminar", "event", "knowledge", "abbreviations", "index"}
    return ClassifiedPage(
        page_type=page_type,
        section_l1=section_l1,
        title=title,
        extraction_quality=extraction_quality,
        is_primary_corpus=is_primary_corpus,
        page_bundle_role=detect_bundle_role(page_type, text),
    )
