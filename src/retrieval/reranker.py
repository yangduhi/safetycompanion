from __future__ import annotations

import re

from src.retrieval.disambiguation import disambiguation_adjustment
from src.common.text import tokenize


FIELD_PRIORS = {
    "overview": 1.0,
    "course_contents": 1.15,
    "course_objectives": 1.1,
    "expansion": 1.2,
    "keyword": 1.05,
    "schedule": 1.05,
}


def _hard_negative_adjustment(query: str, item: dict, query_profile: dict | None = None) -> tuple[float, dict]:
    normalized_query = (query_profile or {}).get("normalized_query", query)
    lower_query = normalized_query.lower()
    text = f"{item.get('title', '')} {item.get('text', '')}".lower()
    score = 0.0
    features: dict[str, bool | float] = {}

    if "briefing" in lower_query and "briefing" not in text:
        score -= 0.4
        features["briefing_penalty"] = True
    if "introduction" in lower_query and "introduction" not in text and "basics" not in text:
        score -= 0.25
        features["introduction_penalty"] = True
    if "policy" in lower_query and "policy" in text:
        score += 0.3
        features["policy_boost"] = True

    query_standard_match = re.findall(r"fmvss\s*\d+[a-z]?", lower_query)
    if query_standard_match:
        for standard in query_standard_match:
            compact = standard.replace(" ", "")
            if compact in text.replace(" ", ""):
                score += 0.6
                features["standard_exact_boost"] = True
            elif "fmvss" in text:
                score -= 0.4
                features["standard_sibling_penalty"] = True
    return round(score, 4), features


def rerank(query: str, candidates: list[dict], top_n: int = 5, route: str = "fallback_general", query_profile: dict | None = None) -> list[dict]:
    normalized_query = (query_profile or {}).get("normalized_query", query)
    query_terms = set(tokenize(normalized_query))
    rescored: list[dict] = []
    for item in candidates:
        terms = set(tokenize(item.get("text", ""))) | set(tokenize(item.get("title", "")))
        overlap = len(query_terms & terms)
        prior = FIELD_PRIORS.get(item.get("field_name"), 1.0)
        score = item.get("fused_score", item.get("score", 0.0)) + overlap * 0.25
        score *= prior
        disambiguation_score, disambiguation_features = disambiguation_adjustment(query, route, item, query_profile=query_profile)
        hard_negative_score, hard_negative_features = _hard_negative_adjustment(query, item, query_profile=query_profile)
        score += disambiguation_score + hard_negative_score
        row = dict(item)
        row["rerank_score"] = round(score, 4)
        row["disambiguation_score"] = disambiguation_score
        row["hard_negative_score"] = hard_negative_score
        row["disambiguation_features"] = disambiguation_features
        row["hard_negative_features"] = hard_negative_features
        rescored.append(row)
    return sorted(rescored, key=lambda item: item["rerank_score"], reverse=True)[:top_n]
