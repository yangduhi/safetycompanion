from __future__ import annotations

from collections import Counter

from src.eval.utils import safe_rate


REQUIRED_GRAPH_QUESTION_KEYS = {
    "qid",
    "query",
    "difficulty",
    "query_type",
    "graph_route_type",
    "expected_entities",
    "expected_pages",
    "expected_titles",
    "expected_relation_types",
    "requires_graph",
    "requires_backfill",
    "requires_multi_hop",
}

GRAPH_FAILURE_TYPES = {
    "GRAPH_ENTITY_MISS",
    "GRAPH_FALSE_RELATION",
    "GRAPH_ROUTE_MISS",
    "GRAPH_BACKFILL_FAIL",
    "GRAPH_SUMMARY_UNGROUNDED",
}


def validate_graph_questions(questions: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(questions, start=1):
        missing = sorted(REQUIRED_GRAPH_QUESTION_KEYS - set(row))
        if missing:
            errors.append(f"row {index}: missing keys={missing}")
        qid = str(row.get("qid", "")).strip()
        if not qid:
            errors.append(f"row {index}: empty qid")
        elif qid in seen_ids:
            errors.append(f"row {index}: duplicate qid={qid}")
        else:
            seen_ids.add(qid)
        if not isinstance(row.get("expected_entities"), list) or not row.get("expected_entities"):
            errors.append(f"row {index}: expected_entities must be non-empty list")
        if not isinstance(row.get("expected_pages"), list) or not row.get("expected_pages"):
            errors.append(f"row {index}: expected_pages must be non-empty list")
        if not isinstance(row.get("expected_titles"), list) or not row.get("expected_titles"):
            errors.append(f"row {index}: expected_titles must be non-empty list")
        if not isinstance(row.get("expected_relation_types"), list) or not row.get("expected_relation_types"):
            errors.append(f"row {index}: expected_relation_types must be non-empty list")
    return errors


def compute_graph_metrics(rows: list[dict]) -> dict[str, float]:
    total = len(rows)
    return {
        "graph_route_top1_hit_rate": safe_rate(sum(1 for row in rows if row.get("top1_hit")), total),
        "graph_route_top3_hit_rate": safe_rate(sum(1 for row in rows if row.get("top3_hit")), total),
        "graph_backfill_success_rate": safe_rate(sum(1 for row in rows if row.get("backfill_success")), total),
        "graph_grounded_success_rate": safe_rate(sum(1 for row in rows if row.get("grounded_success")), total),
        "graph_regression_on_mainline": safe_rate(sum(1 for row in rows if row.get("mainline_regression")), total),
    }


def graph_eval_markdown(metrics: dict[str, float]) -> str:
    lines = ["# Graph Eval", ""]
    for key in sorted(metrics):
        lines.append(f"- {key}: {metrics[key]}")
    return "\n".join(lines) + "\n"


def graph_failure_markdown(rows: list[dict]) -> str:
    lines = ["# Graph Failure Cases", ""]
    if not rows:
        lines.append("- no graph failures")
        return "\n".join(lines) + "\n"
    counts = Counter(str(row.get("graph_failure_type", "UNKNOWN")) for row in rows)
    lines.append("## Counts")
    for key, value in sorted(counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Examples"])
    for row in rows[:20]:
        lines.append(f"- {row.get('graph_failure_type')}: {row.get('query')} -> {row.get('top_result_title')}")
    return "\n".join(lines) + "\n"


def merge_graph_rows(retrieval_details: list[dict], answer_details: list[dict]) -> list[dict]:
    answer_by_question = {row["question"]: row for row in answer_details}
    rows: list[dict] = []
    for row in retrieval_details:
        answer = answer_by_question.get(row["question"], {})
        rows.append(
            {
                "qid": row.get("qid"),
                "query": row.get("question"),
                "query_type": row.get("question_type"),
                "graph_route_type": row.get("graph_route_type"),
                "top1_hit": row.get("top1_hit", False),
                "top3_hit": row.get("top3_hit", False),
                "graph_nodes_hit": row.get("graph_nodes_hit", 0),
                "graph_edges_hit": row.get("graph_edges_hit", 0),
                "backfill_success": answer.get("graph_backfill_success", False),
                "grounded_success": answer.get("grounded_success", False),
                "top_result_title": row.get("top_result_title"),
                "top_result_page": row.get("top_result_page"),
                "mainline_regression": False,
            }
        )
    return rows


def build_graph_failure_rows(rows: list[dict]) -> list[dict]:
    failures: list[dict] = []
    for row in rows:
        failure_type = None
        if not row.get("graph_nodes_hit"):
            failure_type = "GRAPH_ENTITY_MISS"
        elif not row.get("top3_hit"):
            failure_type = "GRAPH_FALSE_RELATION"
        elif not row.get("backfill_success"):
            failure_type = "GRAPH_BACKFILL_FAIL"
        elif not row.get("grounded_success"):
            failure_type = "GRAPH_SUMMARY_UNGROUNDED"

        if failure_type:
            failures.append(
                {
                    "qid": row.get("qid"),
                    "query": row.get("query"),
                    "graph_failure_type": failure_type,
                    "top_result_title": row.get("top_result_title"),
                }
            )
    return failures
