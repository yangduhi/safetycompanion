from __future__ import annotations

from typing import Callable


def evaluate_answers(gold_questions: list[dict], answer_query: Callable[[str], dict]) -> dict:
    if not gold_questions:
        return {
            "citation_page_hit_rate": 0.0,
            "grounded_success_rate": 0.0,
        }
    citation_hits = 0
    grounded_hits = 0
    for question in gold_questions:
        result = answer_query(question["question"])
        evidence = result.get("evidence", [])
        pages = {item.get("pdf_page") for item in evidence}
        expected = set(question.get("expected_pdf_pages", []))
        if expected & pages:
            citation_hits += 1
            grounded_hits += 1
    total = len(gold_questions)
    return {
        "citation_page_hit_rate": round(citation_hits / total, 4),
        "grounded_success_rate": round(grounded_hits / total, 4),
    }
