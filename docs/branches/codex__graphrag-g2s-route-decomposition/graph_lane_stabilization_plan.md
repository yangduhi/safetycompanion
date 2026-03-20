# Graph Lane Stabilization Plan

## 목적

GraphRAG 실험 경로를 더 키우기 전에, 현재 분리된 두 lane을 각각 안정화한다.

- `entity_relation_lookup`
- `topic_cluster_lookup`

## 현재 상태

- `entity_relation_lookup`
  - exact entity 문제에 맞는 graph-first 경로
  - 남은 과제: `Euro NCAP` generic relation 분리
- `topic_cluster_lookup`
  - topic-filtered hybrid retrieval + graph validator
  - 남은 과제:
    - `Passive Safety` representative ranking
    - `Automated Driving` representative ranking

## 다음 순서

### 1. entity lane 안정화

- exact entity vs broad overview 분리
- title exact hit / `knowledge_topic` / `page_summary` 우선 강화
- NCAP generic overview penalty 보정

### 2. topic lane 안정화

- 대표성 점수에서 `overview`, `briefing`, `update`, `introduction` 가산
- 지나치게 세부적인 protocol/matrix/rating page 감점
- seminar/event/knowledge representative prior 재조정

### 3. lane별 eval

- `graph_eval_entity_relation.md`
- `graph_eval_topic_cluster_v2.md`
- `graph_route_details_v3.csv`

## 중단 기준

아래 기준을 못 넘기면 G3로 가지 않는다.

- `entity_relation_lookup top1 >= 0.9`
- `topic_cluster_lookup top1 >= 0.75`
- `graph_backfill_success_rate = 1.0`
- `graph_grounded_success_rate >= 0.85`
