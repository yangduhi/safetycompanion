from pathlib import Path

from src.common.runtime import read_jsonl
from src.eval.graph_eval import (
    GRAPH_FAILURE_TYPES,
    compute_graph_metrics,
    graph_eval_markdown,
    validate_graph_questions,
)


ROOT = Path(__file__).resolve().parents[1]


def test_graph_hard_questions_contract_is_valid():
    questions = read_jsonl(ROOT / "data" / "eval" / "graph_hard_questions.jsonl")
    errors = validate_graph_questions(questions)
    assert errors == []
    assert len(questions) >= 8


def test_graph_failure_taxonomy_constants_are_defined():
    assert {
        "GRAPH_ENTITY_MISS",
        "GRAPH_FALSE_RELATION",
        "GRAPH_ROUTE_MISS",
        "GRAPH_BACKFILL_FAIL",
        "GRAPH_SUMMARY_UNGROUNDED",
    }.issubset(GRAPH_FAILURE_TYPES)


def test_graph_eval_markdown_contains_expected_metrics():
    metrics = compute_graph_metrics(
        [
            {
                "top1_hit": True,
                "top3_hit": True,
                "backfill_success": True,
                "grounded_success": True,
                "mainline_regression": False,
            },
            {
                "top1_hit": False,
                "top3_hit": True,
                "backfill_success": False,
                "grounded_success": False,
                "mainline_regression": False,
            },
        ]
    )
    markdown = graph_eval_markdown(metrics)
    assert "graph_route_top1_hit_rate" in markdown
    assert "graph_backfill_success_rate" in markdown
