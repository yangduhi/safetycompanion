from __future__ import annotations

from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from src.common.runtime import ensure_dir, read_json, write_json
from src.common.text import tokenize


def _texts(chunks: Iterable[dict]) -> list[str]:
    return [chunk.get("text", "") for chunk in chunks]


def build_dense_store(chunks: list[dict], out_path: Path, max_features: int = 5000, svd_components: int = 128) -> None:
    ensure_dir(out_path.parent)
    texts = _texts(chunks)
    vectorizer = TfidfVectorizer(max_features=max_features, ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(texts)
    svd = None
    dense = matrix
    if matrix.shape[0] >= 2 and matrix.shape[1] >= 2:
        components = max(2, min(svd_components, matrix.shape[0] - 1, matrix.shape[1] - 1))
        if components >= 2:
            svd = TruncatedSVD(n_components=components, random_state=42)
            dense = svd.fit_transform(matrix)
    if hasattr(dense, "toarray"):
        dense = dense.toarray()
    dense = normalize(dense)
    joblib.dump({"chunks": chunks, "vectorizer": vectorizer, "svd": svd, "matrix": dense}, out_path)


def search_dense(store_path: Path, query: str, top_k: int) -> list[dict]:
    store = joblib.load(store_path)
    vectorizer = store["vectorizer"]
    svd = store["svd"]
    query_vector = vectorizer.transform([query])
    if svd is not None:
        query_vector = svd.transform(query_vector)
    if hasattr(query_vector, "toarray"):
        query_vector = query_vector.toarray()
    query_vector = normalize(query_vector)
    scores = cosine_similarity(query_vector, store["matrix"]).ravel()
    ranked_idx = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in ranked_idx:
        row = dict(store["chunks"][int(idx)])
        row["score"] = float(scores[int(idx)])
        results.append(row)
    return results


def build_bm25_store(chunks: list[dict], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    tokenized = [tokenize(chunk.get("text", "")) for chunk in chunks]
    bm25 = BM25Okapi(tokenized)
    joblib.dump({"chunks": chunks, "tokenized": tokenized, "bm25": bm25}, out_path)


def search_bm25(store_path: Path, query: str, top_k: int) -> list[dict]:
    store = joblib.load(store_path)
    bm25 = store["bm25"]
    scores = bm25.get_scores(tokenize(query))
    ranked_idx = np.argsort(scores)[::-1][:top_k]
    results = []
    for idx in ranked_idx:
        row = dict(store["chunks"][int(idx)])
        row["score"] = float(scores[int(idx)])
        results.append(row)
    return results


def persist_lookup_store(data: dict, out_path: Path) -> None:
    ensure_dir(out_path.parent)
    write_json(out_path, data)


def load_lookup_store(path: Path) -> dict:
    if not path.exists():
        return {}
    return read_json(path)
