from __future__ import annotations

from collections import Counter

from src.graph.entity_extractor import extract_entities
from src.graph.relation_extractor import extract_relations


def build_graph(entries: list[dict]) -> tuple[list[dict], list[dict]]:
    return extract_entities(entries), extract_relations(entries)


def graph_schema_markdown(nodes: list[dict], edges: list[dict]) -> str:
    node_counts = Counter(node.get("node_type", "Unknown") for node in nodes)
    edge_counts = Counter(edge.get("edge_type", "Unknown") for edge in edges)
    lines = ["# Graph Schema", ""]
    lines.append("## Node Counts")
    for key, value in sorted(node_counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Edge Counts"])
    for key, value in sorted(edge_counts.items()):
        lines.append(f"- {key}: {value}")
    return "\n".join(lines) + "\n"
