from __future__ import annotations


def retrieve_graph_paths(question: str, nodes: list[dict], edges: list[dict]) -> list[dict]:
    lower = question.lower()
    return [edge for edge in edges if lower in str(edge.get("provenance_text", "")).lower()][:5]
