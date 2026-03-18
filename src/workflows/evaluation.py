from __future__ import annotations

from pathlib import Path

from src.common.pipeline import RunContext
from src.common.runtime import write_jsonl, write_text
from src.eval.answer_eval import evaluate_answers
from src.eval.error_taxonomy import build_error_taxonomy, error_taxonomy_markdown
from src.eval.extraction_eval import evaluate_extraction
from src.eval.graph_eval import build_graph_failure_rows, compute_graph_metrics, graph_eval_markdown, graph_failure_markdown, merge_graph_rows
from src.eval.parse_eval import evaluate_parse
from src.eval.reporting import (
    contains_korean,
    markdown_from_metrics,
    matches_exact_anchor,
    write_baseline_snapshot,
    write_detail_csv,
    write_filtered_detail_csv,
    write_retrieval_slice_markdown,
    write_reranker_ablation,
)
from src.eval.retrieval_eval import evaluate_retrieval
from src.qa.answer_generator import build_grounded_answer
from src.retrieval.service import QueryService
from src.workflows.result import WorkflowResult


def run_evaluation(ctx: RunContext, baseline_label: str | None = None) -> WorkflowResult:
    page_manifest = ctx.read_jsonl("page_manifest")
    entries = ctx.read_jsonl("entries")
    abbreviations = ctx.read_jsonl("abbreviations")
    calendar_entries = ctx.read_jsonl("calendar_entries")
    gold_questions = ctx.read_jsonl("gold_questions")
    adversarial_questions = ctx.read_jsonl("adversarial_questions")
    multi_page_hard_questions = ctx.read_jsonl("multi_page_hard_questions")
    graph_hard_questions = ctx.read_jsonl("graph_hard_questions")
    graph_eval_questions = [
        {
            **row,
            "question": row.get("question") or row.get("query"),
            "question_type": row.get("question_type") or row.get("query_type"),
            "expected_pdf_pages": row.get("expected_pdf_pages") or row.get("expected_pages") or [],
            "expected_titles": row.get("expected_titles") or [],
        }
        for row in graph_hard_questions
    ]

    service = QueryService(ctx.root, ctx.config)
    graph_enabled = bool(ctx.config.get("features", "graph_rag", default=False))

    def retrieve(question: str) -> dict:
        return service.retrieve(question)

    def answer_query(question: str) -> dict:
        trace = service.retrieve(question)
        answer = build_grounded_answer(question, trace["route"], trace["ranked_hits"], route_policy=service.route_policy)
        return {"trace": trace, "answer": answer}

    metrics = {}
    metrics.update(evaluate_parse(page_manifest))
    metrics.update(evaluate_extraction(entries, abbreviations, calendar_entries))
    retrieval_metrics, retrieval_details = evaluate_retrieval(gold_questions, retrieve)
    answer_metrics, answer_details = evaluate_answers(gold_questions, answer_query)
    adversarial_retrieval_metrics, adversarial_retrieval_details = evaluate_retrieval(adversarial_questions, retrieve)
    adversarial_answer_metrics, adversarial_answer_details = evaluate_answers(adversarial_questions, answer_query)
    multi_page_hard_retrieval_metrics, multi_page_hard_retrieval_details = evaluate_retrieval(multi_page_hard_questions, retrieve)
    multi_page_hard_answer_metrics, multi_page_hard_answer_details = evaluate_answers(multi_page_hard_questions, answer_query)
    metrics.update(retrieval_metrics)
    metrics.update(answer_metrics)
    metrics.update({f"adversarial__{key}": value for key, value in adversarial_retrieval_metrics.items()})
    metrics.update({f"adversarial__{key}": value for key, value in adversarial_answer_metrics.items()})
    metrics.update({f"multi_page_hard__{key}": value for key, value in multi_page_hard_retrieval_metrics.items()})
    metrics.update({f"multi_page_hard__{key}": value for key, value in multi_page_hard_answer_metrics.items()})
    graph_rows: list[dict] = []
    graph_failures: list[dict] = []
    graph_eval_path = ctx.output_path("graph_eval.md")
    graph_eval_entity_relation_path = ctx.output_path("graph_eval_entity_relation.md")
    graph_eval_topic_cluster_path = ctx.output_path("graph_eval_topic_cluster.md")
    graph_eval_topic_cluster_v2_path = ctx.output_path("graph_eval_topic_cluster_v2.md")
    graph_eval_standard_relation_path = ctx.output_path("graph_eval_standard_relation.md")
    graph_route_details_path = ctx.output_path("graph_route_details.csv")
    graph_route_details_v2_path = ctx.output_path("graph_route_details_v2.csv")
    graph_route_details_v3_path = ctx.output_path("graph_route_details_v3.csv")
    graph_failure_cases_path = ctx.output_path("graph_failure_cases.jsonl")
    graph_failure_cases_v2_path = ctx.output_path("graph_failure_cases_v2.jsonl")
    graph_failure_cases_v3_path = ctx.output_path("graph_failure_cases_v3.jsonl")
    if graph_enabled and graph_eval_questions:
        graph_retrieval_metrics, graph_retrieval_details = evaluate_retrieval(graph_eval_questions, retrieve)
        graph_answer_metrics, graph_answer_details = evaluate_answers(graph_eval_questions, answer_query)
        graph_rows = merge_graph_rows(graph_retrieval_details, graph_answer_details)
        graph_failures = build_graph_failure_rows(graph_rows)
        graph_metrics = compute_graph_metrics(graph_rows)
        metrics.update({f"graph__{key}": value for key, value in graph_retrieval_metrics.items()})
        metrics.update({f"graph__{key}": value for key, value in graph_answer_metrics.items()})
        metrics.update(graph_metrics)
        write_text(graph_eval_path, graph_eval_markdown(graph_metrics))
        write_detail_csv(graph_route_details_path, graph_rows)
        write_detail_csv(graph_route_details_v2_path, graph_rows)
        write_detail_csv(graph_route_details_v3_path, graph_rows)
        write_jsonl(graph_failure_cases_path, graph_failures)
        write_jsonl(graph_failure_cases_v2_path, graph_failures)
        write_jsonl(graph_failure_cases_v3_path, graph_failures)
        entity_rows = [
            row
            for row in graph_rows
            if row.get("query_type") in {"dummy_family_relation", "standard_topic_relation", "organization_entry_relation"}
        ]
        write_text(graph_eval_entity_relation_path, graph_eval_markdown(compute_graph_metrics(entity_rows)))
        write_text(
            graph_eval_topic_cluster_path,
            graph_eval_markdown(compute_graph_metrics([row for row in graph_rows if row.get("query_type") == "topic_cluster_relation"])),
        )
        write_text(
            graph_eval_topic_cluster_v2_path,
            graph_eval_markdown(compute_graph_metrics([row for row in graph_rows if row.get("query_type") == "topic_cluster_relation"])),
        )
        write_text(
            graph_eval_standard_relation_path,
            graph_eval_markdown(compute_graph_metrics([row for row in graph_rows if row.get("query_type") == "standard_topic_relation"])),
        )
    else:
        graph_eval_path = None
        graph_eval_entity_relation_path = None
        graph_eval_topic_cluster_path = None
        graph_eval_topic_cluster_v2_path = None
        graph_eval_standard_relation_path = None
        graph_route_details_path = None
        graph_route_details_v2_path = None
        graph_route_details_v3_path = None
        graph_failure_cases_path = None
        graph_failure_cases_v2_path = None
        graph_failure_cases_v3_path = None

    summary_path = ctx.output_path("eval_summary.md")
    retrieval_report_path = ctx.output_path("retrieval_report.md")
    citation_report_path = ctx.output_path("citation_report.md")
    grounding_report_path = ctx.output_path("grounding_report.md")
    retrieval_details_path = ctx.output_path("retrieval_details.csv")
    retrieval_top1_details_path = ctx.output_path("retrieval_top1_details.csv")
    retrieval_top3_details_path = ctx.output_path("retrieval_top3_details.csv")
    citation_details_path = ctx.output_path("citation_details.csv")
    grounding_details_path = ctx.output_path("grounding_details.csv")
    korean_query_eval_path = ctx.output_path("korean_query_eval.md")
    hard_route_eval_path = ctx.output_path("hard_route_eval.md")
    multi_page_eval_path = ctx.output_path("multi_page_eval.md")
    multi_page_group_details_path = ctx.output_path("multi_page_group_details.csv")
    dummy_hardslice_eval_path = ctx.output_path("dummy_hardslice_eval.md")
    multi_page_group_details_v2_path = ctx.output_path("multi_page_group_details_v2.csv")
    multi_page_group_details_v4_path = ctx.output_path("multi_page_group_details_v4.csv")
    multi_page_dummy_eval_path = ctx.output_path("multi_page_dummy_eval.md")
    multi_page_dummy_eval_v3_path = ctx.output_path("multi_page_dummy_eval_v3.md")
    recommendation_eval_path = ctx.output_path("recommendation_eval.md")
    compare_eval_path = ctx.output_path("compare_eval.md")
    compare_pair_details_path = ctx.output_path("compare_pair_details.csv")
    compare_grounding_report_path = ctx.output_path("compare_grounding_report.md")
    event_lookup_eval_path = ctx.output_path("event_lookup_eval.md")
    exact_anchor_eval_path = ctx.output_path("exact_anchor_eval.md")
    reranker_ablation_path = ctx.output_path("reranker_ablation.md")
    error_taxonomy_report_path = ctx.output_path("error_taxonomy_report.md")
    error_taxonomy_report_v3_path = ctx.output_path("error_taxonomy_report_v3.md")
    error_taxonomy_report_v4_path = ctx.output_path("error_taxonomy_report_v4.md")
    compare_regression_report_path = ctx.output_path("compare_regression_report.md")
    error_analysis_path = ctx.output_path("error_analysis.csv")
    failure_cases_path = ctx.output_path("failure_cases.jsonl")

    retrieval_report_metrics = {
        key: value
        for key, value in metrics.items()
        if key.startswith("retrieval_") or key.startswith("adversarial__retrieval_") or key in {"recall_at_10", "page_hit_rate"}
    }
    citation_report_metrics = {key: value for key, value in metrics.items() if key.startswith("citation_") or key.startswith("adversarial__citation_")}
    grounding_report_metrics = {
        key: value
        for key, value in metrics.items()
        if key.startswith("grounded_")
        or key.startswith("field_grounding_")
        or key.startswith("adversarial__grounded_")
        or key.startswith("adversarial__field_grounding_")
    }

    write_text(summary_path, markdown_from_metrics("Evaluation Summary", metrics))
    write_text(retrieval_report_path, markdown_from_metrics("Retrieval Report", retrieval_report_metrics))
    write_text(citation_report_path, markdown_from_metrics("Citation Report", citation_report_metrics))
    write_text(grounding_report_path, markdown_from_metrics("Grounding Report", grounding_report_metrics))
    write_detail_csv(retrieval_details_path, retrieval_details + adversarial_retrieval_details + multi_page_hard_retrieval_details)
    write_filtered_detail_csv(retrieval_top1_details_path, retrieval_details + adversarial_retrieval_details, "top1_hit", True)
    write_filtered_detail_csv(retrieval_top3_details_path, retrieval_details + adversarial_retrieval_details, "top3_hit", True)
    write_detail_csv(citation_details_path, answer_details + multi_page_hard_answer_details)
    write_detail_csv(grounding_details_path, answer_details + adversarial_answer_details + multi_page_hard_answer_details)

    all_retrieval_rows = retrieval_details + adversarial_retrieval_details + multi_page_hard_retrieval_details
    korean_rows = [row for row in all_retrieval_rows if contains_korean(row.get("question"))]
    hard_rows = [row for row in all_retrieval_rows if row.get("difficulty") == "hard"]
    multi_page_rows = [row for row in all_retrieval_rows if row.get("question_type") == "multi_page_lookup"]
    dummy_rows = [
        row
        for row in all_retrieval_rows
        if row.get("question_type") == "multi_page_lookup"
        and any(token in str(row.get("question", "")).lower() for token in ["thor", "dummy", "atd", "landscape"])
    ]
    recommendation_rows = [row for row in all_retrieval_rows if row.get("question_type") == "recommendation"]
    compare_rows = [row for row in all_retrieval_rows if row.get("question_type") == "compare"]
    event_rows = [row for row in all_retrieval_rows if row.get("question_type") == "event_lookup"]
    exact_anchor_rows = [row for row in all_retrieval_rows if matches_exact_anchor(row.get("question"))]
    write_retrieval_slice_markdown(korean_query_eval_path, "Korean Query Eval", korean_rows)
    write_retrieval_slice_markdown(hard_route_eval_path, "Hard Route Eval", hard_rows)
    write_retrieval_slice_markdown(multi_page_eval_path, "Multi Page Eval", multi_page_rows)
    write_retrieval_slice_markdown(dummy_hardslice_eval_path, "Dummy Hard Slice Eval", dummy_rows)
    write_retrieval_slice_markdown(multi_page_dummy_eval_path, "Multi Page Dummy Eval", dummy_rows)
    write_retrieval_slice_markdown(recommendation_eval_path, "Recommendation Eval", recommendation_rows)
    write_retrieval_slice_markdown(compare_eval_path, "Compare Eval", compare_rows)
    write_retrieval_slice_markdown(event_lookup_eval_path, "Event Lookup Eval", event_rows)
    write_retrieval_slice_markdown(exact_anchor_eval_path, "Exact Anchor Eval", exact_anchor_rows)
    write_reranker_ablation(reranker_ablation_path, all_retrieval_rows)
    write_detail_csv(compare_pair_details_path, [row for row in all_retrieval_rows if row.get("question_type") == "compare"])
    write_detail_csv(multi_page_group_details_path, multi_page_rows)
    write_detail_csv(multi_page_group_details_v2_path, dummy_rows)
    write_detail_csv(multi_page_group_details_v4_path, dummy_rows)
    write_retrieval_slice_markdown(multi_page_dummy_eval_v3_path, "Multi Page Dummy Eval V3", dummy_rows)

    all_grounding_rows = answer_details + adversarial_answer_details + multi_page_hard_answer_details
    compare_grounding_rows = [row for row in all_grounding_rows if row.get("question_type") == "compare"]
    write_text(
        compare_grounding_report_path,
        markdown_from_metrics(
            "Compare Grounding Report",
            {
                "compare_grounded_success_rate": round(
                    sum(1 for row in compare_grounding_rows if row.get("grounded_success")) / len(compare_grounding_rows),
                    4,
                )
                if compare_grounding_rows
                else 0.0,
                "compare_pair_success_rate": round(
                    sum(1 for row in compare_grounding_rows if row.get("compare_pair_success")) / len(compare_grounding_rows),
                    4,
                )
                if compare_grounding_rows
                else 0.0,
            },
        ),
    )
    taxonomy_rows = build_error_taxonomy(all_retrieval_rows, all_grounding_rows)
    write_text(error_taxonomy_report_path, error_taxonomy_markdown(taxonomy_rows))
    write_text(error_taxonomy_report_v3_path, error_taxonomy_markdown(taxonomy_rows))
    write_text(error_taxonomy_report_v4_path, error_taxonomy_markdown(taxonomy_rows))
    write_text(
        compare_regression_report_path,
        markdown_from_metrics(
            "Compare Regression Report",
            {
                "compare_top1_hit_rate": round(sum(1 for row in compare_rows if row.get("top1_hit")) / len(compare_rows), 4) if compare_rows else 0.0,
                "compare_grounded_success_rate": round(
                    sum(1 for row in compare_grounding_rows if row.get("grounded_success")) / len(compare_grounding_rows),
                    4,
                )
                if compare_grounding_rows
                else 0.0,
            },
        ),
    )

    write_text(error_analysis_path, "metric,value\n" + "\n".join(f"{key},{value}" for key, value in metrics.items()) + "\n")
    failures = [
        {"type": "GATE_MISS", "metric": key, "value": value}
        for key, value in metrics.items()
        if key in {"recall_at_10", "page_hit_rate", "citation_page_hit_rate", "grounded_success_rate"} and float(value) < 0.8
    ]
    failures.extend(taxonomy_rows)
    failures.extend(graph_failures)
    write_jsonl(failure_cases_path, failures)

    baseline_artifacts: list[Path] = []
    if baseline_label:
        baseline_dir = ctx.root / "docs" / "baselines"
        baseline_json, baseline_md = write_baseline_snapshot(baseline_dir, baseline_label, metrics)
        baseline_artifacts.extend([baseline_json, baseline_md])

    artifacts = [
        summary_path,
        retrieval_report_path,
        citation_report_path,
        grounding_report_path,
        retrieval_details_path,
        retrieval_top1_details_path,
        retrieval_top3_details_path,
        citation_details_path,
        grounding_details_path,
        korean_query_eval_path,
        hard_route_eval_path,
        multi_page_eval_path,
        multi_page_group_details_path,
        multi_page_group_details_v2_path,
        multi_page_group_details_v4_path,
        multi_page_dummy_eval_path,
        multi_page_dummy_eval_v3_path,
        dummy_hardslice_eval_path,
        recommendation_eval_path,
        compare_eval_path,
        compare_pair_details_path,
        compare_grounding_report_path,
        event_lookup_eval_path,
        exact_anchor_eval_path,
        reranker_ablation_path,
        error_taxonomy_report_path,
        error_taxonomy_report_v3_path,
        error_taxonomy_report_v4_path,
        compare_regression_report_path,
        error_analysis_path,
        failure_cases_path,
        *baseline_artifacts,
    ]
    if graph_eval_path:
        artifacts.extend(
            [
                graph_eval_path,
                graph_eval_entity_relation_path,
                graph_eval_topic_cluster_path,
                graph_eval_topic_cluster_v2_path,
                graph_eval_standard_relation_path,
                graph_route_details_path,
                graph_route_details_v2_path,
                graph_route_details_v3_path,
                graph_failure_cases_path,
                graph_failure_cases_v2_path,
                graph_failure_cases_v3_path,
            ]
        )
    return WorkflowResult(
        artifacts=artifacts,
        metrics=metrics,
        output_text=summary_path.read_text(encoding="utf-8"),
    )
