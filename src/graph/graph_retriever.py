from __future__ import annotations

from collections import defaultdict

from src.graph.catalog import (
    detect_query_topics,
    extract_dummy_families,
    extract_organizations,
    extract_standards,
)


def _match_graph_nodes(question: str, query_profile: dict, nodes: list[dict]) -> list[dict]:
    text = " ".join(
        [
            question,
            str(query_profile.get("normalized_query", "")),
            " ".join(query_profile.get("alias_expansions", [])),
            " ".join(query_profile.get("expanded_terms", [])),
        ]
    )
    targets: set[tuple[str, str]] = set()
    for dummy in extract_dummy_families(text):
        targets.add(("DummyFamily", dummy))
    for standard in extract_standards(text):
        targets.add(("Standard", standard))
    for org in extract_organizations(text):
        targets.add(("Organization", org))
    for topic in detect_query_topics(text):
        targets.add(("Topic", topic))
    for anchor in query_profile.get("exact_anchors", []):
        if anchor.startswith("FMVSS") or anchor.startswith("GTR") or anchor.startswith("UN R") or anchor.startswith("R"):
            targets.add(("Standard", anchor))
        elif anchor in {"THOR", "HIII", "ATD"}:
            canonical_dummy = "HYBRID III" if anchor == "HIII" else anchor
            targets.add(("DummyFamily", canonical_dummy))

    matched: list[dict] = []
    for node in nodes:
        if node.get("node_type") == "Entry":
            continue
        key = (str(node.get("node_type")), str(node.get("canonical_name") or node.get("name")))
        if key in targets:
            matched.append(node)
    return matched


def retrieve_graph_paths(question: str, query_profile: dict, nodes: list[dict], edges: list[dict]) -> dict:
    matched_nodes = _match_graph_nodes(question, query_profile, nodes)
    matched_target_ids = {node["node_id"] for node in matched_nodes}
    entry_hits: dict[str, dict] = {}
    matched_edges: list[dict] = []

    for edge in edges:
        source_id = str(edge.get("source_id", ""))
        target_id = str(edge.get("target_id", ""))
        edge_type = str(edge.get("edge_type", ""))
        if target_id in matched_target_ids and source_id.startswith("entry:"):
            matched_edges.append(edge)
            entry_id = str(edge.get("source_entry_id") or source_id.replace("entry:", "", 1))
            hit = entry_hits.setdefault(
                entry_id,
                {
                    "entry_id": entry_id,
                    "score": 0.0,
                    "matched_node_names": set(),
                    "matched_node_types": set(),
                    "matched_edge_types": set(),
                    "source_pages": set(),
                },
            )
            hit["score"] += float(edge.get("confidence", 0.0)) + 0.2
            target_node = next((node for node in matched_nodes if node["node_id"] == target_id), None)
            if target_node:
                hit["matched_node_names"].add(str(target_node.get("name")))
                hit["matched_node_types"].add(str(target_node.get("node_type")))
            hit["matched_edge_types"].add(edge_type)
            if edge.get("source_page") is not None:
                hit["source_pages"].add(int(edge["source_page"]))

    target_count = max(1, len(matched_nodes))
    ranked_hits: list[dict] = []
    for hit in entry_hits.values():
        coverage_bonus = 0.25 * (len(hit["matched_node_names"]) / target_count)
        ranked_hits.append(
            {
                "entry_id": hit["entry_id"],
                "score": round(hit["score"] + coverage_bonus, 4),
                "matched_node_names": sorted(hit["matched_node_names"]),
                "matched_node_types": sorted(hit["matched_node_types"]),
                "matched_edge_types": sorted(hit["matched_edge_types"]),
                "source_pages": sorted(hit["source_pages"]),
            }
        )

    ranked_hits.sort(key=lambda row: (-float(row["score"]), row["entry_id"]))
    return {
        "matched_nodes": matched_nodes,
        "matched_edges": matched_edges,
        "entry_hits": ranked_hits,
    }
