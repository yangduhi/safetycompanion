from __future__ import annotations

import re
import subprocess
from pathlib import Path

from src.common.runtime import ensure_dir
from src.common.text import compact_lines
from src.parse.page_classifier import classify_page_record


def extract_text_pages(pdf_path: Path, temp_dir: Path) -> list[str]:
    ensure_dir(temp_dir)
    out_path = temp_dir / f"{pdf_path.stem}.layout.txt"
    command = ["pdftotext", "-layout", str(pdf_path), str(out_path)]
    subprocess.run(command, check=True, capture_output=True)
    text = out_path.read_text(encoding="utf-8", errors="replace")
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    return pages


def guess_printed_page(pdf_page: int, lines: list[str]) -> int | None:
    cleaned = compact_lines(lines)
    for line in reversed(cleaned[-4:]):
        if re.fullmatch(r"\d{1,3}", line):
            return int(line)
    if 6 <= pdf_page <= 223:
        return pdf_page
    return None


def build_page_records(pdf_path: Path, document_id: str, temp_dir: Path) -> tuple[list[dict], list[dict]]:
    raw_pages = extract_text_pages(pdf_path, temp_dir)
    manifest: list[dict] = []
    blocks: list[dict] = []
    for index, raw_text in enumerate(raw_pages, start=1):
        lines = compact_lines(raw_text.splitlines())
        text = "\n".join(lines)
        classification = classify_page_record(index, text)
        word_count = len(re.findall(r"\b\w+\b", text))
        printed_page = guess_printed_page(index, lines)
        manifest.append(
            {
                "document_id": document_id,
                "pdf_page": index,
                "printed_page": printed_page,
                "page_type": classification.page_type,
                "section_l1": classification.section_l1,
                "title": classification.title,
                "text": text,
                "raw_text": raw_text,
                "word_count": word_count,
                "extraction_quality": classification.extraction_quality,
                "is_primary_corpus": classification.is_primary_corpus,
                "page_bundle_role": classification.page_bundle_role,
            }
        )
        blocks.append(
            {
                "document_id": document_id,
                "pdf_page": index,
                "printed_page": printed_page,
                "blocks": [
                    {
                        "block_id": f"p{index:03d}_b{block_idx:03d}",
                        "text": line,
                        "raw_text": raw_line.rstrip(),
                        "reading_order": block_idx,
                    }
                    for block_idx, raw_line in enumerate(raw_text.splitlines(), start=1)
                    if raw_line.strip()
                    for line in [raw_line.strip()]
                ],
            }
        )
    return manifest, blocks


def build_source_page_map(manifest: list[dict]) -> list[dict]:
    return [
        {
            "pdf_page": row["pdf_page"],
            "printed_page": row["printed_page"],
            "section_l1": row["section_l1"],
            "page_type_guess": row["page_type"],
            "has_text_layer": True,
            "low_text_flag": row["word_count"] < 20,
            "is_primary_corpus": row["is_primary_corpus"],
            "notes": None,
        }
        for row in manifest
    ]


def build_parse_report(manifest: list[dict]) -> str:
    counts: dict[str, int] = {}
    low_text_pages: list[int] = []
    missing_title_pages: list[int] = []
    for row in manifest:
        counts[row["page_type"]] = counts.get(row["page_type"], 0) + 1
        if row["word_count"] < 20:
            low_text_pages.append(row["pdf_page"])
        if not row["title"]:
            missing_title_pages.append(row["pdf_page"])
    lines = [
        "# Parse Report",
        "",
        f"- total pages: {len(manifest)}",
        "",
        "## Page Type Counts",
    ]
    for key in sorted(counts):
        lines.append(f"- {key}: {counts[key]}")
    lines.extend(
        [
            "",
            "## Low Text Pages",
            f"- {low_text_pages}",
            "",
            "## Missing Titles",
            f"- {missing_title_pages}",
        ]
    )
    return "\n".join(lines) + "\n"
