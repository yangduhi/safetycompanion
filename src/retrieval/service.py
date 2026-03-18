from __future__ import annotations

import re
from pathlib import Path

from src.common.config import LoadedConfig
from src.common.paths import ProjectPaths
from src.common.policy import load_route_policy, normalize_abbreviation_key, route_policy_for
from src.common.runtime import read_jsonl
from src.graph.graph_retriever import retrieve_graph_paths
from src.common.text import tokenize
from src.retrieval.compare_ranking import compare_pair_success, select_compare_pairs
from src.retrieval.multipage_grouping import (
    assign_page_role,
    dummy_group_score,
    item_anchor_clusters,
    secondary_page_gate,
    seed_priority_score,
)
from src.retrieval.query_normalization import build_query_profile
from src.retrieval.build_indexes import load_lookup_store, search_bm25, search_dense
from src.retrieval.fusion import reciprocal_rank_fusion
from src.retrieval.reranker import rerank
from src.retrieval.router import route_query


class QueryService:
    def __init__(self, root: Path, config: LoadedConfig) -> None:
        self.root = root
        self.config = config
        self.paths = ProjectPaths(root, config)
        self.chunks = read_jsonl(self.paths.path_from_config("chunks"))
        self.entries = read_jsonl(self.paths.path_from_config("entries"))
        self.entries_by_id = {entry["entry_id"]: entry for entry in self.entries if entry.get("entry_id")}
        self.chunks_by_entry_id: dict[str, list[dict]] = {}
        for chunk in self.chunks:
            entry_id = chunk.get("entry_id")
            if entry_id:
                self.chunks_by_entry_id.setdefault(entry_id, []).append(chunk)
        self.dense_entry_store = self.paths.dense_entry_index
        self.dense_field_store = self.paths.dense_field_index
        self.bm25_store = self.paths.bm25_index
        self.abbr_lookup = load_lookup_store(self.paths.abbreviation_lookup_store)
        self.index_lookup = load_lookup_store(self.paths.back_index_lookup_store)
        self.calendar_lookup = load_lookup_store(self.paths.calendar_lookup_store)
        self.route_policy = load_route_policy(root, config)
        self.graph_enabled = bool(self.config.get("features", "graph_rag", default=False))
        self.graph_nodes = read_jsonl(self.paths.graph_nodes_path) if self.graph_enabled and self.paths.graph_nodes_path.exists() else []
        self.graph_edges = read_jsonl(self.paths.graph_edges_path) if self.graph_enabled and self.paths.graph_edges_path.exists() else []

    def _search_dense_collection(self, query: str, top_k: int) -> tuple[list[dict], list[dict]]:
        dense_entry = search_dense(self.dense_entry_store, query, top_k) if self.dense_entry_store.exists() else []
        dense_field = search_dense(self.dense_field_store, query, top_k) if self.dense_field_store.exists() else []
        return dense_entry, dense_field

    def _page_hits(self, pages: set[int]) -> list[dict]:
        hits = []
        for chunk in self.chunks:
            if chunk.get("pdf_page") in pages or chunk.get("printed_page") in pages:
                row = dict(chunk)
                row["score"] = 1.0
                hits.append(row)
        return hits

    def _anchor_hits(self, query_profile: dict) -> list[dict]:
        anchors = [anchor for anchor in query_profile.get("exact_anchors", []) if anchor]
        title_aliases = [alias for alias in query_profile.get("alias_expansions", []) if alias]
        dummy_clusters = set(query_profile.get("dummy_anchor_clusters", []))
        if not anchors and not title_aliases:
            return []
        hits: list[dict] = []
        seen: set[str] = set()
        for chunk in self.chunks:
            haystack = f"{chunk.get('title', '')} {chunk.get('text', '')}".upper()
            compact_haystack = haystack.replace(" ", "")
            matched = False
            for anchor in anchors:
                compact_anchor = anchor.replace(" ", "")
                if anchor in haystack or compact_anchor in compact_haystack:
                    matched = True
                    break
            if not matched:
                for alias in title_aliases:
                    if alias.lower() in f"{chunk.get('title', '')} {chunk.get('text', '')}".lower():
                        matched = True
                        break
            if not matched:
                continue
            chunk_id = chunk.get("chunk_id")
            if chunk_id in seen:
                continue
            seen.add(chunk_id)
            row = dict(chunk)
            row["score"] = max(float(row.get("score", 0.0)), 2.4)
            if dummy_clusters:
                title_lower = str(chunk.get("title", "")).lower()
                if "thor" in title_lower:
                    row["score"] += 0.5
                if "hiii" in title_lower or "hybrid iii" in title_lower:
                    row["score"] += 0.45
                if "atd" in title_lower:
                    row["score"] += 0.45
            row["anchor_hit"] = True
            hits.append(row)
        return hits

    def _compare_target_hits(self, query_profile: dict, top_k: int) -> tuple[list[dict], list[dict], list[dict]]:
        compare_targets = query_profile.get("compare_targets", [])
        if len(compare_targets) < 2:
            return [], [], []
        generic_compare_terms = {"course", "seminar", "training", "lecture", "together", "multiple", "pages", "two"}
        dense_entry_hits: list[dict] = []
        dense_field_hits: list[dict] = []
        bm25_hits: list[dict] = []
        for index, target in enumerate(compare_targets[:3], start=1):
            target_profile = build_query_profile(target)
            specific_expansions = [term for term in target_profile.get("expanded_terms", []) if term not in generic_compare_terms]
            target_query = " ".join([target_profile.get("normalized_anchor_query", target), *specific_expansions]).strip()
            target_terms = {term for term in tokenize(target_query) if term not in generic_compare_terms}
            target_lower = target.lower()
            target_dense_entry, target_dense_field = self._search_dense_collection(target_query, top_k)
            target_bm25 = search_bm25(self.bm25_store, target_query, top_k) if self.bm25_store.exists() else []

            targeted_title_hits: list[dict] = []
            for chunk in self.chunks:
                if chunk.get("entry_type") not in {"seminar", "event"}:
                    continue
                if chunk.get("chunk_type") not in {"entry_overview_chunk", "field_chunk"}:
                    continue
                title_lower = str(chunk.get("title", "")).lower()
                boost = 0.0
                if "automated driving" in target_lower and title_lower.startswith("automated driving"):
                    boost += 1.2
                if "briefing" in target_lower and "briefing" in title_lower:
                    boost += 1.1
                if "policy" in target_lower and ("policy" in title_lower or "policies" in title_lower):
                    boost += 0.9
                if ("입문" in target or "introduction" in target_lower) and "introduction" in title_lower:
                    boost += 0.35
                if boost > 0:
                    enriched = dict(chunk)
                    enriched["compare_target_index"] = index
                    enriched["score"] = float(enriched.get("score", 0.0)) + boost
                    targeted_title_hits.append(enriched)

            target_dense_entry.extend(targeted_title_hits)
            for row in target_dense_entry:
                enriched = dict(row)
                enriched["compare_target_index"] = index
                title_terms = set(tokenize(enriched.get("title", "")))
                overlap = len(target_terms & title_terms) * 0.08
                prefix_boost = 0.25 if enriched.get("title", "").lower().startswith(target_lower.split()[0]) else 0.0
                phrase_boost = 0.0
                title_lower = enriched.get("title", "").lower()
                if "automated driving" in target_lower and "automated driving" in title_lower:
                    phrase_boost += 0.6
                elif "automated driving" in target_lower:
                    phrase_boost -= 0.45
                if "briefing" in target_lower and "briefing" in title_lower:
                    phrase_boost += 0.7
                elif "briefing" in target_lower:
                    phrase_boost -= 0.35
                if "policy" in target_lower and ("policy" in title_lower or "policies" in title_lower):
                    phrase_boost += 0.5
                elif "policy" in target_lower:
                    phrase_boost -= 0.25
                if ("입문" in target or "introduction" in target_lower) and "introduction" in title_lower:
                    phrase_boost += 0.25
                enriched["score"] = float(enriched.get("score", 0.0)) + 0.15 + overlap + prefix_boost + phrase_boost
                dense_entry_hits.append(enriched)
            for row in target_dense_field:
                enriched = dict(row)
                enriched["compare_target_index"] = index
                title_terms = set(tokenize(enriched.get("title", "")))
                overlap = len(target_terms & title_terms) * 0.08
                prefix_boost = 0.25 if enriched.get("title", "").lower().startswith(target_lower.split()[0]) else 0.0
                phrase_boost = 0.0
                title_lower = enriched.get("title", "").lower()
                if "automated driving" in target_lower and "automated driving" in title_lower:
                    phrase_boost += 0.6
                elif "automated driving" in target_lower:
                    phrase_boost -= 0.45
                if "briefing" in target_lower and "briefing" in title_lower:
                    phrase_boost += 0.7
                elif "briefing" in target_lower:
                    phrase_boost -= 0.35
                if "policy" in target_lower and ("policy" in title_lower or "policies" in title_lower):
                    phrase_boost += 0.5
                elif "policy" in target_lower:
                    phrase_boost -= 0.25
                if ("입문" in target or "introduction" in target_lower) and "introduction" in title_lower:
                    phrase_boost += 0.25
                enriched["score"] = float(enriched.get("score", 0.0)) + 0.15 + overlap + prefix_boost + phrase_boost
                dense_field_hits.append(enriched)
            for row in target_bm25:
                enriched = dict(row)
                enriched["compare_target_index"] = index
                title_terms = set(tokenize(enriched.get("title", "")))
                overlap = len(target_terms & title_terms) * 0.08
                prefix_boost = 0.25 if enriched.get("title", "").lower().startswith(target_lower.split()[0]) else 0.0
                phrase_boost = 0.0
                title_lower = enriched.get("title", "").lower()
                if "automated driving" in target_lower and "automated driving" in title_lower:
                    phrase_boost += 0.6
                elif "automated driving" in target_lower:
                    phrase_boost -= 0.45
                if "briefing" in target_lower and "briefing" in title_lower:
                    phrase_boost += 0.7
                elif "briefing" in target_lower:
                    phrase_boost -= 0.35
                if "policy" in target_lower and ("policy" in title_lower or "policies" in title_lower):
                    phrase_boost += 0.5
                elif "policy" in target_lower:
                    phrase_boost -= 0.25
                if ("입문" in target or "introduction" in target_lower) and "introduction" in title_lower:
                    phrase_boost += 0.25
                enriched["score"] = float(enriched.get("score", 0.0)) + 0.15 + overlap + prefix_boost + phrase_boost
                bm25_hits.append(enriched)
        return dense_entry_hits, dense_field_hits, bm25_hits

    def _lookup_hits(self, query: str, route: str, query_profile: dict) -> tuple[list[dict], set[int]]:
        lower = query.lower().strip()
        normalized_search = query_profile.get("normalized_query", query)
        query_terms = {token for token in tokenize(normalized_search) if not token.isdigit()}
        normalized_query = normalize_abbreviation_key(normalized_search)
        page_targets: set[int] = set()
        candidates: list[dict] = []

        if route == "abbreviation_lookup":
            query_variants = {lower, normalized_query}
            ascii_tokens = [token.lower() for token in tokenize(normalized_search)]
            if ascii_tokens:
                query_variants.add("".join(ascii_tokens))
            for key, items in self.abbr_lookup.items():
                if lower == key or lower in key or key in query_variants:
                    for item in items:
                        candidates.append(
                            {
                                "chunk_id": f"abbr_{item['abbr'].lower()}_{item['pdf_page']}",
                                "title": item["abbr"],
                                "pdf_page": item["pdf_page"],
                                "printed_page": item.get("printed_page"),
                                "entry_type": "abbreviation",
                                "chunk_type": "abbreviation_chunk",
                                "entry_id": None,
                                "field_name": "expansion",
                                "text": f"{item['abbr']} = {item['expansion']}",
                                "score": 2.0,
                                "expansion": item["expansion"],
                                "source_title": item.get("title", "Important Abbreviations"),
                            }
                        )
                        page_targets.add(item["pdf_page"])

        if route in {"page_or_index_lookup", "fallback_general", "multi_page_lookup"}:
            for key, items in self.index_lookup.items():
                if lower == key or lower in key or key in lower or len(query_terms & {token for token in tokenize(key) if not token.isdigit()}) >= 2:
                    for item in items:
                        page_targets.update(item.get("target_pdf_pages", []))

        if route == "calendar_lookup":
            for key, items in self.calendar_lookup.items():
                key_terms = {token for token in tokenize(key) if not token.isdigit()}
                overlap = len(query_terms & key_terms)
                if lower == key or lower in key or key in lower or overlap >= 2:
                    for item in items:
                        page_targets.add(item["target_page"])
                        candidates.append(
                            {
                                "chunk_id": f"calendar_{item['source_pdf_page']}_{item['target_page']}_{item['title']}",
                                "title": item["title"],
                                "pdf_page": item["source_pdf_page"],
                                "printed_page": None,
                                "entry_type": "calendar",
                                "chunk_type": "calendar_chunk",
                                "entry_id": None,
                                "field_name": "schedule",
                                "text": f"{item['date']} | {item['location']} | p. {item['target_page']} | {item['title']}",
                                "score": 0.6 + overlap * 0.1,
                            }
                        )

        explicit_pages = {
            int(match)
            for match in re.findall(r"\b(\d{1,3})\b", normalized_search)
            if int(match) <= 224
        }
        if route == "page_or_index_lookup" and explicit_pages:
            page_targets.update(explicit_pages)

        page_hits = self._page_hits(page_targets)
        if route == "calendar_lookup":
            candidates = page_hits + candidates
        else:
            candidates.extend(page_hits)
        return candidates, page_targets

    def _filter_by_route_policy(self, route: str, candidates: list[dict], query_profile: dict | None = None) -> list[dict]:
        policy = route_policy_for(self.route_policy, route)
        allowed_entry_types = set(policy.get("allowed_entry_types", []))
        allowed_chunk_types = set(policy.get("allowed_chunk_types", []))
        normalized_query = (query_profile or {}).get("normalized_query", "").lower()
        if route == "multi_page_lookup" and "knowledge page" in normalized_query:
            allowed_entry_types = {"knowledge", "index"}
        if route == "recommendation" and "measurement" in normalized_query:
            allowed_entry_types = {"seminar"}
        dummy_clusters = set((query_profile or {}).get("dummy_anchor_clusters", []))
        dummy_title_terms = ["dummy", "thor", "hiii", "hybrid iii", "atd", "worldsid", "sid-iis", "calibration", "landscape"]
        if route == "multi_page_lookup" and dummy_clusters:
            allowed_entry_types = {"knowledge", "seminar", "event"}
        filtered: list[dict] = []
        for item in candidates:
            entry_type = item.get("entry_type")
            chunk_type = item.get("chunk_type")
            entry_ok = not allowed_entry_types or entry_type in allowed_entry_types
            chunk_ok = not allowed_chunk_types or chunk_type in allowed_chunk_types
            if route == "multi_page_lookup" and dummy_clusters:
                title_haystack = f"{item.get('title', '')}".lower()
                section_haystack = f"{item.get('section_l1', '')}".lower()
                title_hit = any(term in title_haystack for term in dummy_title_terms)
                section_knowledge_hit = (
                    entry_type == "knowledge"
                    and "dummy" in section_haystack
                    and "DUMMY_LANDSCAPE_CLUSTER" in dummy_clusters
                )
                dummy_ok = title_hit or section_knowledge_hit
                if not dummy_ok:
                    continue
            if entry_ok and chunk_ok:
                filtered.append(item)
        if filtered:
            return filtered
        if route == "fallback_general":
            return candidates
        return []

    def _apply_multi_page_policy(self, ranked: list[dict], top_n: int) -> list[dict]:
        selected: list[dict] = []
        seen_pages: set[int] = set()
        seen_sections: set[str] = set()
        for item in ranked:
            page = item.get("pdf_page")
            section = item.get("section_l1")
            score = float(item.get("rerank_score", item.get("fused_score", item.get("score", 0.0))))
            if page not in seen_pages:
                diversity_bonus = 0.15 if section and section not in seen_sections else 0.0
                row = dict(item)
                row["rerank_score"] = round(score + diversity_bonus, 4)
                selected.append(row)
                seen_pages.add(page)
                if section:
                    seen_sections.add(section)
            if len(selected) >= top_n:
                break
        return sorted(selected, key=lambda row: row["rerank_score"], reverse=True)

    def _apply_multi_page_grouping_v2(self, ranked: list[dict], query_profile: dict, top_n: int) -> list[dict]:
        dummy_hints = set(query_profile.get("dummy_anchor_hints", []))
        selected: list[dict] = []
        seen_pages: set[int] = set()
        seen_entries: set[str] = set()
        for item in ranked:
            page = item.get("pdf_page")
            entry_id = item.get("entry_id")
            title_lower = str(item.get("title", "")).lower()
            text_lower = str(item.get("text", "")).lower()
            score = float(item.get("rerank_score", item.get("fused_score", item.get("score", 0.0))))
            group_bonus = 0.0

            if dummy_hints:
                if any(anchor.lower() in title_lower or anchor.lower() in text_lower for anchor in dummy_hints):
                    group_bonus += 0.45
                if item.get("entry_type") == "knowledge":
                    group_bonus += 0.2

            if page in seen_pages:
                continue
            if entry_id and entry_id in seen_entries:
                group_bonus -= 0.2

            row = dict(item)
            row["rerank_score"] = round(score + group_bonus, 4)
            row["group_bonus"] = round(group_bonus, 4)
            selected.append(row)
            seen_pages.add(page)
            if entry_id:
                seen_entries.add(entry_id)
            if len(selected) >= top_n:
                break
        return sorted(selected, key=lambda row: row["rerank_score"], reverse=True)

    def _apply_multi_page_grouping_v3(self, ranked: list[dict], query_profile: dict, top_n: int) -> tuple[list[dict], dict]:
        rescored: list[dict] = []
        for item in ranked:
            base_score = float(item.get("rerank_score", item.get("fused_score", item.get("score", 0.0))))
            group_score, group_features = dummy_group_score(item, query_profile)
            page_role = assign_page_role(item, query_profile)
            seed_score, seed_features = seed_priority_score(item, query_profile)
            anchor_clusters = sorted(item_anchor_clusters(item))
            row = dict(item)
            row["page_role"] = page_role
            row["group_score"] = group_score
            row["group_features"] = group_features
            row["anchor_clusters"] = anchor_clusters
            row["seed_priority_score"] = seed_score
            row["seed_priority_features"] = seed_features
            row["rerank_score"] = round(base_score + group_score, 4)
            rescored.append(row)

        if not rescored:
            return [], {
                "seed_page_selected": None,
                "seed_score": None,
                "seed_role": None,
                "accepted_secondary_pages": [],
                "rejected_secondary_pages": [],
                "page_role_summary": [],
            }

        rescored.sort(key=lambda row: row["rerank_score"], reverse=True)
        seed = max(
            rescored,
            key=lambda row: (
                float(row.get("seed_priority_score", 0.0)),
                float(row.get("rerank_score", 0.0)),
            ),
        )
        seed = dict(seed)
        seed["seed_selected"] = True
        seed["selection_rank"] = 1
        seed_role = seed.get("page_role", "detail_page")
        selected: list[dict] = [seed]
        seen_pages: set[int] = {seed.get("pdf_page")}
        seen_entries: set[str] = {seed.get("entry_id")} if seed.get("entry_id") else set()
        accepted_secondary_debug: list[dict] = []
        rejected_secondary_debug: list[dict] = []
        secondary_candidates: list[dict] = []

        for item in rescored:
            page = item.get("pdf_page")
            entry_id = item.get("entry_id")
            if page in seen_pages:
                continue
            accepted, gate_bonus, gate_features = secondary_page_gate(seed, item, query_profile)
            candidate_debug = {
                "pdf_page": page,
                "title": item.get("title"),
                "page_role": item.get("page_role"),
                "anchor_clusters": item.get("anchor_clusters"),
                "gate_bonus": gate_bonus,
                "gate_features": gate_features,
            }
            if not accepted:
                rejected_secondary_debug.append(candidate_debug)
                continue

            score = float(item.get("rerank_score", 0.0)) + gate_bonus
            group_features = dict(item.get("group_features", {}))
            group_features["secondary_gate_bonus"] = gate_bonus
            group_features["secondary_gate_features"] = gate_features
            if entry_id and entry_id in seen_entries:
                score -= 0.2
                group_features["duplicate_penalty"] = True
            row = dict(item)
            row["rerank_score"] = round(score, 4)
            row["group_features"] = group_features
            row["secondary_gate_bonus"] = gate_bonus
            row["secondary_gate_features"] = gate_features
            secondary_candidates.append(row)
            accepted_secondary_debug.append(candidate_debug)

        secondary_candidates.sort(key=lambda row: row["rerank_score"], reverse=True)
        for rank_offset, item in enumerate(secondary_candidates, start=2):
            page = item.get("pdf_page")
            entry_id = item.get("entry_id")
            if page in seen_pages:
                continue
            if entry_id and entry_id in seen_entries:
                continue
            row = dict(item)
            row["selection_rank"] = rank_offset
            selected.append(row)
            seen_pages.add(page)
            if entry_id:
                seen_entries.add(entry_id)
            if len(selected) >= top_n:
                break

        group_debug = {
            "seed_page_selected": seed.get("pdf_page"),
            "seed_score": seed.get("seed_priority_score"),
            "seed_role": seed_role,
            "seed_title": seed.get("title"),
            "accepted_secondary_pages": [row.get("pdf_page") for row in selected[1:]],
            "accepted_secondary_titles": [row.get("title") for row in selected[1:]],
            "rejected_secondary_pages": [row.get("pdf_page") for row in rejected_secondary_debug],
            "rejected_secondary_titles": [row.get("title") for row in rejected_secondary_debug],
            "page_role_summary": [f"p.{row.get('pdf_page')}:{row.get('page_role')}" for row in selected],
            "accepted_secondary_candidates": accepted_secondary_debug,
            "rejected_secondary_candidates": rejected_secondary_debug,
        }
        return selected, group_debug

    def _apply_compare_policy(self, ranked: list[dict], top_n: int) -> list[dict]:
        pair = select_compare_pairs(ranked, required_targets=2, pair_limit=max(2, min(top_n, 3)))
        if compare_pair_success(pair, required_targets=2):
            return pair
        return ranked[:top_n]

    def _best_chunk_for_entry(self, entry_id: str, route: str = "relationship_query") -> dict | None:
        candidates = self.chunks_by_entry_id.get(entry_id, [])
        if not candidates:
            return None
        preferred_fields = route_policy_for(self.route_policy, route).get("preferred_fields", [])
        preferred_chunk_types = {"field_chunk", "entry_overview_chunk", "knowledge_table_chunk"}

        def field_rank(chunk: dict) -> int:
            field_name = chunk.get("field_name")
            if field_name in preferred_fields:
                return preferred_fields.index(field_name)
            return len(preferred_fields) + 10

        filtered = [chunk for chunk in candidates if chunk.get("chunk_type") in preferred_chunk_types]
        ranked = sorted(filtered or candidates, key=lambda chunk: (field_rank(chunk), len(str(chunk.get("text", "")))))
        return ranked[0] if ranked else None

    def _backfill_graph_hits(self, graph_trace: dict) -> list[dict]:
        backfilled: list[dict] = []
        for hit in graph_trace.get("entry_hits", []):
            entry_id = hit.get("entry_id")
            if not entry_id:
                continue
            chunk = self._best_chunk_for_entry(entry_id, route="relationship_query")
            entry = self.entries_by_id.get(entry_id)
            if chunk:
                row = dict(chunk)
            elif entry:
                row = {
                    "chunk_id": f"graph_backfill_{entry_id}",
                    "entry_id": entry_id,
                    "entry_type": entry.get("entry_type"),
                    "chunk_type": "entry_overview_chunk",
                    "field_name": "overview",
                    "title": entry.get("title"),
                    "pdf_page": (entry.get("source_pages") or [None])[0],
                    "printed_page": (entry.get("printed_pages") or [None])[0],
                    "section_l1": entry.get("section_l1"),
                    "text": entry.get("summary", ""),
                }
            else:
                continue

            row["score"] = float(hit.get("score", 0.0)) + 2.0
            row["graph_score"] = float(hit.get("score", 0.0))
            row["graph_match_names"] = hit.get("matched_node_names", [])
            row["graph_match_types"] = hit.get("matched_node_types", [])
            row["graph_edge_types"] = hit.get("matched_edge_types", [])
            row["graph_backfill_success"] = True
            row["graph_source_pages"] = hit.get("source_pages", [])
            backfilled.append(row)
        return backfilled

    def _relationship_query_results(self, query: str, query_profile: dict, top_n: int) -> tuple[list[dict], dict]:
        if not self.graph_enabled or not self.graph_nodes or not self.graph_edges:
            return [], {"graph_enabled": False, "matched_nodes": [], "matched_edges": [], "entry_hits": []}
        graph_trace = retrieve_graph_paths(query, query_profile, self.graph_nodes, self.graph_edges)
        backfilled = self._backfill_graph_hits(graph_trace)
        ranked = sorted(backfilled, key=lambda row: float(row.get("graph_score", row.get("score", 0.0))), reverse=True)[:top_n]
        graph_debug = {
            "graph_enabled": True,
            "matched_nodes": [node.get("name") for node in graph_trace.get("matched_nodes", [])],
            "matched_edges_count": len(graph_trace.get("matched_edges", [])),
            "matched_entry_ids": [row.get("entry_id") for row in graph_trace.get("entry_hits", [])],
            "backfilled_entry_ids": [row.get("entry_id") for row in ranked],
            "backfill_success": bool(ranked),
        }
        return ranked, graph_debug

    def retrieve(self, query: str) -> dict:
        query_profile = build_query_profile(query)
        search_query = query_profile.get("normalized_query", query)
        route = route_query(
            query,
            normalized_query=search_query,
            is_multi_page_hint=query_profile.get("is_multi_page_hint", False),
            compare_hint=query_profile.get("compare_hint", False),
            relationship_hint=query_profile.get("relationship_hint", False),
            page_lookup_hint=query_profile.get("page_lookup_hint", False),
            event_hint=query_profile.get("event_hint", False),
        )
        dense_top_k = self.config.get("retrieval", "dense_top_k", default=8)
        lexical_top_k = self.config.get("retrieval", "lexical_top_k", default=8)
        final_top_n = self.config.get("retrieval", "final_top_n", default=5)
        rrf_k = self.config.get("retrieval", "rrf_k", default=60)

        if route == "relationship_query":
            relationship_hits, graph_debug = self._relationship_query_results(query, query_profile, final_top_n)
            if relationship_hits:
                return {
                    "route": route,
                    "query_profile": query_profile,
                    "normalized_query": search_query,
                    "page_targets": sorted({item.get("pdf_page") for item in relationship_hits if item.get("pdf_page") is not None}),
                    "dense_entry_hits": [],
                    "dense_field_hits": [],
                    "bm25_hits": [],
                    "lookup_hits": [],
                    "anchor_hits": [],
                    "fused_hits": relationship_hits,
                    "ranked_hits": relationship_hits,
                    "compare_pair_success": None,
                    "group_debug": None,
                    "graph_debug": graph_debug,
                    "policy": route_policy_for(self.route_policy, route),
                }

        dense_entry, dense_field = self._search_dense_collection(search_query, dense_top_k)
        bm25 = search_bm25(self.bm25_store, search_query, lexical_top_k) if self.bm25_store.exists() else []
        lookup_hits, page_targets = self._lookup_hits(query, route, query_profile=query_profile)
        anchor_hits = self._anchor_hits(query_profile)

        if route == "compare":
            compare_dense_entry, compare_dense_field, compare_bm25 = self._compare_target_hits(query_profile, dense_top_k)
            if compare_dense_entry or compare_dense_field or compare_bm25:
                dense_entry = compare_dense_entry
                dense_field = compare_dense_field
                bm25 = compare_bm25

        dense_entry = self._filter_by_route_policy(route, dense_entry, query_profile=query_profile)
        dense_field = self._filter_by_route_policy(route, dense_field, query_profile=query_profile)
        bm25 = self._filter_by_route_policy(route, bm25, query_profile=query_profile)
        lookup_hits = self._filter_by_route_policy(route, lookup_hits, query_profile=query_profile)
        anchor_hits = self._filter_by_route_policy(route, anchor_hits, query_profile=query_profile)

        ranked_lists = [anchor_hits, lookup_hits, dense_entry, dense_field, bm25]
        if route == "calendar_lookup" and lookup_hits:
            ranked_lists = [anchor_hits, lookup_hits]
        elif route == "abbreviation_lookup" and lookup_hits:
            ranked_lists = [anchor_hits, lookup_hits, bm25]
        elif route == "page_or_index_lookup" and lookup_hits:
            ranked_lists = [anchor_hits, lookup_hits, bm25]
        elif route == "multi_page_lookup" and lookup_hits:
            ranked_lists = [anchor_hits, lookup_hits, dense_field, bm25]
        elif route == "compare":
            ranked_lists = [anchor_hits, dense_field, dense_entry, bm25, lookup_hits]
        elif route == "event_lookup":
            ranked_lists = [anchor_hits, dense_entry, dense_field, bm25, lookup_hits]

        fused = reciprocal_rank_fusion(ranked_lists, k=rrf_k)
        pre_rerank = list(fused)
        ranked = rerank(query, fused, top_n=max(final_top_n, 10), route=route, query_profile=query_profile)
        group_debug = None
        if route == "compare":
            ranked = self._apply_compare_policy(ranked, final_top_n)
        elif route == "multi_page_lookup":
            ranked, group_debug = self._apply_multi_page_grouping_v3(ranked, query_profile=query_profile, top_n=final_top_n)
        else:
            ranked = ranked[:final_top_n]
        return {
            "route": route,
            "query_profile": query_profile,
            "normalized_query": search_query,
            "page_targets": sorted(page_targets),
            "dense_entry_hits": dense_entry,
            "dense_field_hits": dense_field,
            "bm25_hits": bm25,
            "lookup_hits": lookup_hits,
            "anchor_hits": anchor_hits,
            "fused_hits": pre_rerank,
            "ranked_hits": ranked,
            "compare_pair_success": compare_pair_success(ranked, required_targets=2) if route == "compare" else None,
            "group_debug": group_debug,
            "graph_debug": None,
            "policy": route_policy_for(self.route_policy, route),
        }
