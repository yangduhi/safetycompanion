from __future__ import annotations

import csv
import re
from pathlib import Path

from src.common.runtime import ensure_dir, write_json, write_text


def write_detail_csv(path: Path, rows: list[dict]) -> None:
    ensure_dir(path.parent)
    if not rows:
        write_text(path, "")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown_from_metrics(title: str, metrics: dict[str, float]) -> str:
    lines = [f"# {title}", ""]
    for key in sorted(metrics):
        lines.append(f"- {key}: {metrics[key]}")
    return "\n".join(lines) + "\n"


def freeze_baseline_markdown(label: str, metrics: dict[str, float]) -> str:
    lines = [f"# {label}", "", "## Frozen Metrics", ""]
    for key in sorted(metrics):
        lines.append(f"- {key}: {metrics[key]}")
    return "\n".join(lines) + "\n"


def write_baseline_snapshot(base_dir: Path, label: str, metrics: dict[str, float]) -> tuple[Path, Path]:
    ensure_dir(base_dir)
    json_path = base_dir / f"{label}.json"
    md_path = base_dir / f"{label}.md"
    write_json(json_path, metrics)
    write_text(md_path, freeze_baseline_markdown(label, metrics))
    return json_path, md_path


def write_filtered_detail_csv(path: Path, rows: list[dict], key: str, expected_value: object) -> None:
    filtered = [row for row in rows if row.get(key) == expected_value]
    write_detail_csv(path, filtered)


def write_retrieval_slice_markdown(path: Path, title: str, rows: list[dict]) -> None:
    total = len(rows)
    top1 = sum(1 for row in rows if row.get("top1_hit"))
    top3 = sum(1 for row in rows if row.get("top3_hit"))
    top10 = sum(1 for row in rows if row.get("top10_hit"))
    lines = [
        f"# {title}",
        "",
        f"- total: {total}",
        f"- top1_hit_rate: {round(top1 / total, 4) if total else 0.0}",
        f"- top3_hit_rate: {round(top3 / total, 4) if total else 0.0}",
        f"- top10_hit_rate: {round(top10 / total, 4) if total else 0.0}",
    ]
    write_text(path, "\n".join(lines) + "\n")


def write_reranker_ablation(path: Path, rows: list[dict]) -> None:
    total = len(rows)
    improved = sum(1 for row in rows if row.get("rerank_improved_top1"))
    pre_top1 = sum(1 for row in rows if row.get("pre_rerank_top1_hit"))
    post_top1 = sum(1 for row in rows if row.get("top1_hit"))
    lines = [
        "# Reranker Ablation",
        "",
        f"- total: {total}",
        f"- pre_rerank_top1_hit_rate: {round(pre_top1 / total, 4) if total else 0.0}",
        f"- post_rerank_top1_hit_rate: {round(post_top1 / total, 4) if total else 0.0}",
        f"- rerank_improved_top1_count: {improved}",
    ]
    write_text(path, "\n".join(lines) + "\n")


def contains_korean(text: str | None) -> bool:
    return bool(text and re.search(r"[가-힣]", text))


def matches_exact_anchor(text: str | None) -> bool:
    return bool(text and re.search(r"(fmvss\s*\d+[a-z]?|fmvss\d+[a-z]?|gtr\s*\d+|gtr\d+|adas|aeb|thor)", text, re.IGNORECASE))
