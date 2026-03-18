from __future__ import annotations

import re
from collections import defaultdict
from typing import Iterable


TOPIC_ALIASES = {
    "PASSIVE SAFETY": ["passive safety"],
    "ACTIVE SAFETY & AUTOMATED DRIVING": ["active safety", "automated driving", "adas", "ads"],
    "DUMMY & CRASH TESTING": ["dummy", "crash testing", "crash test", "atd", "thor", "hiii"],
    "SIMULATION & ENGINEERING": ["simulation", "engineering"],
}

DUMMY_FAMILY_ALIASES = {
    "THOR": ["thor", "thor 50", "thor 5", "thor-m"],
    "HYBRID III": ["hybrid iii", "hybrid-iii", "hiii", "hybrid 3"],
    "ATD": ["atd", "anthropomorphic test device"],
    "WORLDSID": ["worldsid"],
    "SID-IIS": ["sid-iis", "sid iis"],
    "BIORID-II": ["biorid-ii", "biorid"],
    "CRABI": ["crabi"],
}

ORGANIZATION_ALIASES = {
    "HUMANETICS EUROPE GMBH": ["humanetics europe gmbh", "humanetics"],
    "GLOBALAUTOREGS.COM": ["globalautoregs.com", "globalautoregs"],
    "CARHS.TRAINING GMBH": ["carhs.training gmbh", "carhs training", "carhs"],
    "POTOMAC ALLIANCE": ["potomac alliance"],
    "NHTSA": ["nhtsa"],
    "BGS BÖHME & GEHRING GMBH": ["bgs böhme & gehring gmbh", "bgs bohme & gehring gmbh", "bgs"],
}

NCAP_ALIASES = {
    "EURO NCAP": ["euro ncap"],
    "US NCAP": ["u.s. ncap", "us ncap"],
    "C-NCAP": ["c-ncap"],
    "JNCAP": ["jncap"],
    "KNCAP": ["kncap"],
    "ANCAP": ["ancap"],
    "ASEAN NCAP": ["asean ncap"],
    "LATIN NCAP": ["latin ncap"],
    "BHARAT NCAP": ["bharat ncap"],
}

STANDARD_PATTERNS = [
    re.compile(r"\bFMVSS\s*([0-9]{2,3}[A-Z]?)\b", re.IGNORECASE),
    re.compile(r"\bGTR\s*([0-9]{1,2})\b", re.IGNORECASE),
    re.compile(r"\bUN\s*R\s*([0-9]{1,3}[A-Z]?)\b", re.IGNORECASE),
    re.compile(r"\bR\s*([0-9]{1,3}[A-Z]?)\b", re.IGNORECASE),
]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def iter_entry_texts(entry: dict) -> Iterable[tuple[str, str]]:
    title = str(entry.get("title") or "").strip()
    if title:
        yield "title", title
    summary = str(entry.get("summary") or "").strip()
    if summary:
        yield "summary", summary
    fields = entry.get("fields") or {}
    if isinstance(fields, dict):
        for field_name, value in fields.items():
            if value:
                yield str(field_name), str(value)


def entry_fulltext(entry: dict) -> str:
    return "\n".join(text for _, text in iter_entry_texts(entry))


def extract_dummy_families(text: str) -> set[str]:
    lowered = text.lower()
    hits = {
        canonical
        for canonical, aliases in DUMMY_FAMILY_ALIASES.items()
        if any(alias in lowered for alias in aliases)
    }
    return hits


def extract_organizations(text: str) -> set[str]:
    lowered = text.lower()
    hits = {
        canonical
        for canonical, aliases in ORGANIZATION_ALIASES.items()
        if any(alias in lowered for alias in aliases)
    }
    return hits


def extract_standards(text: str) -> set[str]:
    hits: set[str] = set()
    normalized = normalize_space(text)
    for pattern in STANDARD_PATTERNS:
        for match in pattern.finditer(normalized):
            raw = match.group(0)
            token = normalize_space(raw.upper().replace("UN R", "UN R"))
            token = token.replace("FMVSS", "FMVSS ").replace("GTR", "GTR ").replace("R ", "R")
            token = normalize_space(token)
            if token.startswith("R") and not token.startswith("UN R"):
                token = f"UN {token}"
            hits.add(token)
    lowered = text.lower()
    for canonical, aliases in NCAP_ALIASES.items():
        if any(alias in lowered for alias in aliases):
            hits.add(canonical)
    return hits


def canonical_topic(section_l1: str | None) -> str | None:
    if not section_l1:
        return None
    normalized = normalize_space(str(section_l1))
    if normalized.lower() == "dummy & crash testing":
        return "DUMMY & CRASH TESTING"
    if normalized.lower() == "active safety & automated driving":
        return "ACTIVE SAFETY & AUTOMATED DRIVING"
    if normalized.lower() == "passive safety":
        return "PASSIVE SAFETY"
    if normalized.lower() == "simulation & engineering":
        return "SIMULATION & ENGINEERING"
    return normalized.upper()


def detect_query_topics(text: str) -> set[str]:
    lowered = text.lower()
    return {
        topic
        for topic, aliases in TOPIC_ALIASES.items()
        if any(alias in lowered for alias in aliases)
    }


def aggregate_node_sources() -> defaultdict[str, dict]:
    return defaultdict(lambda: {"source_entry_ids": set(), "source_pages": set(), "source_fields": set()})
