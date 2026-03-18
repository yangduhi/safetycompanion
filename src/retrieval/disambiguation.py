from __future__ import annotations

import re

from src.common.text import tokenize


STANDARD_PATTERN = re.compile(r"\b(?:FMVSS\s*\d+[A-Za-z]?|UN\s*R\s*\d+[A-Za-z]?|R\d+[A-Za-z]?|GTR\s*\d+)\b", re.IGNORECASE)

FAMILY_GROUPS = {
    "ncap": ["euro ncap", "c-ncap", "u.s. ncap", "us ncap", "kncap", "asean ncap", "jncap"],
    "safety_domain": ["active safety", "passive safety"],
    "dummy": ["dummy", "atd", "thor", "hiii", "hybrid iii"],
}

SECTION_HINTS = {
    "passive safety": "Passive Safety",
    "active safety": "Active Safety & Automated Driving",
    "automated driving": "Active Safety & Automated Driving",
    "dummy": "Dummy & Crash Testing",
    "crash test": "Dummy & Crash Testing",
    "biomechanics": "Simulation & Engineering",
}


def _extract_standards(text: str) -> list[str]:
    return [match.group(0).lower().replace(" ", "") for match in STANDARD_PATTERN.finditer(text)]


def _extract_family_hits(text: str) -> dict[str, list[str]]:
    lower = text.lower()
    hits: dict[str, list[str]] = {}
    for family, terms in FAMILY_GROUPS.items():
        matched = [term for term in terms if term in lower]
        if matched:
            hits[family] = matched
    return hits


def _title_overlap(query_terms: set[str], title: str) -> float:
    title_terms = set(tokenize(title))
    if not query_terms or not title_terms:
        return 0.0
    return len(query_terms & title_terms) / max(len(query_terms), 1)


def disambiguation_adjustment(query: str, route: str, item: dict, query_profile: dict | None = None) -> tuple[float, dict]:
    query_profile = query_profile or {}
    normalized_query = query_profile.get("normalized_query", query)
    query_terms = set(tokenize(normalized_query))
    score = 0.0
    features: dict[str, float | int | bool] = {}

    title = str(item.get("title", ""))
    text = str(item.get("text", ""))
    section = str(item.get("section_l1", "") or "")
    page_type = str(item.get("entry_type", "") or item.get("page_type", ""))
    field_name = str(item.get("field_name", "") or "")

    overlap = _title_overlap(query_terms, title)
    if overlap:
        boost = round(overlap * 0.8, 4)
        score += boost
        features["title_overlap_boost"] = boost

    query_standards = set(_extract_standards(normalized_query))
    candidate_standards = set(_extract_standards(f"{title} {text}"))
    if query_standards and candidate_standards:
        exact = bool(query_standards & candidate_standards)
        features["standard_exact_match"] = exact
        if exact:
            score += 1.2
        else:
            score -= 0.9

    query_families = _extract_family_hits(normalized_query)
    candidate_families = _extract_family_hits(f"{title} {text} {section}")
    for family, expected_hits in query_families.items():
        candidate_hits = candidate_families.get(family, [])
        if candidate_hits:
            if any(hit in candidate_hits for hit in expected_hits):
                score += 0.5
            else:
                score -= 0.6
                features[f"{family}_mismatch"] = True

    for hint, expected_section in SECTION_HINTS.items():
        if hint in normalized_query.lower():
            if expected_section.lower() in section.lower():
                score += 0.35
                features["section_prior_match"] = True
            else:
                score -= 0.15

    lower_text = f"{title} {text} {section}".lower()
    if "electric vehicle" in normalized_query.lower() and any(token in lower_text for token in ["electric vehicle", "hybrid", "ev"]):
        score += 0.45
        features["electric_vehicle_boost"] = True
    if "requirements" in normalized_query.lower() and "requirement" in lower_text:
        score += 0.25
        features["requirements_boost"] = True
    if any(token in normalized_query.lower() for token in ["measurement", "data acquisition", "instrumentation"]) and any(
        token in lower_text for token in ["measurement", "data acquisition", "instrument", "camera", "workshop"]
    ):
        score += 0.45
        features["measurement_boost"] = True

    if route == "page_or_index_lookup":
        if field_name in {"page_summary", "knowledge_topic", "overview", "keyword"}:
            score += 0.25
        if page_type in {"knowledge", "index"}:
            score += 0.2

    if route == "multi_page_lookup":
        if "knowledge page" in normalized_query.lower() and page_type == "knowledge":
            score += 0.5
            features["knowledge_page_boost"] = True

    if route == "seminar_lookup":
        if page_type == "seminar":
            score += 0.3
        elif page_type != "seminar":
            score -= 0.5

    if route == "event_lookup":
        if page_type == "event":
            score += 0.3
        elif page_type != "event":
            score -= 0.5

    if route == "recommendation":
        if field_name in {"who_should_attend", "course_objectives", "course_contents"}:
            score += 0.35

    if route == "multi_page_lookup":
        if page_type in {"knowledge", "seminar", "event"}:
            score += 0.2

    return round(score, 4), features
