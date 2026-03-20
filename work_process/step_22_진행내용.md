# Step 22. Graph Lane Stabilization Planning

## 목표
GraphRAG의 `entity_relation_lookup`과 `topic_cluster_lookup`을 별개의 안정화 작업으로 관리한다.

## 핵심 판단
1. `entity relation`과 `topic cluster`는 다른 retrieval 문제다.
2. 지금은 G3보다 lane stabilization이 우선이다.
3. parser 실험과 graph lane 안정화는 원인 분리를 위해 분리 운영한다.

## 다음 작업
1. `entity_relation_lookup` exact entity 보정
2. `topic_cluster_lookup` representative ranking 보정
3. lane별 eval 재실행

## 성공 기준
- `entity_relation_lookup top1 >= 0.9`
- `topic_cluster_lookup top1 >= 0.75`
- `graph_backfill_success_rate = 1.0`
- `graph_grounded_success_rate >= 0.85`
