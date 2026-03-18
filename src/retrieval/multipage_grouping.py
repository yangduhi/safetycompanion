from __future__ import annotations

from src.retrieval.query_normalization import DUMMY_CLUSTER_RULES, STRONG_DUMMY_CLUSTERS


SEED_ROLE_PRIORS = {
    "landscape": {
        "landscape_page": 0.95,
        "overview_page": 0.45,
        "spec_page": 0.2,
        "detail_page": 0.15,
        "training_page": -0.45,
        "reference_page": -0.35,
    },
    "specific_anchor": {
        "spec_page": 0.8,
        "detail_page": 0.72,
        "overview_page": 0.28,
        "landscape_page": -0.2,
        "training_page": -0.55,
        "reference_page": -0.4,
    },
    "mixed": {
        "spec_page": 0.6,
        "landscape_page": 0.5,
        "detail_page": 0.45,
        "overview_page": 0.35,
        "training_page": -0.2,
        "reference_page": -0.25,
    },
    "training": {
        "training_page": 0.65,
        "spec_page": 0.3,
        "detail_page": 0.25,
        "overview_page": 0.1,
        "landscape_page": -0.1,
        "reference_page": -0.2,
    },
    "generic_dummy": {
        "landscape_page": 0.7,
        "overview_page": 0.45,
        "spec_page": 0.35,
        "detail_page": 0.25,
        "training_page": -0.25,
        "reference_page": -0.25,
    },
    "generic": {
        "overview_page": 0.25,
        "detail_page": 0.2,
        "spec_page": 0.15,
        "landscape_page": 0.1,
        "training_page": -0.25,
        "reference_page": -0.25,
    },
}


def _item_text(item: dict) -> str:
    return f"{item.get('title', '')} {item.get('text', '')}".lower()


def item_anchor_clusters(item: dict) -> set[str]:
    haystack = _item_text(item)
    clusters: set[str] = set()
    for cluster, aliases in DUMMY_CLUSTER_RULES.items():
        if any(alias in haystack for alias in aliases):
            clusters.add(cluster)
    return clusters


def assign_page_role(item: dict, query_profile: dict) -> str:
    title = str(item.get("title", "")).lower()
    text = str(item.get("text", "")).lower()
    field_name = str(item.get("field_name", "")).lower()
    entry_type = str(item.get("entry_type", "")).lower()

    if "current dummy landscape" in title or ("landscape" in title and "dummy" in title):
        return "landscape_page"
    if any(token in title for token in ["weights, dimensions and calibration", "calibration"]):
        return "spec_page"
    if "dummy-trainings" in title or ("training" in title and "dummy" in title):
        return "training_page"
    if entry_type == "index" or field_name in {"mentioned_entities", "keyword"}:
        return "reference_page"
    if "overview" in title or ("overview" in text and "dummy" in text):
        return "overview_page"
    if any(token in f"{title} {text}" for token in ["thor", "hiii", "hybrid iii", "atd", "sid-iis", "worldsid"]):
        return "detail_page"
    return "detail_page"


def dummy_group_score(item: dict, query_profile: dict) -> tuple[float, dict]:
    title = str(item.get("title", "")).lower()
    text = str(item.get("text", "")).lower()
    section = str(item.get("section_l1", "")).lower()
    clusters = set(query_profile.get("dummy_anchor_clusters", []))
    item_clusters = item_anchor_clusters(item)
    role = assign_page_role(item, query_profile)

    score = 0.0
    features: dict[str, float | bool | str | list[str]] = {
        "assigned_role": role,
        "item_anchor_clusters": sorted(item_clusters),
    }

    overlap = clusters & item_clusters
    if overlap:
        score += len(overlap) * 0.42
        features["anchor_cluster_overlap"] = sorted(overlap)

    if "dummy | crash test" in section or "dummy & crash" in section:
        score += 0.6
        features["section_dummy_boost"] = True

    if any(token in f"{title} {text}" for token in ["current dummy landscape", "dummy landscape", "dummies", "calibration"]):
        score += 0.35
        features["dummy_page_phrase_boost"] = True

    if role in {"landscape_page", "spec_page", "detail_page"}:
        score += 0.18
        features["role_grouping_boost"] = role

    if role == "training_page":
        score -= 0.08
        features["training_soft_penalty"] = True

    if "ncap-tests" in title or "ncap" in title:
        score -= 1.25
        features["ncap_intrusion_penalty"] = True

    return round(score, 4), features


def seed_priority_score(item: dict, query_profile: dict) -> tuple[float, dict]:
    title = str(item.get("title", "")).lower()
    text = str(item.get("text", "")).lower()
    role = assign_page_role(item, query_profile)
    item_clusters = item_anchor_clusters(item)
    query_clusters = set(query_profile.get("dummy_anchor_clusters", []))
    query_mode = str(query_profile.get("dummy_query_mode", "generic"))
    grouping_request_hint = bool(query_profile.get("grouping_request_hint"))
    training_hint = bool(query_profile.get("dummy_training_hint"))

    score = SEED_ROLE_PRIORS.get(query_mode, SEED_ROLE_PRIORS["generic"]).get(role, 0.0)
    features: dict[str, float | bool | str | list[str]] = {
        "query_mode": query_mode,
        "role_prior": round(score, 4),
        "assigned_role": role,
        "item_anchor_clusters": sorted(item_clusters),
    }

    overlap = item_clusters & query_clusters
    if overlap:
        overlap_boost = 0.18 * len(overlap)
        score += overlap_boost
        features["anchor_overlap_boost"] = round(overlap_boost, 4)
        features["anchor_cluster_overlap"] = sorted(overlap)

    if "current dummy landscape" in title:
        if query_mode in {"landscape", "generic_dummy"}:
            score += 0.42
            features["landscape_title_boost"] = 0.42
        elif query_mode == "specific_anchor" and not grouping_request_hint:
            score -= 0.35
            features["landscape_specific_penalty"] = -0.35

    if role == "training_page" and not training_hint:
        score -= 0.35
        features["training_seed_penalty"] = -0.35

    if role == "reference_page":
        score -= 0.25
        features["reference_seed_penalty"] = -0.25

    if item.get("entry_type") == "seminar" and not training_hint:
        score -= 0.12
        features["seminar_seed_penalty"] = -0.12

    if "ncap" in f"{title} {text}":
        score -= 1.4
        features["ncap_seed_penalty"] = -1.4

    if query_mode == "specific_anchor" and role in {"spec_page", "detail_page"} and overlap & STRONG_DUMMY_CLUSTERS:
        score += 0.2
        features["specific_anchor_seed_bonus"] = 0.2

    return round(score, 4), features


def role_compatibility_bonus(seed_role: str, candidate_role: str) -> float:
    if seed_role == candidate_role:
        return 0.05

    strong_pairs = {
        ("landscape_page", "spec_page"),
        ("landscape_page", "detail_page"),
        ("overview_page", "spec_page"),
        ("overview_page", "detail_page"),
        ("spec_page", "detail_page"),
        ("detail_page", "spec_page"),
        ("spec_page", "training_page"),
        ("detail_page", "training_page"),
    }
    weak_pairs = {
        ("spec_page", "overview_page"),
        ("detail_page", "overview_page"),
        ("landscape_page", "training_page"),
        ("training_page", "spec_page"),
    }

    if (seed_role, candidate_role) in strong_pairs:
        return 0.32
    if (seed_role, candidate_role) in weak_pairs:
        return 0.12
    if candidate_role == "reference_page":
        return -0.4
    return -0.3


def secondary_page_gate(seed: dict, candidate: dict, query_profile: dict) -> tuple[bool, float, dict]:
    query_clusters = set(query_profile.get("dummy_anchor_clusters", []))
    query_mode = str(query_profile.get("dummy_query_mode", "generic"))
    training_hint = bool(query_profile.get("dummy_training_hint"))
    seed_clusters = set(seed.get("anchor_clusters") or item_anchor_clusters(seed))
    candidate_clusters = item_anchor_clusters(candidate)
    candidate_role = candidate.get("page_role") or assign_page_role(candidate, query_profile)
    seed_role = seed.get("page_role") or assign_page_role(seed, query_profile)
    candidate_title = str(candidate.get("title", "")).lower()

    features: dict[str, float | bool | str | list[str]] = {
        "seed_role": seed_role,
        "candidate_role": candidate_role,
        "candidate_anchor_clusters": sorted(candidate_clusters),
    }

    if "ncap" in candidate_title:
        features["rejection_reason"] = "ncap_intrusion"
        return False, -1.0, features

    family_overlap = candidate_clusters & (seed_clusters | query_clusters)
    if family_overlap:
        overlap_bonus = 0.15 * len(family_overlap)
        features["family_overlap"] = sorted(family_overlap)
    else:
        overlap_bonus = 0.0
        if candidate_role not in {"training_page"}:
            features["rejection_reason"] = "anchor_family_mismatch"
            return False, -0.45, features

    role_bonus = role_compatibility_bonus(seed_role, candidate_role)
    features["role_bonus"] = role_bonus
    if role_bonus < 0 and candidate_role != "training_page":
        features["rejection_reason"] = "role_incompatible"
        return False, role_bonus, features

    bonus = overlap_bonus + role_bonus
    if candidate_role == "training_page" and not training_hint:
        bonus -= 0.12
        features["training_candidate_penalty"] = -0.12

    if query_mode == "specific_anchor" and candidate_role == "landscape_page" and "landscape" not in str(query_profile.get("normalized_query", "")).lower():
        bonus -= 0.08
        features["specific_anchor_landscape_penalty"] = -0.08

    if query_mode in {"landscape", "generic_dummy"} and candidate_role == "spec_page":
        bonus += 0.08
        features["landscape_spec_bonus"] = 0.08

    return True, round(bonus, 4), features
