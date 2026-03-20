from src.retrieval.query_normalization import build_query_profile


def test_standard_entity_target_for_euro_ncap() -> None:
    profile = build_query_profile("Find entries related to Euro NCAP")
    assert profile["standard_entity_target"] == "EURO NCAP"
