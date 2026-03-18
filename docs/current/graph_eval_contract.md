# Graph Eval Contract

## 목적
GraphRAG 실험 결과를 기본 eval과 섞지 않고 별도 산출물로 추적하기 위한 계약 문서다.

## 입력

- `data/eval/graph_hard_questions.jsonl`
- graph route 또는 graph augmentation trace

## 필수 산출물

- `outputs/<run_id>/graph_eval.md`
- `outputs/<run_id>/graph_route_details.csv`
- `outputs/<run_id>/graph_failure_cases.jsonl`

## 필수 질문 필드

- `qid`
- `query`
- `difficulty`
- `query_type`
- `graph_route_type`
- `expected_entities`
- `expected_pages`
- `expected_titles`
- `expected_relation_types`
- `requires_graph`
- `requires_backfill`
- `requires_multi_hop`

## graph_route_details.csv 필드

- `qid`
- `query`
- `query_type`
- `graph_route_type`
- `top1_hit`
- `top3_hit`
- `graph_nodes_hit`
- `graph_edges_hit`
- `backfill_success`
- `grounded_success`
- `top_result_title`
- `top_result_page`
- `graph_failure_type`

## 필수 지표

- `graph_route_top1_hit_rate`
- `graph_route_top3_hit_rate`
- `graph_backfill_success_rate`
- `graph_grounded_success_rate`
- `graph_regression_on_mainline`

## 해석 원칙

- graph는 후보 제안과 relation tracing을 담당한다.
- 최종 정답 인정은 반드시 원문 evidence backfill을 전제로 한다.
- graph hit만 있고 backfill이 실패하면 성공으로 간주하지 않는다.
