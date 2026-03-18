from src.qa.answer_generator import build_grounded_answer


def test_grounded_answer_contains_page_metadata():
    answer = build_grounded_answer(
        "FMVSS 305a 관련 세미나",
        "seminar_lookup",
        [
            {
                "title": "Crash Safety of Hybrid and Electric Vehicles",
                "pdf_page": 28,
                "printed_page": 28,
                "chunk_id": "demo",
                "field_name": "overview",
                "text": "Participants will get an overview about automotive safety of electric vehicles.",
            }
        ],
    )
    assert "pdf p.28" in answer["answer"]
    assert "printed p.28" in answer["answer"]


def test_grounded_answer_handles_no_evidence():
    answer = build_grounded_answer("없음", "fallback_general", [])
    assert answer["answer"] == "문서상 확인 불가"


def test_abbreviation_route_uses_template_answer():
    route_policy = {
        "abbreviation_lookup": {
            "preferred_fields": ["expansion"],
            "deterministic_template": True,
            "min_evidence": 1,
            "min_distinct_entries": 1,
        }
    }
    answer = build_grounded_answer(
        "AEB",
        "abbreviation_lookup",
        [
            {
                "title": "AEB",
                "pdf_page": 215,
                "printed_page": 215,
                "chunk_id": "abbr_aeb_215",
                "field_name": "expansion",
                "text": "AEB = Autonomous Emergency Braking",
                "expansion": "Autonomous Emergency Braking",
                "score": 2.0,
            }
        ],
        route_policy=route_policy,
    )
    assert answer["template_answer_used"] is True
    assert "Autonomous Emergency Braking" in answer["answer"]
    assert "pdf p.215" in answer["answer"]


def test_compare_route_requires_multiple_evidence():
    route_policy = {
        "compare": {
            "preferred_fields": ["course_description", "overview"],
            "deterministic_template": False,
            "min_evidence": 2,
            "min_distinct_entries": 2,
        }
    }
    answer = build_grounded_answer(
        "두 세미나를 비교해줘",
        "compare",
        [
            {
                "title": "Seminar A",
                "pdf_page": 10,
                "printed_page": 10,
                "chunk_id": "a",
                "entry_id": "entry_a",
                "field_name": "course_description",
                "text": "Description A",
                "score": 1.0,
            }
        ],
        route_policy=route_policy,
    )
    assert "비교를 위한 문서 근거가 충분하지 않음" in answer["answer"]


def test_compare_route_builds_pair_answer():
    route_policy = {
        "compare": {
            "preferred_fields": ["course_description", "overview"],
            "deterministic_template": False,
            "min_evidence": 2,
            "min_distinct_entries": 2,
        }
    }
    answer = build_grounded_answer(
        "A와 B를 비교해줘",
        "compare",
        [
            {
                "title": "Seminar A",
                "pdf_page": 10,
                "printed_page": 10,
                "chunk_id": "a",
                "entry_id": "entry_a",
                "field_name": "course_description",
                "text": "Description A",
                "score": 1.0,
                "compare_target_index": 1,
            },
            {
                "title": "Seminar B",
                "pdf_page": 20,
                "printed_page": 20,
                "chunk_id": "b",
                "entry_id": "entry_b",
                "field_name": "course_description",
                "text": "Description B",
                "score": 1.0,
                "compare_target_index": 2,
            },
        ],
        route_policy=route_policy,
    )
    assert "비교 대상 1" in answer["answer"]
    assert "비교 대상 2" in answer["answer"]


def test_multi_page_answer_contains_page_roles():
    route_policy = {
        "multi_page_lookup": {
            "preferred_fields": ["page_summary", "overview"],
            "deterministic_template": False,
            "min_evidence": 2,
            "min_distinct_entries": 2,
        }
    }
    answer = build_grounded_answer(
        "THOR 관련 페이지를 정리해줘",
        "multi_page_lookup",
        [
            {
                "title": "Current Dummy Landscape",
                "pdf_page": 129,
                "printed_page": 129,
                "chunk_id": "p129",
                "entry_id": "entry_129",
                "field_name": "page_summary",
                "text": "Current Dummy Landscape overview",
                "page_role": "landscape_page",
                "score": 1.0,
            },
            {
                "title": "THOR 50 % Male",
                "pdf_page": 136,
                "printed_page": 136,
                "chunk_id": "p136",
                "entry_id": "entry_136",
                "field_name": "overview",
                "text": "THOR injury criteria",
                "page_role": "criteria_page",
                "score": 1.0,
            },
        ],
        route_policy=route_policy,
    )
    assert "관련 페이지:" in answer["answer"]
    assert "페이지 역할:" in answer["answer"]
