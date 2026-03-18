# Step 21. GraphRAG Phase G2-S Relationship Route Decomposition

## 목표
기존 `relationship_query`를 `entity_relation_lookup`과 `topic_cluster_lookup`으로 분리해, entity relation은 graph-first로 유지하고 topic cluster는 topic-filtered hybrid retrieval + graph validator로 전환한다.

## 선행조건
- `step_20_진행내용.md` 완료
- G1 / G2 direct relation 경로 동작
- `graph_backfill_success_rate = 1.0` 유지

## 핵심 판단
1. entity relation과 topic cluster는 다른 retrieval 문제다.
2. entity relation은 graph-first가 유효하다.
3. topic cluster는 graph-only가 아니라 topic-filtered hybrid retrieval이 더 적합하다.

## 필수 작업
1. route를 `entity_relation_lookup`, `topic_cluster_lookup`으로 분리
2. route policy 분리
3. topic cluster 전용 candidate 생성과 representative ranking 구현
4. entity relation / topic cluster 전용 graph eval 리포트 분리

## 산출물
- `docs/branches/codex__graphrag-g2s-route-decomposition/phase_g2s_execution_guide.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/entity_relation_lookup_spec.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/topic_cluster_lookup_spec.md`
- `outputs/<run_id>/graph_eval_entity_relation.md`
- `outputs/<run_id>/graph_eval_topic_cluster_v2.md`
- `outputs/<run_id>/graph_route_details_v3.csv`

## 완료 기준
- entity relation은 graph-first 경로 유지
- topic cluster는 topic-filtered hybrid 경로로 동작
- mainline regression 없음
- graph backfill success 유지
