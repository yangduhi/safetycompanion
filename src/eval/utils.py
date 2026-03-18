from __future__ import annotations

from collections import defaultdict


def safe_rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def aggregate_boolean_metric(
    details: list[dict],
    field_name: str,
    prefix: str,
) -> dict[str, float]:
    metrics: dict[str, float] = {}
    metrics[prefix] = safe_rate(sum(1 for row in details if row.get(field_name)), len(details))

    by_difficulty: dict[str, list[dict]] = defaultdict(list)
    by_type: dict[str, list[dict]] = defaultdict(list)
    for row in details:
        by_difficulty[row.get("difficulty", "unknown")].append(row)
        by_type[row.get("question_type", "unknown")].append(row)

    for key, rows in sorted(by_difficulty.items()):
        metrics[f"{prefix}__difficulty__{key}"] = safe_rate(sum(1 for row in rows if row.get(field_name)), len(rows))
    for key, rows in sorted(by_type.items()):
        metrics[f"{prefix}__type__{key}"] = safe_rate(sum(1 for row in rows if row.get(field_name)), len(rows))
    return metrics
