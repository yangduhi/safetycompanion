from __future__ import annotations


def evaluate_extraction(entries: list[dict], abbreviations: list[dict], calendar_entries: list[dict]) -> dict:
    total = len(entries)
    summaries = sum(1 for entry in entries if entry.get("summary"))
    return {
        "entry_count": total,
        "entry_summary_coverage": round(summaries / total, 4) if total else 0.0,
        "abbreviation_count": len(abbreviations),
        "calendar_entry_count": len(calendar_entries),
    }
