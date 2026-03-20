# PR Stack Plan

## PR 1: Graph Lane Stabilization

Goal:

- freeze `graph_baseline_exp_v1`
- include `Euro NCAP` exact-entity typing / tiering
- include `G002` triage alignment
- include CLI query input guardrail

Suggested contents:

- `src/retrieval/query_normalization.py`
- `src/retrieval/router.py`
- `src/retrieval/service.py`
- `src/qa/answer_generator.py`
- `src/workflows/evaluation.py`
- `src/cli/parser.py`
- `src/cli/commands/query.py`
- graph eval data files under `data/eval/`
- graph-specific tests

## PR 2: ODL Whitelist Auxiliary Parser Lane

Goal:

- freeze ODL as `whitelist-only auxiliary parser lane`

Suggested contents:

- `src/parse/opendataloader_parser.py`
- `src/parse/pdf_parser.py`
- `src/workflows/ingest.py`
- ODL configs
- ODL tests

## PR 3: Docs / Operating Rules

Goal:

- make the current baseline, triage rationale, and commit discipline reproducible

Suggested contents:

- baseline docs
- ODL verdict docs
- generated-data handling docs
- work-process docs

## PR 4: Optional Snapshot / Freeze

Only if explicitly desired:

- generated parsed data
- generated processed data
- tags / release notes / archive references
