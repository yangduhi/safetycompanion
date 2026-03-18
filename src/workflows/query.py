from __future__ import annotations

from src.common.pipeline import RunContext
from src.common.runtime import ensure_dir, write_json, write_text
from src.qa.answer_generator import build_grounded_answer
from src.retrieval.service import QueryService
from src.workflows.result import WorkflowResult


def run_query(ctx: RunContext, question: str) -> WorkflowResult:
    service = QueryService(ctx.root, ctx.config)
    trace = service.retrieve(question)
    answer = build_grounded_answer(question, trace["route"], trace["ranked_hits"], route_policy=service.route_policy)

    payload = {"trace": trace, "answer": answer}
    trace_path = ctx.output_path("query_traces") / "last_query.json"
    ensure_dir(trace_path.parent)
    write_json(trace_path, payload)

    answer_path = ctx.output_path("grounded_answer_samples.md")
    write_text(answer_path, answer["answer"] + "\n")
    return WorkflowResult(
        artifacts=[trace_path, answer_path],
        output_text=answer["answer"],
    )
