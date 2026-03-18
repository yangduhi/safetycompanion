from __future__ import annotations

import re


def route_query(query: str, normalized_query: str | None = None, is_multi_page_hint: bool = False) -> str:
    lower = query.lower()
    normalized_lower = (normalized_query or query).lower()
    if re.fullmatch(r"[A-Za-z0-9+./-]{2,15}", query.strip()) or "약어" in query:
        return "abbreviation_lookup"
    if any(token in query for token in ["추천"]) or "recommend" in normalized_lower:
        return "recommendation"
    if any(token in query for token in ["비교", "차이"]) or "compare" in normalized_lower or "difference" in normalized_lower:
        return "compare"
    if is_multi_page_hint or any(token in query for token in ["두 개", "2개", "함께", "여러 페이지"]):
        return "multi_page_lookup"
    if "page" in normalized_lower or "페이지" in query or re.search(r"\bp\.\s*\d+\b", normalized_lower):
        return "page_or_index_lookup"
    if re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", query) or "calendar" in normalized_lower or "일정" in query:
        return "calendar_lookup"
    if any(token in query for token in ["관계", "관련성", "relationship"]):
        return "relationship_query"
    if any(token in normalized_lower for token in ["event", "conference", "summit"]):
        return "event_lookup"
    if any(token in normalized_lower for token in ["seminar", "course", "training", "lecture"]) or any(token in query for token in ["교육", "세미나", "강의", "과정"]):
        return "seminar_lookup"
    return "fallback_general"
