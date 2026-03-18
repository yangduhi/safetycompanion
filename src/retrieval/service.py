from __future__ import annotations

import re
from pathlib import Path

from src.common.config import LoadedConfig
from src.common.policy import load_route_policy, normalize_abbreviation_key, route_policy_for
from src.common.runtime import read_jsonl
from src.common.text import tokenize
from src.retrieval.query_normalization import build_query_profile
from src.retrieval.build_indexes import load_lookup_store, search_bm25, search_dense
from src.retrieval.fusion import reciprocal_rank_fusion
from src.retrieval.reranker import rerank
from src.retrieval.router import route_query


class QueryService:
    def __init__(self, root: Path, config: LoadedConfig) -> None:
        self.root = root
        self.config = config
        self.chunks = read_jsonl(root / config.get("paths", "chunks"))
        self.entries = read_jsonl(root / config.get("paths", "entries"))
        self.dense_entry_store = root / "indexes" / "dense_entry" / "index.joblib"
        self.dense_field_store = root / "indexes" / "dense_field" / "index.joblib"
        self.bm25_store = root / "indexes" / "bm25" / "index.joblib"
        self.abbr_lookup = load_lookup_store(root / "indexes" / "lookup" / "abbreviations.json")
        self.index_lookup = load_lookup_store(root / "indexes" / "lookup" / "back_index.json")
        self.calendar_lookup = load_lookup_store(root / "indexes" / "lookup" / "calendar.json")
        self.route_policy = load_route_policy(root, config)

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
        filtered: list[dict] = []
        for item in candidates:
            entry_type = item.get("entry_type")
            chunk_type = item.get("chunk_type")
            entry_ok = not allowed_entry_types or entry_type in allowed_entry_types
            chunk_ok = not allowed_chunk_types or chunk_type in allowed_chunk_types
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

    def retrieve(self, query: str) -> dict:
        query_profile = build_query_profile(query)
        search_query = query_profile.get("normalized_query", query)
        route = route_query(
            query,
            normalized_query=search_query,
            is_multi_page_hint=query_profile.get("is_multi_page_hint", False),
            compare_hint=query_profile.get("compare_hint", False),
            page_lookup_hint=query_profile.get("page_lookup_hint", False),
            event_hint=query_profile.get("event_hint", False),
        )
        dense_top_k = self.config.get("retrieval", "dense_top_k", default=8)
        lexical_top_k = self.config.get("retrieval", "lexical_top_k", default=8)
        final_top_n = self.config.get("retrieval", "final_top_n", default=5)
        rrf_k = self.config.get("retrieval", "rrf_k", default=60)

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
        if route == "multi_page_lookup":
            ranked = self._apply_multi_page_policy(ranked, final_top_n)
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
            "policy": route_policy_for(self.route_policy, route),
        }
