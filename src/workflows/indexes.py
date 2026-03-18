from __future__ import annotations

from src.common.pipeline import RunContext
from src.common.runtime import write_json, write_jsonl, write_text
from src.retrieval.build_indexes import build_bm25_store, build_dense_store, persist_lookup_store
from src.retrieval.chunker import build_chunks
from src.retrieval.lookup_stores import build_abbreviation_lookup, build_calendar_lookup, build_index_lookup
from src.retrieval.service import QueryService
from src.workflows.result import WorkflowResult


def run_build_indexes(ctx: RunContext) -> WorkflowResult:
    paths = ctx.paths
    entries = ctx.read_jsonl("entries")
    abbreviations = ctx.read_jsonl("abbreviations")
    back_index = ctx.read_jsonl("back_index")
    calendar_entries = ctx.read_jsonl("calendar_entries")

    chunks = build_chunks(entries, abbreviations, back_index, calendar_entries)
    write_jsonl(ctx.path_from_config("chunks"), chunks)

    entry_chunks = [chunk for chunk in chunks if chunk["chunk_type"] == "entry_overview_chunk"]
    field_chunks = [chunk for chunk in chunks if chunk["chunk_type"] not in {"entry_overview_chunk", "calendar_chunk", "index_lookup_chunk"}]
    primary_chunks = [chunk for chunk in chunks if chunk["is_primary_corpus"]]

    dense_cfg = ctx.config.get("retrieval", "dense_index", default={}) or {}
    build_dense_store(
        entry_chunks,
        paths.dense_entry_index,
        dense_cfg.get("vectorizer_max_features", 5000),
        dense_cfg.get("svd_components", 128),
    )
    build_dense_store(
        field_chunks,
        paths.dense_field_index,
        dense_cfg.get("vectorizer_max_features", 5000),
        dense_cfg.get("svd_components", 128),
    )
    build_bm25_store(primary_chunks, paths.bm25_index)

    persist_lookup_store(build_abbreviation_lookup(abbreviations), paths.abbreviation_lookup_store)
    persist_lookup_store(build_index_lookup(back_index), paths.back_index_lookup_store)
    persist_lookup_store(build_calendar_lookup(calendar_entries), paths.calendar_lookup_store)

    service = QueryService(ctx.root, ctx.config)
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

    return WorkflowResult(
        artifacts=[ctx.path_from_config("chunks"), build_manifest_path, smoke_report_path],
        metrics={"chunk_count": len(chunks)},
        output_text=f"Index build complete. Run: {ctx.run_id}",
    )
