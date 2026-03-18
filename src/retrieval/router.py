from __future__ import annotations

import re


def route_query(query: str) -> str:
    lower = query.lower()
    if re.fullmatch(r"[A-Za-z0-9+./-]{2,15}", query.strip()) or "약어" in query:
        return "abbreviation_lookup"
    if "page" in lower or "페이지" in query or re.search(r"\bp\.\s*\d+\b", lower):
        return "page_or_index_lookup"
    if re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", query) or "calendar" in lower or "일정" in query:
        return "calendar_lookup"
    if any(token in query for token in ["비교", "차이", "추천", "recommend", "compare"]):
        return "compare_or_recommend"
    if any(token in query for token in ["관계", "관련성", "relationship"]):
        return "relationship_query"
    if any(token in query.lower() for token in ["event", "conference", "summit"]):
        return "event_lookup"
    if any(token in query.lower() for token in ["seminar", "course", "교육", "세미나"]):
        return "seminar_lookup"
    return "fallback_general"
