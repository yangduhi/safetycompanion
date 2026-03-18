from __future__ import annotations

from typing import Callable

from src.eval.utils import aggregate_boolean_metric


def evaluate_answers(gold_questions: list[dict], answer_query: Callable[[str], dict]) -> tuple[dict, list[dict]]:
    if not gold_questions:
        return (
            {
                "citation_page_hit_rate": 0.0,
                "citation_top1_hit_rate": 0.0,
                "grounded_success_rate": 0.0,
                "field_grounding_hit_rate": 0.0,
            },
            [],
        )
    details: list[dict] = []
    for question in gold_questions:
        payload = answer_query(question["question"])
        result = payload["answer"]
        trace = payload["trace"]
        evidence = result.get("evidence", [])
        pages = {item.get("pdf_page") for item in evidence}
        expected = set(question.get("expected_pdf_pages", []))
        expected_fields = set(question.get("expected_field_names", []))
        top1_page = evidence[0].get("pdf_page") if evidence else None
        evidence_fields = {item.get("field_name") for item in evidence if item.get("field_name")}
        field_hit = bool(expected_fields & evidence_fields) if expected_fields else bool(evidence_fields)
        citation_any_hit = bool(expected & pages)
        citation_top1_hit = top1_page in expected if top1_page is not None else False
        grounded = bool(
            result.get("answer")
            and result.get("answer") != "문서상 확인 불가"
            and citation_top1_hit
            and field_hit
            and evidence
            and evidence[0].get("text")
        )
        details.append(
            {
                "question": question["question"],
                "difficulty": question.get("difficulty", "unknown"),
                "question_type": question.get("question_type", "unknown"),
                "route": trace.get("route"),
                "route_name": result.get("route_name", trace.get("route")),
                "citation_any_hit": citation_any_hit,
                "citation_top1_hit": citation_top1_hit,
                "field_grounding_hit": field_hit,
                "grounded_success": grounded,
                "top1_page": top1_page,
                "top1_field": evidence[0].get("field_name") if evidence else None,
                "selected_field": result.get("selected_field"),
                "evidence_count": result.get("evidence_count", len(evidence)),
                "span_present": result.get("span_present", False),
                "template_answer_used": result.get("template_answer_used", False),
                "multi_page_used": result.get("multi_page_used", False),
                "graph_backfill_success": result.get("graph_backfill_used", False),
                "compare_pair_success": result.get("route_name") == "compare" and result.get("evidence_count", 0) >= 2,
                "answer_preview": result.get("answer", "")[:200],
            }
        )

    metrics: dict[str, float] = {}
    metrics.update(aggregate_boolean_metric(details, "citation_any_hit", "citation_page_hit_rate"))
    metrics.update(aggregate_boolean_metric(details, "citation_top1_hit", "citation_top1_hit_rate"))
    metrics.update(aggregate_boolean_metric(details, "field_grounding_hit", "field_grounding_hit_rate"))
    metrics.update(aggregate_boolean_metric(details, "grounded_success", "grounded_success_rate"))
    return metrics, details
