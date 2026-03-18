from __future__ import annotations


def evaluate_parse(page_manifest: list[dict]) -> dict:
    primary = [page for page in page_manifest if page["page_type"] in {"seminar", "event"}]
    titled = [page for page in primary if page.get("title")]
    return {
        "page_manifest_coverage": len(page_manifest),
        "seminar_event_title_extraction_accuracy": round(len(titled) / len(primary), 4) if primary else 0.0,
    }
