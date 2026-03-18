from src.graph.graph_builder import build_graph


def test_build_graph_creates_minimal_nodes_and_edges():
    entries = [
        {
            "entry_id": "entry_1",
            "entry_type": "seminar",
            "title": "International Safety and Crash-Test Regulations",
            "section_l1": "Active Safety & Automated Driving",
            "summary": "FMVSS 208 and Euro NCAP are discussed with John Creamer from GlobalAutoRegs.com and Dr. Thomas Kinsky of Humanetics Europe GmbH. THOR and automated driving are mentioned.",
            "source_pages": [20],
            "fields": {},
        }
    ]

    nodes, edges = build_graph(entries)
    node_types = {node["node_type"] for node in nodes}
    edge_types = {edge["edge_type"] for edge in edges}

    assert {"Entry", "Topic", "Standard", "DummyFamily", "Organization"}.issubset(node_types)
    assert {"BELONGS_TO_TOPIC", "MENTIONS_STANDARD", "MENTIONS_DUMMY", "MENTIONS_ORG"}.issubset(edge_types)


def test_graph_edges_include_provenance_fields():
    entries = [
        {
            "entry_id": "entry_1",
            "entry_type": "knowledge",
            "title": "Current Dummy Landscape",
            "section_l1": "Dummy & Crash Testing",
            "summary": "THOR and Hybrid III dummy overview.",
            "source_pages": [129],
            "fields": {"page_summary": "THOR and Hybrid III dummy overview."},
        }
    ]
    _, edges = build_graph(entries)
    edge = edges[0]

    assert "source_entry_id" in edge
    assert "source_page" in edge
    assert "source_field" in edge
    assert "provenance_text" in edge
    assert "extraction_method" in edge
