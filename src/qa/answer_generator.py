from __future__ import annotations

from typing import Iterable

from src.common.policy import route_policy_for
from src.common.text import tokenize
from src.retrieval.compare_ranking import compare_pair_success


FIELD_PRIORITY_BY_ROUTE = {
    "abbreviation_lookup": ["expansion", "overview"],
    "page_or_index_lookup": ["page_summary", "knowledge_topic", "overview", "keyword"],
    "seminar_lookup": ["course_description", "course_objectives", "course_contents", "overview"],
    "event_lookup": ["description", "overview"],
    "calendar_lookup": ["course_description", "description", "overview", "schedule"],
    "compare": ["course_description", "course_contents", "description", "overview"],
    "recommendation": ["who_should_attend", "course_objectives", "course_contents", "overview"],
    "multi_page_lookup": ["page_summary", "knowledge_topic", "overview", "course_description"],
    "entity_relation_lookup": ["description", "overview", "page_summary", "knowledge_topic", "course_description"],
    "topic_cluster_lookup": ["overview", "course_description", "description", "page_summary", "knowledge_topic"],
    "relationship_query": ["page_summary", "description", "course_description", "overview"],
    "fallback_general": ["overview", "course_description", "page_summary", "description"],
}


def format_citation(item: dict) -> str:
    printed = item.get("printed_page")
    field_name = item.get("field_name")
    field_suffix = f", field {field_name}" if field_name else ""
    if printed is None:
        return f"{item.get('title', 'Untitled')} (pdf p.{item.get('pdf_page')}{field_suffix})"
    return f"{item.get('title', 'Untitled')} (pdf p.{item.get('pdf_page')}, printed p.{printed}{field_suffix})"


def _field_priority(route: str, field_name: str | None, route_policy: dict | None = None) -> int:
    if not field_name:
        return 999
    if route_policy:
        preferred = route_policy_for(route_policy, route).get("preferred_fields") or FIELD_PRIORITY_BY_ROUTE.get(route, FIELD_PRIORITY_BY_ROUTE["fallback_general"])
    else:
        preferred = FIELD_PRIORITY_BY_ROUTE.get(route, FIELD_PRIORITY_BY_ROUTE["fallback_general"])
    if field_name in preferred:
        return preferred.index(field_name)
    return len(preferred) + 10


def _extract_span(query: str, text: str, max_chars: int = 280) -> dict:
    if not text:
        return {
            "evidence_text": "",
            "evidence_start": 0,
            "evidence_end": 0,
            "span_present": False,
        }
    query_terms = [term for term in tokenize(query) if len(term) > 1]
    candidates = []
    for segment in [part.strip() for part in text.splitlines() if part.strip()] or [text]:
        lowered = segment.lower()
        overlap = sum(1 for term in query_terms if term in lowered)
        candidates.append((overlap, segment))
    candidates.sort(key=lambda item: (item[0], len(item[1])), reverse=True)
    best = candidates[0][1][:max_chars].strip()
    try:
        start = text.index(best)
    except ValueError:
        start = 0
    end = start + len(best)
    return {
        "evidence_text": best,
        "evidence_start": start,
        "evidence_end": end,
        "span_present": bool(best),
    }


def _confidence(item: dict) -> float:
    score = float(item.get("rerank_score", item.get("fused_score", item.get("score", 0.0))))
    if score <= 0:
        return 0.0
    if score >= 3:
        return 1.0
    return round(score / 3.0, 4)


def _entity_tier_rank(item: dict) -> int:
    value = item.get("entity_relation_tier_rank")
    return 99 if value is None else int(value)


def select_evidence(route: str, candidates: list[dict], limit: int = 3, route_policy: dict | None = None) -> list[dict]:
    if not candidates:
        return []
    policy = route_policy_for(route_policy or {}, route) if route_policy else {}
    ranked = sorted(
        candidates,
        key=lambda item: (
            _entity_tier_rank(item) if route == "entity_relation_lookup" else 99,
            -float(item.get("rerank_score", item.get("fused_score", item.get("score", 0.0)))),
            _field_priority(route, item.get("field_name"), route_policy=route_policy),
        ),
    )
    selected: list[dict] = []
    seen: set[tuple] = set()
    seen_entries: set[str] = set()
    seen_compare_targets: set[int] = set()
    min_distinct_entries = int(policy.get("min_distinct_entries", 1))

    for item in ranked:
        dedupe_key = (item.get("chunk_id"), item.get("title"), item.get("pdf_page"), item.get("field_name"))
        if dedupe_key in seen:
            continue
        if route in {"compare", "recommendation"} and len(seen_entries) < min_distinct_entries:
            entry_id = item.get("entry_id")
            if entry_id and entry_id in seen_entries and len(ranked) > len(selected):
                continue
        if route == "compare":
            compare_target_index = item.get("compare_target_index")
            if compare_target_index and compare_target_index in seen_compare_targets and len(seen_compare_targets) < min_distinct_entries:
                continue
        seen.add(dedupe_key)
        if item.get("entry_id"):
            seen_entries.add(item["entry_id"])
        if route == "compare" and item.get("compare_target_index"):
            seen_compare_targets.add(item["compare_target_index"])
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def _abbreviation_answer(query: str, route: str, selected: list[dict]) -> dict:
    top = selected[0]
    abbr = top.get("title", query).strip()
    expansion = top.get("expansion") or top.get("evidence_text") or top.get("text", "")
    if isinstance(expansion, str) and "=" in expansion:
        expansion = expansion.split("=", 1)[1].strip()
    answer = (
        f"{abbr}는 {expansion}입니다. "
        f"출처: {format_citation(top)}."
    )
    return {
        "query": query,
        "route": route,
        "answer": answer,
        "evidence": selected,
        "selected_field": top.get("field_name"),
        "evidence_count": len(selected),
        "span_present": all(item.get("span_present", False) for item in selected),
        "template_answer_used": True,
        "multi_page_used": len({item.get('pdf_page') for item in selected}) > 1,
        "route_name": route,
    }


def _compare_answer(query: str, route: str, selected: list[dict]) -> dict:
    if not compare_pair_success(selected, required_targets=2):
        return {
            "query": query,
            "route": route,
            "answer": "비교를 위한 문서 근거가 충분하지 않음",
            "evidence": [],
            "selected_field": None,
            "evidence_count": len(selected),
            "span_present": False,
            "template_answer_used": True,
            "multi_page_used": False,
            "route_name": route,
        }

    first, second = selected[:2]
    answer = "\n".join(
        [
            f"질의 경로: {route}",
            f"비교 대상 1: {format_citation(first)}",
            f"비교 대상 2: {format_citation(second)}",
            "",
            "비교 요약:",
            f"- {first.get('title', 'Untitled')}",
            f"  근거: {first.get('evidence_text', '') or first.get('text', '')[:180]}",
            f"- {second.get('title', 'Untitled')}",
            f"  근거: {second.get('evidence_text', '') or second.get('text', '')[:180]}",
        ]
    )
    evidence = [
        {
            "title": item.get("title"),
            "pdf_page": item.get("pdf_page"),
            "printed_page": item.get("printed_page"),
            "chunk_id": item.get("chunk_id"),
            "field_name": item.get("field_name"),
            "text": item.get("text", "")[:400],
            "evidence_text": item.get("evidence_text", ""),
            "evidence_field": item.get("evidence_field"),
            "evidence_start": item.get("evidence_start"),
            "evidence_end": item.get("evidence_end"),
            "evidence_page": item.get("evidence_page"),
            "evidence_confidence": item.get("evidence_confidence"),
            "entry_id": item.get("entry_id"),
            "compare_target_index": item.get("compare_target_index"),
        }
        for item in selected[:2]
    ]
    return {
        "query": query,
        "route": route,
        "answer": answer,
        "evidence": evidence,
        "selected_field": f"{first.get('field_name')}|{second.get('field_name')}",
        "evidence_count": len(evidence),
        "span_present": all(item.get("evidence_text") for item in evidence),
        "template_answer_used": True,
        "multi_page_used": True,
        "route_name": route,
    }


def _multi_page_answer(query: str, route: str, selected: list[dict]) -> dict:
    if not selected:
        return {
            "query": query,
            "route": route,
            "answer": "문서상 확인 불가",
            "evidence": [],
            "selected_field": None,
            "evidence_count": 0,
            "span_present": False,
            "template_answer_used": True,
            "multi_page_used": False,
            "route_name": route,
        }

    page_list = []
    page_roles = []
    for item in selected:
        seed_marker = " [seed]" if int(item.get("selection_rank", 99) or 99) == 1 else ""
        page_list.append(f"- p.{item.get('pdf_page')}: {item.get('title', 'Untitled')}{seed_marker}")
        page_roles.append(f"- p.{item.get('pdf_page')}: {item.get('page_role', 'detail_page')}")
    summary_lines = [
        f"- {item.get('title', 'Untitled')}: {item.get('evidence_text', '') or item.get('text', '')[:160]}"
        for item in selected[:3]
    ]
    answer = "\n".join(
        [
            f"질의 경로: {route}",
            "",
            "관련 페이지:",
            *page_list,
            "",
            "페이지 역할:",
            *page_roles,
            "",
            "통합 요약:",
            *summary_lines,
        ]
    )
    evidence = [
        {
            "title": item.get("title"),
            "pdf_page": item.get("pdf_page"),
            "printed_page": item.get("printed_page"),
            "chunk_id": item.get("chunk_id"),
            "field_name": item.get("field_name"),
            "text": item.get("text", "")[:400],
            "evidence_text": item.get("evidence_text", ""),
            "evidence_field": item.get("evidence_field"),
            "evidence_start": item.get("evidence_start"),
            "evidence_end": item.get("evidence_end"),
            "evidence_page": item.get("evidence_page"),
            "evidence_confidence": item.get("evidence_confidence"),
            "entry_id": item.get("entry_id"),
            "page_role": item.get("page_role"),
        }
        for item in selected
    ]
    return {
        "query": query,
        "route": route,
        "answer": answer,
        "evidence": evidence,
        "selected_field": selected[0].get("field_name"),
        "evidence_count": len(evidence),
        "span_present": all(item.get("evidence_text") for item in evidence),
        "template_answer_used": True,
        "multi_page_used": True,
        "route_name": route,
    }


def _relationship_answer(query: str, route: str, selected: list[dict]) -> dict:
    if not selected:
        return {
            "query": query,
            "route": route,
            "answer": "문서상 확인 불가",
            "evidence": [],
            "selected_field": None,
            "evidence_count": 0,
            "span_present": False,
            "template_answer_used": True,
            "multi_page_used": False,
            "route_name": route,
            "graph_backfill_used": False,
        }

    graph_entities = sorted(
        {
            entity
            for item in selected
            for entity in item.get("graph_match_names", [])
            if entity
        }
    )
    related_lines = [
        f"- {item.get('title', 'Untitled')} -> {format_citation(item)}"
        for item in selected
    ]
    entity_lines = [f"- {entity}" for entity in graph_entities] or ["- explicit graph entity not recorded"]
    answer = "\n".join(
        [
            f"질의 경로: {route}",
            "",
            "그래프 매칭 엔터티:",
            *entity_lines,
            "",
            "관련 엔트리:",
            *related_lines,
        ]
    )
    evidence = [
        {
            "title": item.get("title"),
            "pdf_page": item.get("pdf_page"),
            "printed_page": item.get("printed_page"),
            "chunk_id": item.get("chunk_id"),
            "field_name": item.get("field_name"),
            "text": item.get("text", "")[:400],
            "evidence_text": item.get("evidence_text", ""),
            "evidence_field": item.get("evidence_field"),
            "evidence_start": item.get("evidence_start"),
            "evidence_end": item.get("evidence_end"),
            "evidence_page": item.get("evidence_page"),
            "evidence_confidence": item.get("evidence_confidence"),
            "entry_id": item.get("entry_id"),
            "graph_match_names": item.get("graph_match_names", []),
            "graph_edge_types": item.get("graph_edge_types", []),
        }
        for item in selected
    ]
    return {
        "query": query,
        "route": route,
        "answer": answer,
        "evidence": evidence,
        "selected_field": selected[0].get("field_name"),
        "evidence_count": len(evidence),
        "span_present": all(item.get("evidence_text") for item in evidence),
        "template_answer_used": True,
        "multi_page_used": len({item.get('pdf_page') for item in selected}) > 1,
        "route_name": route,
        "graph_backfill_used": True,
    }


def _entity_relation_answer(query: str, route: str, selected: list[dict]) -> dict:
    if not selected:
        return {
            "query": query,
            "route": route,
            "answer": "문서상 확인 불가",
            "evidence": [],
            "selected_field": None,
            "evidence_count": 0,
            "span_present": False,
            "template_answer_used": True,
            "multi_page_used": False,
            "route_name": route,
            "graph_backfill_used": False,
        }

    representative = next((item for item in selected if _entity_tier_rank(item) == 0), selected[0])
    supporting = [item for item in selected if item.get("entry_id") != representative.get("entry_id")][:2]
    supporting_lines = [f"- {item.get('title', 'Untitled')} -> {format_citation(item)}" for item in supporting] or ["- supporting evidence not selected"]
    answer = "\n".join(
        [
            f"질의 경로: {route}",
            "",
            f"대표 엔트리: {representative.get('title', 'Untitled')} -> {format_citation(representative)}",
            "",
            "관련 참고 엔트리:",
            *supporting_lines,
        ]
    )
    ordered = [representative, *supporting]
    evidence = [
        {
            "title": item.get("title"),
            "pdf_page": item.get("pdf_page"),
            "printed_page": item.get("printed_page"),
            "chunk_id": item.get("chunk_id"),
            "field_name": item.get("field_name"),
            "text": item.get("text", "")[:400],
            "evidence_text": item.get("evidence_text", ""),
            "evidence_field": item.get("evidence_field"),
            "evidence_start": item.get("evidence_start"),
            "evidence_end": item.get("evidence_end"),
            "evidence_page": item.get("evidence_page"),
            "evidence_confidence": item.get("evidence_confidence"),
            "entry_id": item.get("entry_id"),
            "graph_match_names": item.get("graph_match_names", []),
            "graph_edge_types": item.get("graph_edge_types", []),
            "entity_relation_tier": item.get("entity_relation_tier"),
            "entity_relation_role": item.get("entity_relation_role"),
        }
        for item in ordered
    ]
    return {
        "query": query,
        "route": route,
        "answer": answer,
        "evidence": evidence,
        "selected_field": representative.get("field_name"),
        "evidence_count": len(evidence),
        "span_present": all(item.get("evidence_text") for item in evidence),
        "template_answer_used": True,
        "multi_page_used": len({item.get('pdf_page') for item in evidence}) > 1,
        "route_name": route,
        "graph_backfill_used": True,
    }


def _topic_cluster_answer(query: str, route: str, selected: list[dict]) -> dict:
    if not selected:
        return {
            "query": query,
            "route": route,
            "answer": "문서상 확인 불가",
            "evidence": [],
            "selected_field": None,
            "evidence_count": 0,
            "span_present": False,
            "template_answer_used": True,
            "multi_page_used": False,
            "route_name": route,
            "graph_backfill_used": False,
        }

    representative = selected[0]
    related_lines = [f"- {item.get('title', 'Untitled')} -> {format_citation(item)}" for item in selected]
    answer = "\n".join(
        [
            f"질의 경로: {route}",
            "",
            f"대표 엔트리: {representative.get('title', 'Untitled')}",
            "",
            "토픽 관련 엔트리:",
            *related_lines,
        ]
    )
    evidence = [
        {
            "title": item.get("title"),
            "pdf_page": item.get("pdf_page"),
            "printed_page": item.get("printed_page"),
            "chunk_id": item.get("chunk_id"),
            "field_name": item.get("field_name"),
            "text": item.get("text", "")[:400],
            "evidence_text": item.get("evidence_text", ""),
            "evidence_field": item.get("evidence_field"),
            "evidence_start": item.get("evidence_start"),
            "evidence_end": item.get("evidence_end"),
            "evidence_page": item.get("evidence_page"),
            "evidence_confidence": item.get("evidence_confidence"),
            "entry_id": item.get("entry_id"),
            "graph_match_names": item.get("graph_match_names", []),
            "graph_edge_types": item.get("graph_edge_types", []),
        }
        for item in selected
    ]
    return {
        "query": query,
        "route": route,
        "answer": answer,
        "evidence": evidence,
        "selected_field": representative.get("field_name"),
        "evidence_count": len(evidence),
        "span_present": all(item.get("evidence_text") for item in evidence),
        "template_answer_used": True,
        "multi_page_used": len({item.get('pdf_page') for item in selected}) > 1,
        "route_name": route,
        "graph_backfill_used": True,
    }


def build_grounded_answer(query: str, route: str, candidates: Iterable[dict], route_policy: dict | None = None) -> dict:
    route = "compare" if route == "compare_or_recommend" else route
    ranked = list(candidates)
    if not ranked:
        return {
            "query": query,
            "route": route,
            "answer": "문서상 확인 불가",
            "evidence": [],
            "selected_field": None,
            "evidence_count": 0,
            "span_present": False,
            "template_answer_used": False,
            "multi_page_used": False,
            "route_name": route,
        }
    policy = route_policy_for(route_policy or {}, route) if route_policy else {}
    selected_raw = select_evidence(route, ranked, limit=max(3, int(policy.get("min_evidence", 1))), route_policy=route_policy)
    selected = []
    for item in selected_raw:
        span = _extract_span(query, item.get("text", ""))
        enriched = dict(item)
        enriched.update(span)
        enriched["evidence_field"] = item.get("field_name")
        enriched["evidence_page"] = item.get("pdf_page")
        enriched["evidence_confidence"] = _confidence(item)
        selected.append(enriched)

    if policy.get("deterministic_template"):
        return _abbreviation_answer(query, route, selected)
    if route == "compare":
        return _compare_answer(query, route, selected)
    if route == "multi_page_lookup":
        return _multi_page_answer(query, route, selected)
    if route == "entity_relation_lookup":
        return _entity_relation_answer(query, route, selected)
    if route == "relationship_query":
        return _relationship_answer(query, route, selected)
    if route == "topic_cluster_lookup":
        return _topic_cluster_answer(query, route, selected)

    top = selected[0]
    evidence_count = len(selected)
    distinct_entries = {item.get("entry_id") for item in selected if item.get("entry_id")}
    min_evidence = int(policy.get("min_evidence", 1))
    min_distinct_entries = int(policy.get("min_distinct_entries", 1))
    multi_page_used = len({item.get("pdf_page") for item in selected}) > 1

    cautious_answer = None
    if route in {"compare", "recommendation"}:
        if evidence_count < min_evidence or len(distinct_entries) < min_distinct_entries:
            if route == "recommendation" or any(token in query for token in ["추천", "recommend"]):
                cautious_answer = "추천 가능하지만 문서 근거가 충분하지 않음"
            else:
                cautious_answer = "비교를 위한 문서 근거가 충분하지 않음"

    evidence = [
        {
            "title": item.get("title"),
            "pdf_page": item.get("pdf_page"),
            "printed_page": item.get("printed_page"),
            "chunk_id": item.get("chunk_id"),
            "field_name": item.get("field_name"),
            "text": item.get("text", "")[:400],
            "evidence_text": item.get("evidence_text", ""),
            "evidence_field": item.get("evidence_field"),
            "evidence_start": item.get("evidence_start"),
            "evidence_end": item.get("evidence_end"),
            "evidence_page": item.get("evidence_page"),
            "evidence_confidence": item.get("evidence_confidence"),
            "entry_id": item.get("entry_id"),
        }
        for item in selected
    ]
    bullet_lines = [f"- {format_citation(item)}" for item in selected]
    if route == "multi_page_lookup" and len(selected) >= 2 and not cautious_answer:
        summary_text = "관련 페이지: " + ", ".join(
            f"{item.get('title', 'Untitled')} (p.{item.get('pdf_page')})" for item in selected[:3]
        )
    elif route in {"compare", "recommendation"} and len(selected) >= 2 and not cautious_answer:
        summary_text = " / ".join(item.get("title", "Untitled") for item in selected[:2])
    elif cautious_answer:
        summary_text = cautious_answer
    else:
        summary_text = top.get("evidence_text", "").strip() or top.get("text", "")[:500].strip() or top.get("title", "문서상 확인 불가")
    answer = "\n".join(
        [
            f"질의 경로: {route}",
            f"가장 관련 높은 근거: {format_citation(top)}",
            "",
            "요약:",
            summary_text,
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
        "selected_field": top.get("field_name"),
        "evidence_count": evidence_count,
        "span_present": all(item.get("evidence_text") for item in evidence),
        "template_answer_used": False,
        "multi_page_used": multi_page_used,
        "route_name": route,
        "graph_backfill_used": False,
    }
