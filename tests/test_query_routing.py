from src.retrieval.router import route_query
from src.retrieval.query_normalization import build_query_profile


def test_abbreviation_route():
    profile = build_query_profile("AEB")
    assert route_query("AEB", normalized_query=profile["normalized_query"], is_multi_page_hint=profile["is_multi_page_hint"], compare_hint=profile["compare_hint"], relationship_hint=profile["relationship_hint"], page_lookup_hint=profile["page_lookup_hint"], event_hint=profile["event_hint"]) == "abbreviation_lookup"


def test_calendar_route():
    profile = build_query_profile("20.10.2026 일정 알려줘")
    assert route_query("20.10.2026 일정 알려줘", normalized_query=profile["normalized_query"], is_multi_page_hint=profile["is_multi_page_hint"], compare_hint=profile["compare_hint"], relationship_hint=profile["relationship_hint"], page_lookup_hint=profile["page_lookup_hint"], event_hint=profile["event_hint"]) == "calendar_lookup"


def test_seminar_route():
    profile = build_query_profile("ADAS 세미나 찾아줘")
    assert route_query("ADAS 세미나 찾아줘", normalized_query=profile["normalized_query"], is_multi_page_hint=profile["is_multi_page_hint"], compare_hint=profile["compare_hint"], relationship_hint=profile["relationship_hint"], page_lookup_hint=profile["page_lookup_hint"], event_hint=profile["event_hint"]) == "seminar_lookup"


def test_recommendation_route():
    profile = build_query_profile("충돌 계측 입문에 가까운 교육을 추천해줘")
    assert route_query("충돌 계측 입문에 가까운 교육을 추천해줘", normalized_query=profile["normalized_query"], is_multi_page_hint=profile["is_multi_page_hint"], compare_hint=profile["compare_hint"], relationship_hint=profile["relationship_hint"], page_lookup_hint=profile["page_lookup_hint"], event_hint=profile["event_hint"]) == "recommendation"


def test_multi_page_route():
    profile = build_query_profile("전기차 안전 요구사항을 다루는 핵심 지식 페이지 두 개를 찾아줘")
    assert route_query("전기차 안전 요구사항을 다루는 핵심 지식 페이지 두 개를 찾아줘", normalized_query=profile["normalized_query"], is_multi_page_hint=profile["is_multi_page_hint"], compare_hint=profile["compare_hint"], relationship_hint=profile["relationship_hint"], page_lookup_hint=profile["page_lookup_hint"], event_hint=profile["event_hint"]) == "multi_page_lookup"


def test_compare_route():
    profile = build_query_profile("Automated Driving 입문 세미나와 정책 브리핑 세미나를 함께 찾아줘")
    assert len(profile["compare_targets"]) >= 2
    assert route_query("Automated Driving 입문 세미나와 정책 브리핑 세미나를 함께 찾아줘", normalized_query=profile["normalized_query"], is_multi_page_hint=profile["is_multi_page_hint"], compare_hint=profile["compare_hint"], relationship_hint=profile["relationship_hint"], page_lookup_hint=profile["page_lookup_hint"], event_hint=profile["event_hint"]) == "compare"


def test_event_paraphrase_route():
    profile = build_query_profile("ADAS experience 어디")
    assert route_query("ADAS experience 어디", normalized_query=profile["normalized_query"], is_multi_page_hint=profile["is_multi_page_hint"], compare_hint=profile["compare_hint"], relationship_hint=profile["relationship_hint"], page_lookup_hint=profile["page_lookup_hint"], event_hint=profile["event_hint"]) == "event_lookup"


def test_exact_anchor_normalization():
    profile = build_query_profile("fmvss305a page?")
    assert "FMVSS 305A" in profile["normalized_anchor_query"]


def test_dummy_anchor_clusters():
    profile = build_query_profile("THOR와 HIII 관련 페이지를 함께 정리해줘")
    assert "THOR_CLUSTER" in profile["dummy_anchor_clusters"]
    assert "HIII_CLUSTER" in profile["dummy_anchor_clusters"]


def test_relationship_route():
    profile = build_query_profile("THOR와 관련된 엔트리를 보여줘")
    assert route_query(
        "THOR와 관련된 엔트리를 보여줘",
        normalized_query=profile["normalized_query"],
        is_multi_page_hint=profile["is_multi_page_hint"],
        compare_hint=profile["compare_hint"],
        relationship_hint=profile["relationship_hint"],
        page_lookup_hint=profile["page_lookup_hint"],
        event_hint=profile["event_hint"],
    ) == "relationship_query"


def test_relationship_route_for_standard_query():
    profile = build_query_profile("FMVSS 208과 관련된 엔트리를 보여줘")
    assert route_query(
        "FMVSS 208과 관련된 엔트리를 보여줘",
        normalized_query=profile["normalized_query"],
        is_multi_page_hint=profile["is_multi_page_hint"],
        compare_hint=profile["compare_hint"],
        relationship_hint=profile["relationship_hint"],
        page_lookup_hint=profile["page_lookup_hint"],
        event_hint=profile["event_hint"],
    ) == "relationship_query"


def test_relationship_route_takes_precedence_over_multi_page_for_entry_queries():
    profile = build_query_profile("Hybrid III와 THOR가 함께 나오는 지식 엔트리를 찾아줘")
    assert route_query(
        "Hybrid III와 THOR가 함께 나오는 지식 엔트리를 찾아줘",
        normalized_query=profile["normalized_query"],
        is_multi_page_hint=profile["is_multi_page_hint"],
        compare_hint=profile["compare_hint"],
        relationship_hint=profile["relationship_hint"],
        page_lookup_hint=profile["page_lookup_hint"],
        event_hint=profile["event_hint"],
    ) == "relationship_query"
