from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from src.common.config import LoadedConfig
from src.common.runtime import ensure_dir


_CONTAINER_KEYS = ("kids", "children", "rows", "cells", "items")


def _page_spec(pages: list[int]) -> str:
    return ",".join(str(page) for page in sorted(set(pages)))


def is_opendataloader_available(command: str = "opendataloader-pdf") -> bool:
    return shutil.which(command) is not None


def _find_output_json(output_dir: Path, pdf_path: Path) -> Path:
    preferred = list(output_dir.rglob(f"{pdf_path.stem}.json"))
    if preferred:
        return preferred[0]
    candidates = sorted(output_dir.rglob("*.json"))
    if not candidates:
        raise FileNotFoundError(f"No OpenDataLoader JSON output found in {output_dir}")
    return candidates[0]


def _iter_node_text(node: Any, inherited_page: int | None = None) -> list[tuple[int | None, str]]:
    if isinstance(node, list):
        items: list[tuple[int | None, str]] = []
        for item in node:
            items.extend(_iter_node_text(item, inherited_page=inherited_page))
        return items

    if not isinstance(node, dict):
        return []

    page_number = node.get("page number", inherited_page)
    content = node.get("content")
    node_type = str(node.get("type", "")).lower()
    has_children = any(key in node for key in _CONTAINER_KEYS)
    items: list[tuple[int | None, str]] = []

    # Emit leaf-node content directly; recurse into structural containers.
    if isinstance(content, str) and content.strip():
        if not has_children or node_type in {"heading", "paragraph", "caption", "formula", "list", "listitem", "list-item", "text"}:
            items.append((page_number, content))

    for key in _CONTAINER_KEYS:
        children = node.get(key)
        if isinstance(children, list):
            items.extend(_iter_node_text(children, inherited_page=page_number))

    return items


def extract_page_texts_from_odl_json(payload: Any) -> dict[int, str]:
    page_lines: dict[int, list[str]] = {}
    for page_number, text in _iter_node_text(payload):
        if page_number is None:
            continue
        bucket = page_lines.setdefault(int(page_number), [])
        for line in str(text).splitlines():
            stripped = line.strip()
            if stripped:
                bucket.append(stripped)
    return {page: "\n".join(lines) for page, lines in page_lines.items() if lines}


def parse_pages_with_opendataloader(
    pdf_path: Path,
    pages: list[int],
    temp_dir: Path,
    config: LoadedConfig,
) -> dict[int, str]:
    if not pages:
        return {}

    command = str(config.get("parse", "auxiliary", "command", default="opendataloader-pdf"))
    if not is_opendataloader_available(command):
        raise FileNotFoundError(f"{command} is not available on PATH")

    page_spec = _page_spec(pages)
    run_key = hashlib.sha1(f"{pdf_path.name}:{page_spec}".encode("utf-8")).hexdigest()[:10]
    run_dir = ensure_dir(temp_dir / f"odl_{pdf_path.stem}_{run_key}")
    cli = [
        command,
        str(pdf_path),
        "-o",
        str(run_dir),
        "-f",
        "json",
        "--pages",
        page_spec,
    ]

    if bool(config.get("parse", "auxiliary", "quiet", default=True)):
        cli.append("--quiet")

    reading_order = config.get("parse", "auxiliary", "reading_order", default="xycut")
    if reading_order:
        cli.extend(["--reading-order", str(reading_order)])

    table_method = config.get("parse", "auxiliary", "table_method", default="cluster")
    if table_method:
        cli.extend(["--table-method", str(table_method)])

    content_safety_off = config.get("parse", "auxiliary", "content_safety_off", default=[])
    if content_safety_off:
        cli.extend(["--content-safety-off", ",".join(str(item) for item in content_safety_off)])

    if bool(config.get("parse", "auxiliary", "use_struct_tree", default=False)):
        cli.append("--use-struct-tree")

    mode = str(config.get("parse", "auxiliary", "mode", default="local")).lower()
    if mode == "hybrid":
        hybrid_backend = str(config.get("parse", "auxiliary", "hybrid_backend", default="docling-fast"))
        cli.extend(["--hybrid", hybrid_backend])
        hybrid_mode = config.get("parse", "auxiliary", "hybrid_mode", default="auto")
        if hybrid_mode:
            cli.extend(["--hybrid-mode", str(hybrid_mode)])
        hybrid_url = config.get("parse", "auxiliary", "hybrid_url", default=None)
        if hybrid_url:
            cli.extend(["--hybrid-url", str(hybrid_url)])
        hybrid_timeout_ms = config.get("parse", "auxiliary", "hybrid_timeout_ms", default=None)
        if hybrid_timeout_ms:
            cli.extend(["--hybrid-timeout", str(hybrid_timeout_ms)])
        if bool(config.get("parse", "auxiliary", "hybrid_fallback", default=False)):
            cli.append("--hybrid-fallback")

    try:
        subprocess.run(cli, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise RuntimeError(f"OpenDataLoader invocation failed: {message}") from exc

    output_json = _find_output_json(run_dir, pdf_path)
    payload = json.loads(output_json.read_text(encoding="utf-8"))
    return extract_page_texts_from_odl_json(payload)
