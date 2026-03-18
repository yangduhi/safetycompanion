from __future__ import annotations

from typing import Callable


def evaluate_retrieval(gold_questions: list[dict], retrieve: Callable[[str], list[dict]]) -> dict:
    if not gold_questions:
        return {
            "recall_at_10": 0.0,
            "page_hit_rate": 0.0,
        }
    hits = 0
    page_hits = 0
    for question in gold_questions:
        results = retrieve(question["question"])[:10]
        expected_pages = set(question.get("expected_pdf_pages", []))
        expected_titles = [title.lower() for title in question.get("expected_titles", [])]
        pages = {row.get("pdf_page") for row in results}
        titles = [str(row.get("title", "")).lower() for row in results]
        if expected_pages & pages:
            page_hits += 1
        if any(any(expected in title for expected in expected_titles) for title in titles) or expected_pages & pages:
            hits += 1
    total = len(gold_questions)
    return {
        "recall_at_10": round(hits / total, 4),
        "page_hit_rate": round(page_hits / total, 4),
    }
