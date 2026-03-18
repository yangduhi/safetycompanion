from __future__ import annotations

import re
from collections import Counter


EXACT_ANCHOR_PATTERN = re.compile(r"(fmvss\s*\d+[a-z]?|fmvss\d+[a-z]?|gtr\s*\d+|gtr\d+|adas|aeb|thor)", re.IGNORECASE)


def build_error_taxonomy(retrieval_details: list[dict], grounding_details: list[dict]) -> list[dict]:
    grounding_by_question = {row["question"]: row for row in grounding_details}
    failures: list[dict] = []
    for row in retrieval_details:
        question = row["question"]
        grounding = grounding_by_question.get(question, {})
        failure_type = None

        if row.get("question_type") == "compare" and row.get("route_name") != "compare":
            failure_type = "COMPARE_ROUTE_MISS"
        elif row.get("question_type") == "event_lookup" and row.get("route_name") not in {"event_lookup", "page_or_index_lookup"}:
            failure_type = "EVENT_PARAPHRASE_MISS"
        elif row.get("question_type") == "multi_page_lookup" and row.get("page_hit_top10") and not row.get("top1_hit"):
            top_title = str(row.get("top_result_title") or "").lower()
            question = str(row.get("question") or "").lower()
            if any(token in question for token in ["thor", "dummy", "atd", "landscape"]):
                seed_page = row.get("seed_page_selected")
                expected_pages = set(row.get("expected_pdf_pages") or [])
                top_role = str(row.get("top_result_role") or "")
                rejected_secondary_pages = str(row.get("rejected_secondary_pages") or "")
                accepted_secondary_pages = str(row.get("accepted_secondary_pages") or "")
                if seed_page and seed_page not in expected_pages:
                    failure_type = "MULTI_PAGE_COLLAPSE__SEED_PRIORITY_MISS"
                elif "ncap" in top_title:
                    failure_type = "MULTI_PAGE_COLLAPSE__UNRELATED_PAGE_INTRUSION"
                elif top_role in {"training_page", "reference_page"}:
                    failure_type = "MULTI_PAGE_COLLAPSE__ROLE_ASSIGNMENT_FAIL"
                elif rejected_secondary_pages and not accepted_secondary_pages:
                    failure_type = "MULTI_PAGE_COLLAPSE__SECONDARY_PAGE_MISS"
                else:
                    failure_type = "MULTI_PAGE_COLLAPSE__DUMMY_TOPIC_MERGE_FAIL"
            elif top_title and "current dummy landscape" in top_title:
                failure_type = "MULTI_PAGE_COLLAPSE__MISSING_SECONDARY_PAGE"
            else:
                failure_type = "MULTI_PAGE_COLLAPSE__WRONG_PAGE_GROUPING"
        elif EXACT_ANCHOR_PATTERN.search(question) and not row.get("top10_hit"):
            question_lower = str(question).lower()
            if any(token in question_lower for token in ["dummy", "thor", "atd", "landscape"]):
                failure_type = "ANCHOR_NORMALIZATION_FAIL__DUMMY_ALIAS"
            elif re.search(r"(fmvss\d|gtr\d)", question_lower):
                failure_type = "ANCHOR_NORMALIZATION_FAIL__CODE_STYLE"
            else:
                failure_type = "ANCHOR_NORMALIZATION_FAIL__TOKEN_SPLIT"
        elif row.get("top10_hit") and not row.get("top1_hit"):
            failure_type = "DISAMBIGUATION_FAIL"
        elif not row.get("top10_hit") and row.get("route_name") == "fallback_general":
            failure_type = "ROUTE_WRONG"
        elif grounding.get("citation_any_hit") and not grounding.get("grounded_success"):
            failure_type = "GROUNDING_POLICY_FAIL"

        if failure_type:
            failures.append(
                {
                    "question": question,
                    "difficulty": row.get("difficulty"),
                    "question_type": row.get("question_type"),
                    "route_name": row.get("route_name"),
                    "failure_type": failure_type,
                    "top_result_title": row.get("top_result_title"),
                    "top_result_page": row.get("top_result_page"),
                }
            )
    return failures


def error_taxonomy_markdown(rows: list[dict]) -> str:
    counts = Counter(row["failure_type"] for row in rows)
    lines = ["# Error Taxonomy Report", ""]
    if not rows:
        lines.append("- no classified failures")
        return "\n".join(lines) + "\n"
    lines.append("## Counts")
    for key, value in sorted(counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Examples"])
    for row in rows[:20]:
        lines.append(
            f"- {row['failure_type']}: {row['question']} -> {row.get('top_result_title')} (p.{row.get('top_result_page')})"
        )
    return "\n".join(lines) + "\n"
