from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from src.common.config import load_config
from src.common.pipeline import RunContext
from src.common.runtime import ensure_dir, now_utc_iso, read_jsonl, write_json, write_jsonl, write_text
from src.eval.answer_eval import evaluate_answers
from src.eval.error_taxonomy import build_error_taxonomy, error_taxonomy_markdown
from src.eval.extraction_eval import evaluate_extraction
from src.eval.parse_eval import evaluate_parse
from src.eval.retrieval_eval import evaluate_retrieval
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
from src.ingest.abbreviation_extractor import extract_abbreviations
from src.ingest.calendar_extractor import extract_calendar_entries
from src.ingest.entry_extractor import build_extraction_quality_report, extract_entries
from src.ingest.index_extractor import build_page_links, extract_back_index
from src.parse.pdf_parser import build_page_records, build_parse_report, build_source_page_map
from src.qa.answer_generator import build_grounded_answer
from src.retrieval.build_indexes import (
    build_bm25_store,
    build_dense_store,
    persist_lookup_store,
)
from src.retrieval.chunker import build_chunks
from src.retrieval.lookup_stores import build_abbreviation_lookup, build_calendar_lookup, build_index_lookup
from src.retrieval.service import QueryService


ROOT = Path(__file__).resolve().parent.parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def default_config_path() -> Path:
    prod = ROOT / "configs" / "prod.yaml"
    return prod if prod.exists() else ROOT / "configs" / "project.yaml"


def load_runtime_context(config_path: str | None, pdf_override: str | None = None) -> RunContext:
    config = load_config(config_path or default_config_path())
    return RunContext.create(ROOT, config, pdf_override=pdf_override)


def write_manifest_status(ctx: RunContext, manifest: dict, status: str, step_name: str, artifacts: list[Path] | None = None, metrics: dict | None = None) -> None:
    manifest["status"] = status
    manifest["finished_at"] = now_utc_iso()
    manifest.setdefault("steps_completed", []).append(step_name)
    if artifacts:
        manifest.setdefault("artifacts", []).extend(str(path.relative_to(ROOT)) for path in artifacts)
    if metrics:
        manifest.setdefault("metrics", {}).update(metrics)
    ctx.write_run_manifest(manifest)


def cmd_preflight(args: argparse.Namespace) -> int:
    ctx = load_runtime_context(args.config)
    manifest = ctx.init_run_manifest()
    lines = ["# Preflight Report", ""]
    required_commands = ["python", "pdfinfo", "pdftotext"]
    success = True
    for command in required_commands:
        found = shutil.which(command) is not None
        lines.append(f"- {command}: {'ok' if found else 'missing'}")
        success = success and found
    pdf_exists = ctx.pdf_path.exists()
    lines.append(f"- pdf exists: {pdf_exists}")
    success = success and pdf_exists
    report_path = ctx.output_path("preflight_report.md")
    write_text(report_path, "\n".join(lines) + "\n")
    write_manifest_status(ctx, manifest, "success" if success else "failed", "preflight", artifacts=[report_path])
    print(report_path.read_text(encoding="utf-8"))
    return 0 if success else 1


def cmd_ingest(args: argparse.Namespace) -> int:
    ctx = load_runtime_context(args.config, pdf_override=args.pdf)
    manifest = ctx.init_run_manifest()
    parse_tmp = ensure_dir(ROOT / "tmp" / "pdfs")
    page_manifest, page_blocks = build_page_records(ctx.pdf_path, ctx.config.get("document", "id"), parse_tmp)
    source_page_map = build_source_page_map(page_manifest)
    parse_report = build_parse_report(page_manifest)

    entries = extract_entries(page_manifest)
    abbreviations = extract_abbreviations(page_manifest)
    back_index = extract_back_index(page_manifest)
    calendar_entries = extract_calendar_entries(page_manifest)
    page_links = build_page_links(back_index, calendar_entries)
    extraction_report = build_extraction_quality_report(entries)

    write_jsonl(ctx.path_from_config("page_manifest"), page_manifest)
    write_jsonl(ctx.path_from_config("page_blocks"), page_blocks)
    write_jsonl(ctx.path_from_config("source_map"), source_page_map)
    write_jsonl(ctx.path_from_config("entries"), entries)
    write_jsonl(ctx.path_from_config("abbreviations"), abbreviations)
    write_jsonl(ctx.path_from_config("back_index"), back_index)
    write_jsonl(ctx.path_from_config("calendar_entries"), calendar_entries)
    write_jsonl(ctx.path_from_config("page_links"), page_links)

    parse_report_path = ctx.output_path("parse_report.md")
    extraction_report_path = ctx.output_path("extraction_quality_report.md")
    page_review_queue_path = ctx.output_path("page_review_queue.json")
    source_audit_report_path = ctx.output_path("source_audit_report.md")

    low_confidence = [
        {"pdf_page": page["pdf_page"], "page_type": page["page_type"], "title": page["title"]}
        for page in page_manifest
        if page["extraction_quality"] != "high"
    ]
    write_text(parse_report_path, parse_report)
    write_text(extraction_report_path, extraction_report)
    write_json(page_review_queue_path, low_confidence[:50])
    write_text(
        source_audit_report_path,
        "\n".join(
            [
                "# Source Audit Report",
                "",
                f"- total pages: {len(page_manifest)}",
                f"- entries: {len(entries)}",
                f"- abbreviations: {len(abbreviations)}",
                f"- back index rows: {len(back_index)}",
                f"- calendar rows: {len(calendar_entries)}",
            ]
        )
        + "\n",
    )

    metrics = {}
    metrics.update(evaluate_parse(page_manifest))
    metrics.update(evaluate_extraction(entries, abbreviations, calendar_entries))
    write_manifest_status(
        ctx,
        manifest,
        "success",
        "ingest",
        artifacts=[
            ctx.path_from_config("page_manifest"),
            ctx.path_from_config("entries"),
            parse_report_path,
            extraction_report_path,
            page_review_queue_path,
            source_audit_report_path,
        ],
        metrics=metrics,
    )
    print(f"Ingest complete. Run: {ctx.run_id}")
    return 0


def cmd_build_indexes(args: argparse.Namespace) -> int:
    ctx = load_runtime_context(args.config)
    manifest = ctx.init_run_manifest()
    entries = read_jsonl(ctx.path_from_config("entries"))
    abbreviations = read_jsonl(ctx.path_from_config("abbreviations"))
    back_index = read_jsonl(ctx.path_from_config("back_index"))
    calendar_entries = read_jsonl(ctx.path_from_config("calendar_entries"))

    chunks = build_chunks(entries, abbreviations, back_index, calendar_entries)
    write_jsonl(ctx.path_from_config("chunks"), chunks)

    entry_chunks = [chunk for chunk in chunks if chunk["chunk_type"] == "entry_overview_chunk"]
    field_chunks = [chunk for chunk in chunks if chunk["chunk_type"] not in {"entry_overview_chunk", "calendar_chunk", "index_lookup_chunk"}]
    primary_chunks = [chunk for chunk in chunks if chunk["is_primary_corpus"]]

    dense_entry_dir = ensure_dir(ROOT / "indexes" / "dense_entry")
    dense_field_dir = ensure_dir(ROOT / "indexes" / "dense_field")
    bm25_dir = ensure_dir(ROOT / "indexes" / "bm25")
    lookup_dir = ensure_dir(ROOT / "indexes" / "lookup")

    dense_cfg = ctx.config.get("retrieval", "dense_index", default={}) or {}
    build_dense_store(entry_chunks, dense_entry_dir / "index.joblib", dense_cfg.get("vectorizer_max_features", 5000), dense_cfg.get("svd_components", 128))
    build_dense_store(field_chunks, dense_field_dir / "index.joblib", dense_cfg.get("vectorizer_max_features", 5000), dense_cfg.get("svd_components", 128))
    build_bm25_store(primary_chunks, bm25_dir / "index.joblib")

    persist_lookup_store(build_abbreviation_lookup(abbreviations), lookup_dir / "abbreviations.json")
    persist_lookup_store(build_index_lookup(back_index), lookup_dir / "back_index.json")
    persist_lookup_store(build_calendar_lookup(calendar_entries), lookup_dir / "calendar.json")

    service = QueryService(ROOT, ctx.config)
    smoke_questions = [
        "FMVSS 305a 관련 세미나를 찾아줘",
        "Automated Driving 관련 교육은?",
        "2026년 11월 impact biomechanics 세미나는 어디에 있나?",
        "THOR 관련 페이지는?",
        "AEB 는 무엇인가?",
    ]
    smoke_lines = ["# Retrieval Smoke Test", ""]
    for question in smoke_questions:
        result = service.retrieve(question)
        top = result["ranked_hits"][0]["title"] if result["ranked_hits"] else "NO_RESULT"
        smoke_lines.append(f"- {question} -> {top}")
    smoke_report_path = ctx.output_path("retrieval_smoke_test.md")
    write_text(smoke_report_path, "\n".join(smoke_lines) + "\n")

    build_manifest_path = ctx.output_path("index_build_manifest.json")
    build_manifest = {
        "document_hash": ctx.source_hash,
        "entry_count": len(entries),
        "chunk_count": len(chunks),
        "embedding_backend": "tfidf_svd",
        "bm25_backend": "rank_bm25",
    }
    write_json(build_manifest_path, build_manifest)
    write_manifest_status(ctx, manifest, "success", "build-indexes", artifacts=[ctx.path_from_config("chunks"), build_manifest_path, smoke_report_path], metrics={"chunk_count": len(chunks)})
    print(f"Index build complete. Run: {ctx.run_id}")
    return 0


def _query_once(query: str, config_path: str | None) -> tuple[RunContext, dict, dict]:
    ctx = load_runtime_context(config_path)
    manifest = ctx.init_run_manifest()
    service = QueryService(ROOT, ctx.config)
    trace = service.retrieve(query)
    answer = build_grounded_answer(query, trace["route"], trace["ranked_hits"], route_policy=service.route_policy)
    return ctx, manifest, {"trace": trace, "answer": answer}


def cmd_query(args: argparse.Namespace) -> int:
    ctx, manifest, payload = _query_once(args.question, args.config)
    trace = payload["trace"]
    answer = payload["answer"]
    trace_path = ctx.output_path("query_traces") / "last_query.json"
    ensure_dir(trace_path.parent)
    write_json(trace_path, payload)
    answer_path = ctx.output_path("grounded_answer_samples.md")
    write_text(answer_path, answer["answer"] + "\n")
    write_manifest_status(ctx, manifest, "success", "query", artifacts=[trace_path, answer_path])
    print(answer["answer"])
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    ctx = load_runtime_context(args.config)
    manifest = ctx.init_run_manifest()
    page_manifest = read_jsonl(ctx.path_from_config("page_manifest"))
    entries = read_jsonl(ctx.path_from_config("entries"))
    abbreviations = read_jsonl(ctx.path_from_config("abbreviations"))
    calendar_entries = read_jsonl(ctx.path_from_config("calendar_entries"))
    gold_questions = read_jsonl(ctx.path_from_config("gold_questions"))
    adversarial_questions = read_jsonl(ctx.path_from_config("adversarial_questions"))
    multi_page_hard_questions = read_jsonl(ctx.path_from_config("multi_page_hard_questions"))

    service = QueryService(ROOT, ctx.config)

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
    multi_page_dummy_eval_path = ctx.output_path("multi_page_dummy_eval.md")
    recommendation_eval_path = ctx.output_path("recommendation_eval.md")
    compare_eval_path = ctx.output_path("compare_eval.md")
    compare_pair_details_path = ctx.output_path("compare_pair_details.csv")
    compare_grounding_report_path = ctx.output_path("compare_grounding_report.md")
    event_lookup_eval_path = ctx.output_path("event_lookup_eval.md")
    exact_anchor_eval_path = ctx.output_path("exact_anchor_eval.md")
    reranker_ablation_path = ctx.output_path("reranker_ablation.md")
    error_taxonomy_report_path = ctx.output_path("error_taxonomy_report.md")
    error_taxonomy_report_v3_path = ctx.output_path("error_taxonomy_report_v3.md")
    compare_regression_report_path = ctx.output_path("compare_regression_report.md")
    error_analysis_path = ctx.output_path("error_analysis.csv")
    failure_cases_path = ctx.output_path("failure_cases.jsonl")

    retrieval_report_metrics = {key: value for key, value in metrics.items() if key.startswith("retrieval_") or key.startswith("adversarial__retrieval_") or key in {"recall_at_10", "page_hit_rate"}}
    citation_report_metrics = {key: value for key, value in metrics.items() if key.startswith("citation_") or key.startswith("adversarial__citation_")}
    grounding_report_metrics = {key: value for key, value in metrics.items() if key.startswith("grounded_") or key.startswith("field_grounding_") or key.startswith("adversarial__grounded_") or key.startswith("adversarial__field_grounding_")}

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
    dummy_rows = [row for row in all_retrieval_rows if row.get("question_type") == "multi_page_lookup" and any(token in str(row.get("question", "")).lower() for token in ["thor", "dummy", "atd", "landscape"])]
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

    all_grounding_rows = answer_details + adversarial_answer_details + multi_page_hard_answer_details
    compare_grounding_rows = [row for row in all_grounding_rows if row.get("question_type") == "compare"]
    write_text(compare_grounding_report_path, markdown_from_metrics("Compare Grounding Report", {
        "compare_grounded_success_rate": round(sum(1 for row in compare_grounding_rows if row.get("grounded_success")) / len(compare_grounding_rows), 4) if compare_grounding_rows else 0.0,
        "compare_pair_success_rate": round(sum(1 for row in compare_grounding_rows if row.get("compare_pair_success")) / len(compare_grounding_rows), 4) if compare_grounding_rows else 0.0,
    }))
    taxonomy_rows = build_error_taxonomy(all_retrieval_rows, all_grounding_rows)
    write_text(error_taxonomy_report_path, error_taxonomy_markdown(taxonomy_rows))
    write_text(error_taxonomy_report_v3_path, error_taxonomy_markdown(taxonomy_rows))
    write_text(compare_regression_report_path, markdown_from_metrics("Compare Regression Report", {
        "compare_top1_hit_rate": round(sum(1 for row in compare_rows if row.get("top1_hit")) / len(compare_rows), 4) if compare_rows else 0.0,
        "compare_grounded_success_rate": round(sum(1 for row in compare_grounding_rows if row.get("grounded_success")) / len(compare_grounding_rows), 4) if compare_grounding_rows else 0.0,
    }))

    write_text(error_analysis_path, "metric,value\n" + "\n".join(f"{key},{value}" for key, value in metrics.items()) + "\n")
    failures = [
        {"type": "GATE_MISS", "metric": key, "value": value}
        for key, value in metrics.items()
        if key in {"recall_at_10", "page_hit_rate", "citation_page_hit_rate", "grounded_success_rate"} and float(value) < 0.8
    ]
    failures.extend(taxonomy_rows)
    write_jsonl(failure_cases_path, failures)

    baseline_artifacts: list[Path] = []
    if args.baseline_label:
        baseline_dir = ROOT / "docs" / "baselines"
        baseline_json, baseline_md = write_baseline_snapshot(baseline_dir, args.baseline_label, metrics)
        baseline_artifacts.extend([baseline_json, baseline_md])

    write_manifest_status(
        ctx,
        manifest,
        "success",
        "eval",
        artifacts=[
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
            multi_page_dummy_eval_path,
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
            compare_regression_report_path,
            error_analysis_path,
            failure_cases_path,
            *baseline_artifacts,
        ],
        metrics=metrics,
    )
    print(summary_path.read_text(encoding="utf-8"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SafetyCompanion RAG CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--config", default=None)
    preflight.set_defaults(func=cmd_preflight)

    ingest = subparsers.add_parser("ingest")
    ingest.add_argument("--pdf", required=True)
    ingest.add_argument("--config", default=str(default_config_path()))
    ingest.set_defaults(func=cmd_ingest)

    build_indexes = subparsers.add_parser("build-indexes")
    build_indexes.add_argument("--config", default=str(default_config_path()))
    build_indexes.set_defaults(func=cmd_build_indexes)

    query = subparsers.add_parser("query")
    query.add_argument("question")
    query.add_argument("--config", default=str(default_config_path()))
    query.set_defaults(func=cmd_query)

    evaluate = subparsers.add_parser("eval")
    evaluate.add_argument("--config", default=str(default_config_path()))
    evaluate.add_argument("--baseline-label", default=None)
    evaluate.set_defaults(func=cmd_eval)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
