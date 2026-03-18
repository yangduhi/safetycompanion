from __future__ import annotations


def reciprocal_rank_fusion(ranked_lists: list[list[dict]], k: int = 60) -> list[dict]:
    scores: dict[str, float] = {}
    payloads: dict[str, dict] = {}
    for ranked in ranked_lists:
        for rank, item in enumerate(ranked, start=1):
            key = item["chunk_id"]
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            payloads[key] = dict(item)
    fused = []
    for chunk_id, score in sorted(scores.items(), key=lambda pair: pair[1], reverse=True):
        row = dict(payloads[chunk_id])
        row["fused_score"] = score
        fused.append(row)
    return fused
