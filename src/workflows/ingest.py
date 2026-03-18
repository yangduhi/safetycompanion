from __future__ import annotations

from src.common.pipeline import RunContext
from src.common.runtime import ensure_dir, write_json, write_jsonl, write_text
from src.eval.extraction_eval import evaluate_extraction
from src.eval.parse_eval import evaluate_parse
from src.ingest.abbreviation_extractor import extract_abbreviations
from src.ingest.calendar_extractor import extract_calendar_entries
from src.ingest.entry_extractor import build_extraction_quality_report, extract_entries
from src.ingest.index_extractor import build_page_links, extract_back_index
from src.parse.pdf_parser import build_page_records, build_parse_report, build_source_page_map
from src.workflows.result import WorkflowResult


def run_ingest(ctx: RunContext) -> WorkflowResult:
    parse_tmp = ensure_dir(ctx.root / "tmp" / "pdfs")
    page_manifest, page_blocks = build_page_records(ctx.pdf_path, ctx.config.get("document", "id"), parse_tmp)
    source_page_map = build_source_page_map(page_manifest)
    parse_report = build_parse_report(page_manifest)

    entries = extract_entries(page_manifest)
    abbreviations = extract_abbreviations(page_manifest)
    back_index = extract_back_index(page_manifest)
    calendar_entries = extract_calendar_entries(page_manifest)
    page_links = build_page_links(back_index, calendar_entries)
    extraction_report = build_extraction_quality_report(entries)

    write_jsonl(ctx.path_from_config("page_manifest"), page_manifest)
    write_jsonl(ctx.path_from_config("page_blocks"), page_blocks)
    write_jsonl(ctx.path_from_config("source_map"), source_page_map)
    write_jsonl(ctx.path_from_config("entries"), entries)
    write_jsonl(ctx.path_from_config("abbreviations"), abbreviations)
    write_jsonl(ctx.path_from_config("back_index"), back_index)
    write_jsonl(ctx.path_from_config("calendar_entries"), calendar_entries)
    write_jsonl(ctx.path_from_config("page_links"), page_links)

    parse_report_path = ctx.output_path("parse_report.md")
    extraction_report_path = ctx.output_path("extraction_quality_report.md")
    page_review_queue_path = ctx.output_path("page_review_queue.json")
    source_audit_report_path = ctx.output_path("source_audit_report.md")

    low_confidence = [
        {"pdf_page": page["pdf_page"], "page_type": page["page_type"], "title": page["title"]}
        for page in page_manifest
        if page["extraction_quality"] != "high"
    ]
    write_text(parse_report_path, parse_report)
    write_text(extraction_report_path, extraction_report)
    write_json(page_review_queue_path, low_confidence[:50])
    write_text(
        source_audit_report_path,
        "\n".join(
            [
                "# Source Audit Report",
                "",
                f"- total pages: {len(page_manifest)}",
                f"- entries: {len(entries)}",
                f"- abbreviations: {len(abbreviations)}",
                f"- back index rows: {len(back_index)}",
                f"- calendar rows: {len(calendar_entries)}",
            ]
        )
        + "\n",
    )

    metrics = {}
    metrics.update(evaluate_parse(page_manifest))
    metrics.update(evaluate_extraction(entries, abbreviations, calendar_entries))
    return WorkflowResult(
        artifacts=[
            ctx.path_from_config("page_manifest"),
            ctx.path_from_config("entries"),
            parse_report_path,
            extraction_report_path,
            page_review_queue_path,
            source_audit_report_path,
        ],
        metrics=metrics,
        output_text=f"Ingest complete. Run: {ctx.run_id}",
    )
