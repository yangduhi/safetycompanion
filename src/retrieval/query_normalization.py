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
}


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


def build_query_profile(query: str) -> dict:
    collapsed = collapse_spaced_acronyms(query)
    expansions = expand_korean_terms(collapsed)
    bilingual_query_parts = [collapsed]
    if expansions:
        bilingual_query_parts.append(" ".join(expansions))
    bilingual_query = " ".join(part for part in bilingual_query_parts if part).strip()
    return {
        "original_query": query,
        "collapsed_query": collapsed,
        "expanded_terms": expansions,
        "normalized_query": bilingual_query,
        "has_korean": has_korean(query),
        "is_multi_page_hint": any(token in collapsed for token in ["두 개", "2개", "함께", "여러 페이지"]),
    }
