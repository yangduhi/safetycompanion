from src.graph.graph_retriever import retrieve_graph_paths
from src.qa.answer_generator import build_grounded_answer
from src.retrieval.query_normalization import build_query_profile


def test_graph_retriever_returns_entry_hits_for_standard_query():
    query = "show entries related to FMVSS 208"
    profile = build_query_profile(query)
    nodes = [
        {"node_id": "entry:entry_1", "node_type": "Entry", "name": "FMVSS 208 Seminar"},
        {"node_id": "standard:fmvss_208", "node_type": "Standard", "name": "FMVSS 208", "canonical_name": "FMVSS 208"},
    ]
    edges = [
        {
            "edge_id": "edge_1",
            "edge_type": "MENTIONS_STANDARD",
            "source_id": "entry:entry_1",
            "target_id": "standard:fmvss_208",
            "source_entry_id": "entry_1",
            "source_page": 98,
            "source_field": "summary",
            "provenance_text": "FMVSS 208",
            "confidence": 0.88,
        }
    ]

    result = retrieve_graph_paths(query, profile, nodes, edges)

    assert result["matched_nodes"][0]["name"] == "FMVSS 208"
    assert result["entry_hits"][0]["entry_id"] == "entry_1"


def test_relationship_answer_uses_graph_entity_section():
    answer = build_grounded_answer(
        "THOR와 관련된 엔트리를 보여줘",
        "relationship_query",
        [
            {
                "title": "Current Dummy Landscape",
                "pdf_page": 129,
                "printed_page": 129,
                "chunk_id": "p129",
                "entry_id": "entry_129",
                "field_name": "page_summary",
                "text": "Current Dummy Landscape with THOR and Hybrid III",
                "score": 2.4,
                "graph_match_names": ["THOR"],
                "graph_edge_types": ["MENTIONS_DUMMY"],
                "graph_backfill_success": True,
            }
        ],
    )

    assert "그래프 매칭 엔터티:" in answer["answer"]
    assert "THOR" in answer["answer"]
    assert answer["graph_backfill_used"] is True
