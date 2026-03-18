from __future__ import annotations

from typing import Callable

from src.eval.utils import aggregate_boolean_metric


def _title_hit(expected_titles: list[str], titles: list[str]) -> bool:
    lowered_titles = [title.lower() for title in titles]
    lowered_expected = [title.lower() for title in expected_titles]
    return any(any(expected in title for expected in lowered_expected) for title in lowered_titles)


def evaluate_retrieval(gold_questions: list[dict], retrieve: Callable[[str], list[dict]]) -> tuple[dict, list[dict]]:
    if not gold_questions:
        return (
            {
                "retrieval_top1_hit_rate": 0.0,
                "retrieval_top3_hit_rate": 0.0,
                "retrieval_top10_hit_rate": 0.0,
                "retrieval_page_hit_rate_top10": 0.0,
            },
            [],
        )
    details: list[dict] = []
    for question in gold_questions:
        results = retrieve(question["question"])[:10]
        expected_pages = set(question.get("expected_pdf_pages", []))
        expected_titles = question.get("expected_titles", [])
        top1 = results[:1]
        top3 = results[:3]
        top10 = results[:10]

        top1_pages = {row.get("pdf_page") for row in top1}
        top3_pages = {row.get("pdf_page") for row in top3}
        top10_pages = {row.get("pdf_page") for row in top10}
        top1_titles = [str(row.get("title", "")) for row in top1]
        top3_titles = [str(row.get("title", "")) for row in top3]
        top10_titles = [str(row.get("title", "")) for row in top10]

        details.append(
            {
                "question": question["question"],
                "difficulty": question.get("difficulty", "unknown"),
                "question_type": question.get("question_type", "unknown"),
                "expected_pdf_pages": sorted(expected_pages),
                "top1_hit": bool(expected_pages & top1_pages or _title_hit(expected_titles, top1_titles)),
                "top3_hit": bool(expected_pages & top3_pages or _title_hit(expected_titles, top3_titles)),
                "top10_hit": bool(expected_pages & top10_pages or _title_hit(expected_titles, top10_titles)),
                "page_hit_top10": bool(expected_pages & top10_pages),
                "top_result_title": top1_titles[0] if top1_titles else None,
                "top_result_page": next(iter(top1_pages), None) if top1_pages else None,
            }
        )

    metrics: dict[str, float] = {}
    metrics.update(aggregate_boolean_metric(details, "top1_hit", "retrieval_top1_hit_rate"))
    metrics.update(aggregate_boolean_metric(details, "top3_hit", "retrieval_top3_hit_rate"))
    metrics.update(aggregate_boolean_metric(details, "top10_hit", "retrieval_top10_hit_rate"))
    metrics.update(aggregate_boolean_metric(details, "page_hit_top10", "retrieval_page_hit_rate_top10"))
    metrics["recall_at_10"] = metrics["retrieval_top10_hit_rate"]
    metrics["page_hit_rate"] = metrics["retrieval_page_hit_rate_top10"]
    return metrics, details
