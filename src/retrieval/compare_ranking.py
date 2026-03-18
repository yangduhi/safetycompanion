from __future__ import annotations

from collections import defaultdict


def select_compare_pairs(candidates: list[dict], required_targets: int = 2, pair_limit: int = 2) -> list[dict]:
    grouped: dict[int, list[dict]] = defaultdict(list)
    for item in candidates:
        target_index = item.get("compare_target_index")
        if target_index is None:
            continue
        grouped[int(target_index)].append(item)

    if len(grouped) < required_targets:
        return candidates[:pair_limit]

    selected: list[dict] = []
    seen_entries: set[str] = set()
    for target_index in sorted(grouped):
        ranked = sorted(
            grouped[target_index],
            key=lambda row: float(row.get("rerank_score", row.get("fused_score", row.get("score", 0.0)))),
            reverse=True,
        )
        chosen = None
        for item in ranked:
            entry_id = item.get("entry_id")
            if entry_id and entry_id in seen_entries:
                continue
            chosen = item
            break
        if chosen is None and ranked:
            chosen = ranked[0]
        if chosen:
            selected.append(chosen)
            if chosen.get("entry_id"):
                seen_entries.add(chosen["entry_id"])
        if len(selected) >= pair_limit:
            break
    return selected


def compare_pair_success(selected: list[dict], required_targets: int = 2) -> bool:
    targets = {item.get("compare_target_index") for item in selected if item.get("compare_target_index") is not None}
    entries = {item.get("entry_id") for item in selected if item.get("entry_id")}
    return len(targets) >= required_targets and len(entries) >= required_targets
