from __future__ import annotations

import csv
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
