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
