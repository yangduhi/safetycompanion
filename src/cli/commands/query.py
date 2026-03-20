from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from src.cli.shared import finalize_command, load_runtime_context
from src.workflows.query import run_query


def _contains_korean(text: str) -> bool:
    return bool(re.search(r"[가-힣]", text))


def _looks_like_encoding_drift(text: str) -> bool:
    suspicious_tokens = ["??", "? ", " ?"]
    common_query_words = ["topic", "entry", "entries", "page", "compare", "recommend", "schedule"]
    lowered = text.lower()
    return not _contains_korean(text) and any(token in text for token in suspicious_tokens) and any(word in lowered for word in common_query_words)


def _resolve_question(args: argparse.Namespace) -> str:
    if args.question_file:
        question = Path(args.question_file).read_text(encoding="utf-8").strip()
    else:
        question = str(args.question or "").strip()
    if not question:
        raise ValueError("query requires either a positional question or --question-file")
    return question


def run(args: argparse.Namespace) -> int:
    question = _resolve_question(args)
    if _looks_like_encoding_drift(question):
        print(
            "Warning: the query text looks encoding-corrupted. If you intended to ask in Korean, prefer --question-file with a UTF-8 text file.",
            file=sys.stderr,
        )
    ctx = load_runtime_context(args.config)
    manifest = ctx.init_run_manifest()
    return finalize_command(ctx, manifest, "query", run_query(ctx, question))
