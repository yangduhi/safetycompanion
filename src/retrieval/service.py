from __future__ import annotations

import re
from pathlib import Path

from src.common.config import LoadedConfig
from src.common.runtime import read_jsonl
from src.common.text import tokenize
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

    def _page_hits(self, pages: set[int]) -> list[dict]:
        hits = []
        for chunk in self.chunks:
            if chunk.get("pdf_page") in pages or chunk.get("printed_page") in pages:
                row = dict(chunk)
                row["score"] = 1.0
                hits.append(row)
        return hits

    def _lookup_hits(self, query: str, route: str) -> tuple[list[dict], set[int]]:
        lower = query.lower().strip()
        query_terms = {token for token in tokenize(query) if not token.isdigit()}
        page_targets: set[int] = set()
        candidates: list[dict] = []

        if route == "abbreviation_lookup":
            for key, items in self.abbr_lookup.items():
                if lower == key or lower in key:
                    for item in items:
                        candidates.append(
                            {
                                "chunk_id": f"abbr_{item['abbr'].lower()}_{item['pdf_page']}",
                                "title": item["abbr"],
                                "pdf_page": item["pdf_page"],
                                "printed_page": item.get("printed_page"),
                                "field_name": "expansion",
                                "text": f"{item['abbr']} = {item['expansion']}",
                                "score": 2.0,
                            }
                        )
                        page_targets.add(item["pdf_page"])

        if route in {"page_or_index_lookup", "fallback_general"}:
            for key, items in self.index_lookup.items():
                if lower == key or lower in key or key in lower:
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
                                "field_name": "schedule",
                                "text": f"{item['date']} | {item['location']} | p. {item['target_page']} | {item['title']}",
                                "score": 0.6 + overlap * 0.1,
                            }
                        )

        explicit_pages = {
            int(match)
            for match in re.findall(r"\b(\d{1,3})\b", query)
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

    def retrieve(self, query: str) -> dict:
        route = route_query(query)
        dense_top_k = self.config.get("retrieval", "dense_top_k", default=8)
        lexical_top_k = self.config.get("retrieval", "lexical_top_k", default=8)
        final_top_n = self.config.get("retrieval", "final_top_n", default=5)
        rrf_k = self.config.get("retrieval", "rrf_k", default=60)

        dense_entry = search_dense(self.dense_entry_store, query, dense_top_k) if self.dense_entry_store.exists() else []
        dense_field = search_dense(self.dense_field_store, query, dense_top_k) if self.dense_field_store.exists() else []
        bm25 = search_bm25(self.bm25_store, query, lexical_top_k) if self.bm25_store.exists() else []
        lookup_hits, page_targets = self._lookup_hits(query, route)

        ranked_lists = [lookup_hits, dense_entry, dense_field, bm25]
        if route == "calendar_lookup" and lookup_hits:
            ranked_lists = [lookup_hits]
        elif route == "abbreviation_lookup" and lookup_hits:
            ranked_lists = [lookup_hits, bm25]
        elif route == "page_or_index_lookup" and lookup_hits:
            ranked_lists = [lookup_hits, bm25]

        fused = reciprocal_rank_fusion(ranked_lists, k=rrf_k)
        ranked = rerank(query, fused, top_n=final_top_n)
        return {
            "route": route,
            "page_targets": sorted(page_targets),
            "dense_entry_hits": dense_entry,
            "dense_field_hits": dense_field,
            "bm25_hits": bm25,
            "lookup_hits": lookup_hits,
            "ranked_hits": ranked,
        }
