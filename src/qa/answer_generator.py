from __future__ import annotations

from typing import Iterable


def format_citation(item: dict) -> str:
    printed = item.get("printed_page")
    if printed is None:
        return f"{item.get('title', 'Untitled')} (pdf p.{item.get('pdf_page')})"
    return f"{item.get('title', 'Untitled')} (pdf p.{item.get('pdf_page')}, printed p.{printed})"


def build_grounded_answer(query: str, route: str, candidates: Iterable[dict]) -> dict:
    ranked = list(candidates)
    if not ranked:
        return {
            "query": query,
            "route": route,
            "answer": "문서상 확인 불가",
            "evidence": [],
        }
    top = ranked[0]
    evidence = [
        {
            "title": item.get("title"),
            "pdf_page": item.get("pdf_page"),
            "printed_page": item.get("printed_page"),
            "chunk_id": item.get("chunk_id"),
            "field_name": item.get("field_name"),
            "text": item.get("text", "")[:400],
        }
        for item in ranked[:3]
    ]
    bullet_lines = [f"- {format_citation(item)}" for item in ranked[:3]]
    answer = "\n".join(
        [
            f"질의 경로: {route}",
            f"가장 관련 높은 근거: {format_citation(top)}",
            "",
            "요약:",
            top.get("text", "")[:500].strip() or top.get("title", "문서상 확인 불가"),
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
