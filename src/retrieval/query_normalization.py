from __future__ import annotations

import re


KOREAN_EXPANSIONS = {
    "관련 과정": ["course", "seminar", "training"],
    "과정": ["course", "seminar", "training"],
    "세미나": ["seminar", "course", "training"],
    "교육": ["training", "seminar", "course"],
    "강의": ["seminar", "course", "lecture"],
    "페이지": ["page", "where found"],
    "어디": ["where", "found in"],
    "약어": ["abbreviation", "stands for"],
    "뜻": ["meaning", "stands for"],
    "의미": ["meaning", "stands for"],
    "비교": ["compare", "difference", "versus"],
    "차이": ["difference", "compare"],
    "추천": ["recommend", "suitable", "best match"],
    "일정": ["schedule", "calendar", "date"],
    "충돌시험": ["crash test"],
    "수동안전": ["passive safety"],
    "능동안전": ["active safety"],
    "더미": ["dummy", "atd"],
    "정책": ["policy"],
    "브리핑": ["briefing"],
    "입문": ["introduction", "basics"],
    "지식 페이지": ["knowledge page", "knowledge"],
    "핵심": ["key", "core"],
    "두 개": ["two", "multiple pages"],
    "2개": ["two", "multiple pages"],
    "함께": ["together", "multiple pages"],
    "여러 페이지": ["multiple pages"],
    "전기차": ["electric vehicle", "ev"],
    "요구사항": ["requirements"],
    "안전 요구사항": ["safety requirements"],
    "계측": ["measurement", "data acquisition", "instrumentation"],
    "충돌 계측": ["crash measurement", "crash test data acquisition"],
    "브레이킹": ["braking"],
    "정책 관련": ["policy", "briefing"],
    "실적발표": ["earnings release", "earnings call"],
}

EVENT_ALIASES = {
    "experience",
    "briefing",
    "summit",
    "update",
    "dialogue",
    "week",
    "conference",
}

EXACT_ANCHOR_ALIASES = {
    "adas experience": "The ADAS Experience",
    "impact biomechanics": "Introduction to Impact Biomechanics and Human Body Models",
}

DUMMY_ANCHORS = {"THOR", "HIII", "HYBRID III", "SID-IIS", "WORLDSID", "ATD", "DUMMY", "LANDSCAPE"}


def collapse_spaced_acronyms(text: str) -> str:
    pattern = re.compile(r"\b(?:[A-Za-z]\s+){2,}[A-Za-z]\b")

    def replacer(match: re.Match[str]) -> str:
        return "".join(match.group(0).split())

    return pattern.sub(replacer, text)


def has_korean(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))


def expand_korean_terms(text: str) -> list[str]:
    expansions: list[str] = []
    for source, targets in KOREAN_EXPANSIONS.items():
        if source in text:
            expansions.extend(targets)
    return sorted(set(expansions))


def normalize_exact_anchors(text: str) -> str:
    normalized = text
    normalized = re.sub(r"\bfmvss\s*([0-9]{2,3}[a-z]?)\b", lambda m: f"FMVSS {m.group(1).upper()}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bgtr\s*([0-9]{1,2})\b", lambda m: f"GTR {m.group(1)}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\br\s*([0-9]{2,3}[a-z]?)\b", lambda m: f"R{m.group(1).upper()}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bfmvss([0-9]{2,3}[a-z]?)\b", lambda m: f"FMVSS {m.group(1).upper()}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bgtr([0-9]{1,2})\b", lambda m: f"GTR {m.group(1)}", normalized, flags=re.IGNORECASE)
    return normalized


def apply_exact_anchor_aliases(text: str) -> tuple[str, list[str]]:
    lowered = text.lower()
    expansions: list[str] = []
    for alias, canonical in EXACT_ANCHOR_ALIASES.items():
        if alias in lowered:
            expansions.append(canonical)
    return text, expansions


def extract_exact_anchors(text: str) -> list[str]:
    anchors = re.findall(r"\b(?:FMVSS\s*\d+[A-Z]?|GTR\s*\d+|R\d+[A-Z]?|AEB|ADAS|THOR|HIII|ATD)\b", text, flags=re.IGNORECASE)
    cleaned = []
    for anchor in anchors:
        anchor = re.sub(r"\s+", " ", anchor.strip()).upper()
        cleaned.append(anchor)
    return sorted(set(cleaned))


def extract_dummy_anchor_hints(text: str) -> list[str]:
    hints = []
    lowered = text.lower()
    if "dummy" in lowered or "더미" in text:
        hints.append("DUMMY")
    if "landscape" in lowered:
        hints.append("LANDSCAPE")
    if "hybrid iii" in lowered:
        hints.append("HYBRID III")
    for anchor in ["THOR", "HIII", "ATD", "SID-IIs", "WorldSID"]:
        if anchor.lower() in lowered:
            hints.append(anchor.upper())
    return sorted(set(hints))


def _prepare_compare_text(text: str) -> str:
    prepared = text
    prepared = prepared.replace("세미나와", "세미나 와 ")
    prepared = prepared.replace("세미나과", "세미나 과 ")
    prepared = prepared.replace("교육과", "교육 과 ")
    prepared = prepared.replace("과정과", "과정 과 ")
    return prepared


def extract_compare_targets(text: str) -> list[str]:
    prepared = _prepare_compare_text(text)
    parts = re.split(r"\bvs\b|\bversus\b|\s+및\s+|\s+와\s+|\s+과\s+", prepared, flags=re.IGNORECASE)
    cleaned = []
    for part in parts:
        part = part.strip(" ?")
        if not part:
            continue
        previous = None
        while previous != part:
            previous = part
            part = re.sub(r"(찾아줘|알려줘|보여줘|비교.*|차이.*)$", "", part).strip()
            part = re.sub(r"(함께)$", "", part).strip()
            part = re.sub(r"(를|을)$", "", part).strip()
            part = re.sub(r"(세미나를|세미나을)$", "세미나", part).strip()
        if part:
            cleaned.append(part)
    return cleaned if len(cleaned) >= 2 else []


def is_compare_hint(text: str, compare_targets: list[str]) -> bool:
    if compare_targets:
        return True
    return any(token in text for token in ["비교", "차이", "vs", "versus"])


def is_page_lookup_hint(original_query: str, normalized_query: str) -> bool:
    return any(token in original_query for token in ["페이지", "몇 페이지", "어디"]) or any(token in normalized_query.lower() for token in ["page", "where found"])


def is_event_hint(normalized_query: str) -> bool:
    lower = normalized_query.lower()
    return any(alias in lower for alias in EVENT_ALIASES)


def build_query_profile(query: str) -> dict:
    collapsed = collapse_spaced_acronyms(query)
    normalized_anchors = normalize_exact_anchors(collapsed)
    alias_query, alias_expansions = apply_exact_anchor_aliases(normalized_anchors)
    expansions = expand_korean_terms(alias_query)
    compare_targets = extract_compare_targets(alias_query)
    bilingual_query_parts = [alias_query]
    if expansions:
        bilingual_query_parts.append(" ".join(expansions))
    if alias_expansions:
        bilingual_query_parts.append(" ".join(alias_expansions))
    bilingual_query = " ".join(part for part in bilingual_query_parts if part).strip()
    exact_anchors = extract_exact_anchors(alias_query)
    multi_page_hint = any(token in alias_query for token in ["두 개", "2개", "함께", "여러 페이지"])
    if not multi_page_hint and any(anchor in {"THOR", "HIII", "ATD"} for anchor in exact_anchors) and ("더미" in query or "dummy" in bilingual_query.lower()):
        multi_page_hint = True
    dummy_anchor_hints = extract_dummy_anchor_hints(alias_query)
    return {
        "original_query": query,
        "collapsed_query": collapsed,
        "normalized_anchor_query": alias_query,
        "expanded_terms": expansions,
        "alias_expansions": alias_expansions,
        "normalized_query": bilingual_query,
        "has_korean": has_korean(query),
        "is_multi_page_hint": multi_page_hint,
        "compare_targets": compare_targets,
        "compare_hint": is_compare_hint(alias_query, compare_targets),
        "page_lookup_hint": is_page_lookup_hint(query, bilingual_query),
        "event_hint": is_event_hint(bilingual_query),
        "exact_anchors": exact_anchors,
        "dummy_anchor_hints": dummy_anchor_hints,
    }
