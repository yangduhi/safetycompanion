from __future__ import annotations

from typing import Iterable


FIELD_PRIORITY_BY_ROUTE = {
    "abbreviation_lookup": ["expansion", "overview"],
    "page_or_index_lookup": ["page_summary", "knowledge_topic", "overview", "keyword"],
    "seminar_lookup": ["course_description", "course_objectives", "course_contents", "overview"],
    "event_lookup": ["description", "overview"],
    "calendar_lookup": ["course_description", "description", "overview", "schedule"],
    "compare_or_recommend": ["course_description", "course_contents", "description", "overview"],
    "relationship_query": ["page_summary", "description", "course_description", "overview"],
    "fallback_general": ["overview", "course_description", "page_summary", "description"],
}


def format_citation(item: dict) -> str:
    printed = item.get("printed_page")
    field_name = item.get("field_name")
    field_suffix = f", field {field_name}" if field_name else ""
    if printed is None:
        return f"{item.get('title', 'Untitled')} (pdf p.{item.get('pdf_page')}{field_suffix})"
    return f"{item.get('title', 'Untitled')} (pdf p.{item.get('pdf_page')}, printed p.{printed}{field_suffix})"


def _field_priority(route: str, field_name: str | None) -> int:
    if not field_name:
        return 999
    preferred = FIELD_PRIORITY_BY_ROUTE.get(route, FIELD_PRIORITY_BY_ROUTE["fallback_general"])
    if field_name in preferred:
        return preferred.index(field_name)
    return len(preferred) + 10


def select_evidence(route: str, candidates: list[dict], limit: int = 3) -> list[dict]:
    if not candidates:
        return []
    ranked = sorted(
        candidates,
        key=lambda item: (
            _field_priority(route, item.get("field_name")),
            -float(item.get("rerank_score", item.get("fused_score", item.get("score", 0.0)))),
        ),
    )
    selected: list[dict] = []
    seen: set[tuple] = set()
    seen_entries: set[str] = set()

    for item in ranked:
        dedupe_key = (item.get("chunk_id"), item.get("title"), item.get("pdf_page"), item.get("field_name"))
        if dedupe_key in seen:
            continue
        if route == "compare_or_recommend" and len(seen_entries) < 2:
            entry_id = item.get("entry_id")
            if entry_id and entry_id in seen_entries and len(ranked) > len(selected):
                continue
        seen.add(dedupe_key)
        if item.get("entry_id"):
            seen_entries.add(item["entry_id"])
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def build_grounded_answer(query: str, route: str, candidates: Iterable[dict]) -> dict:
    ranked = list(candidates)
    if not ranked:
        return {
            "query": query,
            "route": route,
            "answer": "문서상 확인 불가",
            "evidence": [],
        }
    selected = select_evidence(route, ranked)
    top = selected[0]
    evidence = [
        {
            "title": item.get("title"),
            "pdf_page": item.get("pdf_page"),
            "printed_page": item.get("printed_page"),
            "chunk_id": item.get("chunk_id"),
            "field_name": item.get("field_name"),
            "text": item.get("text", "")[:400],
        }
        for item in selected
    ]
    bullet_lines = [f"- {format_citation(item)}" for item in selected]
    if route == "compare_or_recommend" and len(selected) >= 2:
        summary_text = " / ".join(item.get("title", "Untitled") for item in selected[:2])
    else:
        summary_text = top.get("text", "")[:500].strip() or top.get("title", "문서상 확인 불가")
    answer = "\n".join(
        [
            f"질의 경로: {route}",
            f"가장 관련 높은 근거: {format_citation(top)}",
            "",
            "요약:",
            summary_text,
            "",
            "근거:",
            *bullet_lines,
        ]
    ).strip()
    return {
        "query": query,
        "route": route,
        "answer": answer,
        "evidence": evidence,
    }
