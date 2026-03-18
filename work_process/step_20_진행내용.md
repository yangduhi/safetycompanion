# Step 20. GraphRAG Phase G2 Refinement

## 목표
Graph `relationship_query`의 direct relation lookup을 stable experimental 수준으로 끌어올리기 위해 topic cluster ranking과 standard relation summary ordering을 보정한다.

## 선행조건
- `step_19_진행내용.md` 완료
- `graph_backfill_success_rate`가 1.0일 것
- mainline regression 없음

## 핵심 판단
1. 지금은 G3보다 G2 refinement가 우선이다.
2. 병목은 graph schema 자체보다 topic cluster representative ranking과 standard summary ordering이다.
3. graph route는 계속 `relationship_query` direct relation lookup에만 한정한다.

## 필수 작업
1. query profile에 graph relation class를 명시한다.
2. topic cluster relation 전용 ranking 보정을 추가한다.
3. standard relation backfill ordering을 query-aware로 보정한다.
4. graph eval을 `topic_cluster_relation`, `standard_topic_relation` slice로 분리한다.

## 산출물
- `docs/branches/codex__graphrag-g2-refinement/phase_g2_refinement_execution_guide.md`
- `docs/branches/codex__graphrag-g2-refinement/topic_cluster_ranking_spec.md`
- `docs/branches/codex__graphrag-g2-refinement/standard_relation_summary_spec.md`
- `outputs/<run_id>/graph_eval_topic_cluster.md`
- `outputs/<run_id>/graph_eval_standard_relation.md`
- `outputs/<run_id>/graph_route_details_v2.csv`
- `outputs/<run_id>/graph_failure_cases_v2.jsonl`

## 완료 기준
- `graph_backfill_success_rate = 1.0` 유지
- direct relation lookup regression 없음
- `topic_cluster_relation` top1 개선
- `standard relation` summary ordering 개선
