from __future__ import annotations


def assign_page_role(item: dict, query_profile: dict) -> str:
    title = str(item.get("title", "")).lower()
    text = str(item.get("text", "")).lower()
    if "landscape" in title or "current dummy landscape" in title:
        return "landscape_page"
    if "thor" in title:
        return "criteria_page"
    if "dummies" in title or "calibration" in title:
        return "spec_page"
    if "dummy-trainings" in title or "training" in title:
        return "training_page"
    if "overview" in title or "overview" in text:
        return "overview_page"
    return "detail_page"


def dummy_group_score(item: dict, query_profile: dict) -> tuple[float, dict]:
    title = str(item.get("title", "")).lower()
    text = str(item.get("text", "")).lower()
    section = str(item.get("section_l1", "")).lower()
    clusters = set(query_profile.get("dummy_anchor_clusters", []))
    score = 0.0
    features: dict[str, float | bool | str] = {}

    if clusters:
        if "THOR_CLUSTER" in clusters and "thor" in f"{title} {text}":
            score += 0.6
            features["thor_match"] = True
        if "HIII_CLUSTER" in clusters and any(token in f"{title} {text}" for token in ["hiii", "hybrid iii"]):
            score += 0.55
            features["hiii_match"] = True
        if "ATD_CLUSTER" in clusters and any(token in f"{title} {text}" for token in ["atd", "anthropomorphic test device"]):
            score += 0.55
            features["atd_match"] = True
        if "DUMMY_LANDSCAPE_CLUSTER" in clusters and any(token in f"{title} {text}" for token in ["dummy", "landscape"]):
            score += 0.65
            features["dummy_landscape_match"] = True

    if "dummy | crash test" in section or "dummy & crash" in section:
        score += 0.35
        features["section_dummy_boost"] = True

    if "ncap-tests" in title or "ncap" in title:
        score -= 0.75
        features["ncap_intrusion_penalty"] = True

    role = assign_page_role(item, query_profile)
    features["assigned_role"] = role
    if role in {"landscape_page", "criteria_page", "spec_page"}:
        score += 0.2
    return round(score, 4), features
