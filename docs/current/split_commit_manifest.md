# Split Commit Manifest

## Purpose

This manifest maps the current dirty worktree into `code`, `docs`, and `generated` layers so commits and PRs can be split without mixing causes.

## Commit 1: Graph Lane Code

- `src/retrieval/query_normalization.py`
- `src/retrieval/router.py`
- `src/retrieval/service.py`
- `src/qa/answer_generator.py`
- `src/workflows/evaluation.py`
- `src/cli/parser.py`
- `src/cli/commands/query.py`
- `tests/test_cli_query_command.py`
- `tests/test_euro_ncap_query_profile.py`
- `data/eval/graph_hard_questions.jsonl`
- `data/eval/euro_ncap_micro_suite.jsonl`
- optional interpretation-only set:
  - `data/eval/graph_hard_questions_strict_knowledge_only.jsonl`

## Commit 2: ODL Auxiliary Parser Code

- `src/parse/opendataloader_parser.py`
- `src/parse/pdf_parser.py`
- `src/workflows/ingest.py`
- `configs/exp_parser_odl.yaml`
- `configs/exp_parser_odl_local.yaml`
- `configs/exp_parser_odl_hybrid.yaml`
- `configs/exp_parser_odl_whitelist.yaml`
- `configs/exp_parser_odl_whitelist_hybrid.yaml`
- `configs/project.yaml`
- `tests/test_aux_parser.py`

## Commit 3: Docs and Operating Rules

- `docs/current/README.md`
- `docs/current/data_contract.md`
- `docs/current/parser_odl_adoption_plan.md`
- `docs/current/page_type_aware_parser_dispatch.md`
- `docs/current/aux_parser_experiment.md`
- `docs/current/odl_whitelist_local_vs_hybrid_eval.md`
- `docs/current/odl_grounding_delta.md`
- `docs/current/odl_page_level_comparison.md`
- `docs/current/odl_page_level_verdict_v2.csv`
- `docs/current/odl_page_summary_quality_report.md`
- `docs/current/odl_whitelist_keep_or_drop.csv`
- `docs/current/odl_whitelist_page_report.csv`
- `docs/current/query_input_encoding.md`
- `docs/current/generated_data_handling.md`
- `docs/current/generated_data_commit_strategy.md`
- `docs/current/commit_split_plan.md`
- `docs/current/split_commit_manifest.md`
- `docs/current/graph_baseline_exp_v1.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/entity_relation_euro_ncap_spec.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/euro_ncap_entity_typing_spec_v2.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/euro_ncap_tiering_policy.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/euro_ncap_confusion_cases.jsonl`
- `docs/branches/codex__graphrag-g2s-route-decomposition/euro_ncap_route_trace.csv`
- `docs/branches/codex__graphrag-g2s-route-decomposition/g002_case_report.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/g002_route_trace.csv`
- `docs/branches/codex__graphrag-g2s-route-decomposition/g002_candidate_diff.jsonl`
- `docs/branches/codex__graphrag-g2s-route-decomposition/graph_eval_entity_relation_v4.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/graph_eval_topic_cluster_v3.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/graph_interactive_batch_diff_report.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/graph_lane_stabilization_plan.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/graph_route_trace_diff.csv`
- `docs/branches/codex__graphrag-g2s-route-decomposition/passive_safety_representative_spec.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/topic_cluster_confusion_cases.jsonl`
- `docs/branches/codex__graphrag-g2s-route-decomposition/topic_cluster_representative_spec.md`
- `work_process/step_22_진행내용.md`
- `work_process/step_23_진행내용.md`
- `work_process/step_24_진행내용.md`
- `work_process/step_25_진행내용.md`
- `work_process/step_26_진행내용.md`
- `work_process/step_27_진행내용.md`

## Keep Out of Code/Docs PRs

Tracked generated data:

- `data/parsed/page_manifest.jsonl`
- `data/parsed/page_blocks.jsonl`

Untracked runtime/generated artifacts:

- `data/graph/nodes.jsonl`
- `data/graph/edges.jsonl`
- `outputs/<run_id>/*`

## Suggested PR Stack

1. Graph lane stabilization
2. ODL whitelist auxiliary parser lane
3. Docs / operating rules
4. Optional generated-data freeze or tag-only snapshot
