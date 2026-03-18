from __future__ import annotations

from src.common.text import tokenize


FIELD_PRIORS = {
    "overview": 1.0,
    "course_contents": 1.15,
    "course_objectives": 1.1,
    "expansion": 1.2,
    "keyword": 1.05,
    "schedule": 1.05,
}


def rerank(query: str, candidates: list[dict], top_n: int = 5) -> list[dict]:
    query_terms = set(tokenize(query))
    rescored: list[dict] = []
    for item in candidates:
        terms = set(tokenize(item.get("text", ""))) | set(tokenize(item.get("title", "")))
        overlap = len(query_terms & terms)
        prior = FIELD_PRIORS.get(item.get("field_name"), 1.0)
        score = item.get("fused_score", item.get("score", 0.0)) + overlap * 0.25
        score *= prior
        row = dict(item)
        row["rerank_score"] = score
        rescored.append(row)
    return sorted(rescored, key=lambda item: item["rerank_score"], reverse=True)[:top_n]
