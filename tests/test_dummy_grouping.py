from src.retrieval.multipage_grouping import secondary_page_gate, seed_priority_score
from src.retrieval.query_normalization import build_query_profile


def test_seed_priority_prefers_specific_anchor_page_for_thor_query():
    profile = build_query_profile("THOR 관련 더미 페이지")
    landscape_page = {
        "title": "Wissen SafetyWissen.com Current Dummy Landscape",
        "text": "THOR 50 % HIII 50 % dummy landscape",
        "field_name": "page_summary",
        "entry_type": "knowledge",
    }
    spec_page = {
        "title": "Wissen SafetyWissen.com Dummies: Weights, Dimensions and Calibration",
        "text": "THOR 50 % Male THOR 5 % Female Qualification Procedures",
        "field_name": "page_summary",
        "entry_type": "knowledge",
    }

    landscape_score, _ = seed_priority_score(landscape_page, profile)
    spec_score, _ = seed_priority_score(spec_page, profile)

    assert spec_score > landscape_score


def test_seed_priority_prefers_landscape_page_for_landscape_query():
    profile = build_query_profile("dummy landscape 관련 페이지들을 모아서 보여줘")
    landscape_page = {
        "title": "Wissen SafetyWissen.com Current Dummy Landscape",
        "text": "THOR 50 % HIII 50 % dummy landscape",
        "field_name": "page_summary",
        "entry_type": "knowledge",
    }
    spec_page = {
        "title": "Wissen SafetyWissen.com Dummies: Weights, Dimensions and Calibration",
        "text": "THOR 50 % Male THOR 5 % Female Qualification Procedures",
        "field_name": "page_summary",
        "entry_type": "knowledge",
    }

    landscape_score, _ = seed_priority_score(landscape_page, profile)
    spec_score, _ = seed_priority_score(spec_page, profile)

    assert landscape_score > spec_score


def test_secondary_gate_rejects_ncap_intrusion():
    profile = build_query_profile("THOR 관련 더미 페이지")
    seed = {
        "title": "Wissen SafetyWissen.com Dummies: Weights, Dimensions and Calibration",
        "text": "THOR 50 % Male THOR 5 % Female Qualification Procedures",
        "field_name": "page_summary",
        "entry_type": "knowledge",
        "page_role": "spec_page",
        "anchor_clusters": ["THOR_CLUSTER", "DUMMY_LANDSCAPE_CLUSTER"],
    }
    candidate = {
        "title": "KNCAP Protocol 2026",
        "text": "NCAP safety protocol overview",
        "field_name": "page_summary",
        "entry_type": "knowledge",
        "page_role": "detail_page",
    }

    accepted, _, features = secondary_page_gate(seed, candidate, profile)

    assert accepted is False
    assert features["rejection_reason"] == "ncap_intrusion"


def test_secondary_gate_accepts_landscape_plus_spec_combo():
    profile = build_query_profile("dummy landscape 관련 페이지들을 모아서 보여줘")
    seed = {
        "title": "Wissen SafetyWissen.com Current Dummy Landscape",
        "text": "THOR 50 % HIII 50 % dummy landscape",
        "field_name": "page_summary",
        "entry_type": "knowledge",
        "page_role": "landscape_page",
        "anchor_clusters": ["THOR_CLUSTER", "HIII_CLUSTER", "DUMMY_LANDSCAPE_CLUSTER"],
    }
    candidate = {
        "title": "Wissen SafetyWissen.com Dummies: Weights, Dimensions and Calibration",
        "text": "THOR 50 % Male THOR 5 % Female Qualification Procedures",
        "field_name": "page_summary",
        "entry_type": "knowledge",
        "page_role": "spec_page",
    }

    accepted, bonus, _ = secondary_page_gate(seed, candidate, profile)

    assert accepted is True
    assert bonus > 0
