from __future__ import annotations

import re
import subprocess
from pathlib import Path

from src.common.config import LoadedConfig
from src.common.runtime import ensure_dir
from src.common.text import compact_lines
from src.parse.opendataloader_parser import parse_pages_with_opendataloader
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


def _page_manifest_row(
    pdf_page: int,
    raw_text: str,
    document_id: str,
    parser_engine: str,
    parser_mode: str,
    printed_page_hint: int | None = None,
) -> dict:
    lines = compact_lines(raw_text.splitlines())
    text = "\n".join(lines)
    classification = classify_page_record(pdf_page, text)
    word_count = len(re.findall(r"\b\w+\b", text))
    printed_page = printed_page_hint if printed_page_hint is not None else guess_printed_page(pdf_page, lines)
    return {
        "document_id": document_id,
        "pdf_page": pdf_page,
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
        "parser_engine": parser_engine,
        "parser_mode": parser_mode,
    }


def _page_blocks_row(pdf_page: int, raw_text: str, document_id: str, printed_page: int | None, parser_engine: str) -> dict:
    return {
        "document_id": document_id,
        "pdf_page": pdf_page,
        "printed_page": printed_page,
        "parser_engine": parser_engine,
        "blocks": [
            {
                "block_id": f"p{pdf_page:03d}_b{block_idx:03d}",
                "text": line,
                "raw_text": raw_line.rstrip(),
                "reading_order": block_idx,
            }
            for block_idx, raw_line in enumerate(raw_text.splitlines(), start=1)
            if raw_line.strip()
            for line in [raw_line.strip()]
        ],
    }


def select_auxiliary_pages(page_manifest: list[dict], config: LoadedConfig) -> list[int]:
    if not bool(config.get("parse", "auxiliary", "enabled", default=False)):
        return []
    engine = str(config.get("parse", "auxiliary", "engine", default="")).lower()
    if engine != "opendataloader":
        return []

    allowed_types = {
        str(page_type).strip()
        for page_type in config.get("parse", "auxiliary", "page_types", default=["knowledge"])
        if str(page_type).strip()
    }
    min_word_count = int(config.get("parse", "auxiliary", "min_word_count", default=0) or 0)
    whitelist_pages = {
        int(page)
        for page in config.get("parse", "auxiliary", "page_numbers", default=[]) or []
        if str(page).strip()
    }
    return [
        int(page["pdf_page"])
        for page in page_manifest
        if page.get("page_type") in allowed_types
        and int(page.get("word_count", 0)) >= min_word_count
        and (not whitelist_pages or int(page["pdf_page"]) in whitelist_pages)
    ]


def _apply_auxiliary_parser(
    page_manifest: list[dict],
    page_blocks: list[dict],
    pdf_path: Path,
    document_id: str,
    temp_dir: Path,
    config: LoadedConfig,
) -> tuple[list[dict], list[dict], dict]:
    diagnostics = {
        "primary_engine": "pdftotext",
        "auxiliary_enabled": bool(config.get("parse", "auxiliary", "enabled", default=False)),
        "auxiliary_engine": config.get("parse", "auxiliary", "engine", default=None),
        "candidate_pages": [],
        "reparsed_pages": [],
        "fallback_reason": None,
    }
    candidate_pages = select_auxiliary_pages(page_manifest, config)
    diagnostics["candidate_pages"] = candidate_pages
    if not candidate_pages:
        return page_manifest, page_blocks, diagnostics

    strict = bool(config.get("parse", "auxiliary", "strict", default=False))
    try:
        repl_texts = parse_pages_with_opendataloader(pdf_path, candidate_pages, temp_dir / "auxiliary", config)
    except Exception as exc:
        diagnostics["fallback_reason"] = str(exc)
        if strict:
            raise
        return page_manifest, page_blocks, diagnostics

    manifest_by_page = {int(row["pdf_page"]): dict(row) for row in page_manifest}
    blocks_by_page = {int(row["pdf_page"]): dict(row) for row in page_blocks}

    for pdf_page in candidate_pages:
        raw_text = repl_texts.get(pdf_page)
        if not raw_text:
            continue
        current = manifest_by_page[pdf_page]
        updated = _page_manifest_row(
            pdf_page=pdf_page,
            raw_text=raw_text,
            document_id=document_id,
            parser_engine="opendataloader",
            parser_mode=str(config.get("parse", "auxiliary", "mode", default="local")),
            printed_page_hint=current.get("printed_page"),
        )
        updated["primary_parser_engine"] = current.get("parser_engine", "pdftotext")
        manifest_by_page[pdf_page] = updated
        blocks_by_page[pdf_page] = _page_blocks_row(
            pdf_page=pdf_page,
            raw_text=raw_text,
            document_id=document_id,
            printed_page=updated.get("printed_page"),
            parser_engine="opendataloader",
        )
        diagnostics["reparsed_pages"].append(pdf_page)

    manifest = [manifest_by_page[index] for index in sorted(manifest_by_page)]
    blocks = [blocks_by_page[index] for index in sorted(blocks_by_page)]
    return manifest, blocks, diagnostics


def build_page_records(pdf_path: Path, document_id: str, temp_dir: Path, config: LoadedConfig) -> tuple[list[dict], list[dict], dict]:
    raw_pages = extract_text_pages(pdf_path, temp_dir)
    manifest: list[dict] = []
    blocks: list[dict] = []
    for index, raw_text in enumerate(raw_pages, start=1):
        row = _page_manifest_row(
            pdf_page=index,
            raw_text=raw_text,
            document_id=document_id,
            parser_engine="pdftotext",
            parser_mode="primary",
        )
        manifest.append(row)
        blocks.append(
            _page_blocks_row(
                pdf_page=index,
                raw_text=raw_text,
                document_id=document_id,
                printed_page=row.get("printed_page"),
                parser_engine="pdftotext",
            )
        )
    return _apply_auxiliary_parser(manifest, blocks, pdf_path, document_id, temp_dir, config)


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


def build_parse_report(manifest: list[dict], diagnostics: dict | None = None) -> str:
    counts: dict[str, int] = {}
    parser_counts: dict[str, int] = {}
    low_text_pages: list[int] = []
    missing_title_pages: list[int] = []
    for row in manifest:
        counts[row["page_type"]] = counts.get(row["page_type"], 0) + 1
        parser_counts[str(row.get("parser_engine", "unknown"))] = parser_counts.get(str(row.get("parser_engine", "unknown")), 0) + 1
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
            "## Parser Engines",
        ]
    )
    for key in sorted(parser_counts):
        lines.append(f"- {key}: {parser_counts[key]}")
    if diagnostics:
        lines.extend(
            [
                "",
                "## Auxiliary Parser",
                f"- enabled: {bool(diagnostics.get('auxiliary_enabled'))}",
                f"- engine: {diagnostics.get('auxiliary_engine')}",
                f"- candidate_pages: {diagnostics.get('candidate_pages', [])}",
                f"- reparsed_pages: {diagnostics.get('reparsed_pages', [])}",
                f"- fallback_reason: {diagnostics.get('fallback_reason')}",
            ]
        )
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
