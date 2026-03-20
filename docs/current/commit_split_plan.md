# Commit Split Plan

## Goal

Separate code, docs, and generated experiment artifacts so regression causes remain explainable.

## Recommended Splits

### Commit A: ODL lane code

- `src/parse/opendataloader_parser.py`
- `src/parse/pdf_parser.py`
- `src/workflows/ingest.py`
- `tests/test_aux_parser.py`
- `configs/exp_parser_odl*.yaml`

### Commit B: ODL docs

- `docs/current/parser_odl_adoption_plan.md`
- `docs/current/page_type_aware_parser_dispatch.md`
- `docs/current/aux_parser_experiment.md`
- `docs/current/odl_whitelist_local_vs_hybrid_eval.md`
- `docs/current/odl_grounding_delta.md`
- `docs/current/odl_page_level_comparison.md`
- `docs/current/odl_page_summary_quality_report.md`
- `docs/current/odl_whitelist_keep_or_drop.csv`

### Commit C: Graph lane stabilization

- `src/retrieval/service.py`
- graph-lane specs and work-process docs

### Commit D: Generated data freeze (optional)

Only if the team explicitly wants to preserve:

- `data/parsed/*.jsonl`
- `data/processed/*.jsonl`

Otherwise, do not mix generated data into code-review commits.
