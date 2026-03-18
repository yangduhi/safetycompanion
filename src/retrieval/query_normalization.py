from __future__ import annotations

import re

from src.graph.catalog import detect_query_topics, extract_dummy_families, extract_organizations, extract_standards


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
    "행사": ["event", "conference"],
    "이벤트": ["event", "conference"],
    "세션": ["session", "event"],
    "업데이트": ["update", "event"],
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
    "session",
}

EXACT_ANCHOR_ALIASES = {
    "adas experience": "The ADAS Experience",
    "impact biomechanics": "Introduction to Impact Biomechanics and Human Body Models",
}

DUMMY_ANCHORS = {"THOR", "HIII", "HYBRID III", "SID-IIS", "WORLDSID", "ATD", "DUMMY", "LANDSCAPE"}

DUMMY_CLUSTER_RULES = {
    "THOR_CLUSTER": ["thor", "thor 50", "thor 5"],
    "HIII_CLUSTER": ["hiii", "hybrid iii", "hybrid-iii", "hybrid 3"],
    "ATD_CLUSTER": ["atd", "anthropomorphic test device"],
    "DUMMY_LANDSCAPE_CLUSTER": ["dummy", "landscape", "current dummy landscape", "dummy landscape"],
}


STRONG_DUMMY_CLUSTERS = {"THOR_CLUSTER", "HIII_CLUSTER", "ATD_CLUSTER"}


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
    normalized = re.sub(r"\bfmvss\s*([0-9]{2,3}[a-z]?)(?=[^A-Za-z0-9]|$)", lambda m: f"FMVSS {m.group(1).upper()}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bgtr\s*([0-9]{1,2})(?=[^A-Za-z0-9]|$)", lambda m: f"GTR {m.group(1)}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\br\s*([0-9]{2,3}[a-z]?)(?=[^A-Za-z0-9]|$)", lambda m: f"R{m.group(1).upper()}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bfmvss([0-9]{2,3}[a-z]?)(?=[^A-Za-z0-9]|$)", lambda m: f"FMVSS {m.group(1).upper()}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bgtr([0-9]{1,2})(?=[^A-Za-z0-9]|$)", lambda m: f"GTR {m.group(1)}", normalized, flags=re.IGNORECASE)
    return normalized


def apply_exact_anchor_aliases(text: str) -> tuple[str, list[str]]:
    lowered = text.lower()
    expansions: list[str] = []
    for alias, canonical in EXACT_ANCHOR_ALIASES.items():
        if alias in lowered:
            expansions.append(canonical)
    return text, expansions


def extract_exact_anchors(text: str) -> list[str]:
    anchors = re.findall(r"\b(?:FMVSS\s*\d+[A-Z]?|GTR\s*\d+|R\d+[A-Z]?|AEB|ADAS|THOR|HIII|ATD)(?=[^A-Za-z0-9]|$)", text, flags=re.IGNORECASE)
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


def extract_dummy_anchor_clusters(text: str) -> list[str]:
    lowered = text.lower()
    clusters: list[str] = []
    for cluster, aliases in DUMMY_CLUSTER_RULES.items():
        if any(alias in lowered for alias in aliases):
            clusters.append(cluster)
    return sorted(set(clusters))


def infer_dummy_query_mode(text: str, clusters: list[str]) -> str:
    lowered = text.lower()
    has_landscape = any(token in lowered for token in ["landscape", "current dummy landscape"])
    has_training = any(token in lowered for token in ["training", "seminar", "course", "education", "lecture"])
    cluster_set = set(clusters)
    has_specific_anchor = bool(cluster_set & STRONG_DUMMY_CLUSTERS)
    has_generic_dummy = "DUMMY_LANDSCAPE_CLUSTER" in cluster_set or "dummy" in lowered

    if has_landscape:
        return "landscape"
    if has_specific_anchor and not has_generic_dummy:
        return "specific_anchor"
    if has_specific_anchor and has_generic_dummy:
        return "mixed"
    if has_training:
        return "training"
    if has_generic_dummy:
        return "generic_dummy"
    return "generic"


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


def is_relationship_hint(original_query: str, normalized_query: str, exact_anchors: list[str]) -> bool:
    text = f"{original_query} {normalized_query}"
    lowered = text.lower()
    relation_tokens = [
        "관계",
        "관련성",
        "관련된 엔트리",
        "관련 엔트리",
        "연관된 엔트리",
        "속한 엔트리",
        "topic",
        "relationship",
        "related entries",
        "related entry",
        "belongs to topic",
    ]
    has_entry_request = "엔트리" in text or "entry" in lowered or "entries" in lowered
    has_relation_token = any(token in lowered for token in relation_tokens)
    if has_relation_token or has_entry_request:
        if exact_anchors:
            return True
        if detect_query_topics(text):
            return True
        if extract_dummy_families(text) or extract_standards(text) or extract_organizations(text):
            return True
    return False


def detect_graph_relation_class(query: str, normalized_query: str, exact_anchors: list[str]) -> str | None:
    text = f"{query} {normalized_query}"
    lowered = text.lower()
    topics = detect_query_topics(text)
    standards = extract_standards(text)
    dummies = extract_dummy_families(text)
    orgs = extract_organizations(text)
    if topics and ("topic" in lowered or "속한" in text or "핵심 엔트리" in text):
        return "topic_cluster_relation"
    if orgs:
        return "organization_entry_relation"
    if standards or any(anchor.startswith(("FMVSS", "GTR", "UN R", "R")) for anchor in exact_anchors):
        return "standard_topic_relation"
    if dummies or any(anchor in {"THOR", "HIII", "ATD"} for anchor in exact_anchors):
        return "dummy_family_relation"
    return None


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
    strong_grouping_request_hint = any(token in alias_query for token in ["두 개", "2개", "함께", "여러 페이지", "정리해줘", "모아서", "모아", "모여", "같이 나오는"])
    related_page_hint = "관련 페이지" in alias_query
    multi_page_hint = strong_grouping_request_hint
    if not multi_page_hint and any(anchor in {"THOR", "HIII", "ATD"} for anchor in exact_anchors) and ("더미" in query or "dummy" in bilingual_query.lower()):
        multi_page_hint = True
    dummy_anchor_hints = extract_dummy_anchor_hints(alias_query)
    dummy_anchor_clusters = extract_dummy_anchor_clusters(alias_query)
    dummy_query_mode = infer_dummy_query_mode(alias_query, dummy_anchor_clusters)
    dummy_training_hint = any(token in alias_query.lower() for token in ["training", "seminar", "course", "교육", "세미나", "과정", "강의"])
    if not multi_page_hint and dummy_anchor_clusters and (strong_grouping_request_hint or related_page_hint):
        multi_page_hint = True
    if not multi_page_hint and len(dummy_anchor_clusters) >= 2:
        multi_page_hint = True
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
        "relationship_hint": is_relationship_hint(query, bilingual_query, exact_anchors),
        "graph_relation_class": detect_graph_relation_class(query, bilingual_query, exact_anchors),
        "exact_anchors": exact_anchors,
        "dummy_anchor_hints": dummy_anchor_hints,
        "dummy_anchor_clusters": dummy_anchor_clusters,
        "dummy_query_mode": dummy_query_mode,
        "dummy_training_hint": dummy_training_hint,
        "grouping_request_hint": strong_grouping_request_hint or related_page_hint,
        "strong_grouping_request_hint": strong_grouping_request_hint,
        "related_page_hint": related_page_hint,
    }
