from __future__ import annotations

import re
import unicodedata
from typing import Iterable


def normalize_whitespace(text: str) -> str:
    return re.sub(r"[ \t]+", " ", text).strip()


def slugify(text: str) -> str:
    value = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_") or "item"


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9][A-Za-z0-9+/._-]*", text.lower())


def first_non_empty(lines: Iterable[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def compact_lines(lines: Iterable[str]) -> list[str]:
    return [normalize_whitespace(line) for line in lines if normalize_whitespace(line)]


def split_blocks(text: str) -> list[str]:
    parts = [normalize_whitespace(part) for part in re.split(r"\n\s*\n", text)]
    return [part for part in parts if part]
