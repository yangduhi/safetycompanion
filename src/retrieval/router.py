from __future__ import annotations

import re


def route_query(
    query: str,
    normalized_query: str | None = None,
    is_multi_page_hint: bool = False,
    compare_hint: bool = False,
    graph_relation_class: str | None = None,
    relationship_hint: bool = False,
    page_lookup_hint: bool = False,
    event_hint: bool = False,
) -> str:
    normalized_lower = (normalized_query or query).lower()

    if re.fullmatch(r"[A-Za-z0-9+./-]{2,15}", query.strip()) or any(token in normalized_lower for token in ["abbreviation", "stands for", "meaning"]):
        return "abbreviation_lookup"
    if any(token in normalized_lower for token in ["recommend", "suitable", "best match"]):
        return "recommendation"
    if compare_hint or "compare" in normalized_lower or "difference" in normalized_lower or "versus" in normalized_lower:
        return "compare"

    # Graph relation lanes should take precedence once the query profile already
    # resolved a specific graph relation class.
    if graph_relation_class == "topic_cluster_relation":
        return "topic_cluster_lookup"
    if graph_relation_class in {"dummy_family_relation", "standard_topic_relation", "organization_entry_relation"} and not page_lookup_hint:
        return "entity_relation_lookup"

    explicit_seminar_like = any(token in normalized_lower for token in ["seminar", "course", "training", "lecture"])
    if (event_hint or any(token in normalized_lower for token in ["event", "conference", "summit", "experience", "briefing", "update", "dialogue", "week"])) and not explicit_seminar_like:
        return "event_lookup"
    if relationship_hint and any(
        token in normalized_lower
        for token in [
            "thor",
            "hybrid iii",
            "hiii",
            "atd",
            "fmvss",
            "gtr",
            "un r",
            "euro ncap",
            "humanetics",
            "globalautoregs",
        ]
    ):
        return "entity_relation_lookup"
    if relationship_hint or "relationship" in normalized_lower or "related entr" in normalized_lower or "belongs to topic" in normalized_lower:
        return "relationship_query"
    if is_multi_page_hint or "multiple pages" in normalized_lower or "together" in normalized_lower:
        return "multi_page_lookup"
    if re.search(r"\d{1,2}\.\d{1,2}\.\d{4}", query) or "calendar" in normalized_lower or "schedule" in normalized_lower:
        return "calendar_lookup"
    if page_lookup_hint or "page" in normalized_lower or re.search(r"\bp\.\s*\d+\b", normalized_lower):
        return "page_or_index_lookup"
    if explicit_seminar_like:
        return "seminar_lookup"
    return "fallback_general"
