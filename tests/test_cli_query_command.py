from __future__ import annotations

import argparse
from pathlib import Path

from src.cli.commands.query import _looks_like_encoding_drift, _resolve_question


def test_resolve_question_uses_positional_value() -> None:
    args = argparse.Namespace(question="Find entries related to Euro NCAP", question_file=None)
    assert _resolve_question(args) == "Find entries related to Euro NCAP"


def test_resolve_question_reads_utf8_file(tmp_path: Path) -> None:
    path = tmp_path / "question.txt"
    path.write_text("Passive Safety topic에 속한 핵심 엔트리를 보여줘\n", encoding="utf-8")
    args = argparse.Namespace(question=None, question_file=str(path))
    assert _resolve_question(args) == "Passive Safety topic에 속한 핵심 엔트리를 보여줘"


def test_detects_suspicious_encoding_drift() -> None:
    assert _looks_like_encoding_drift("Passive Safety topic? ?? ?? ???? ???") is True
    assert _looks_like_encoding_drift("Passive Safety topic에 속한 핵심 엔트리를 보여줘") is False
