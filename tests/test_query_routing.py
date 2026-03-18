from src.retrieval.router import route_query


def test_abbreviation_route():
    assert route_query("AEB") == "abbreviation_lookup"


def test_calendar_route():
    assert route_query("20.10.2026 일정 알려줘") == "calendar_lookup"


def test_seminar_route():
    assert route_query("ADAS 세미나 찾아줘") == "seminar_lookup"
