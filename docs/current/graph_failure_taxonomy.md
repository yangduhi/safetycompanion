# Graph Failure Taxonomy

## 목적
Graph 실험 실패를 기본 retrieval 실패와 분리해 기록하기 위한 taxonomy다.

## 상위 분류

- `GRAPH_ENTITY_MISS`
- `GRAPH_FALSE_RELATION`
- `GRAPH_ROUTE_MISS`
- `GRAPH_BACKFILL_FAIL`
- `GRAPH_SUMMARY_UNGROUNDED`

## 세부 해석

### GRAPH_ENTITY_MISS
- 기대한 entity node가 graph에서 회수되지 않음

### GRAPH_FALSE_RELATION
- 관련 없어야 할 node/edge가 상위 결과에 들어옴

### GRAPH_ROUTE_MISS
- graph를 써야 하는 질문이 다른 route로 처리되거나, 반대로 graph가 불필요한 질문에 사용됨

### GRAPH_BACKFILL_FAIL
- graph는 관련 candidate를 찾았지만 source entry/page evidence로 backfill하지 못함

### GRAPH_SUMMARY_UNGROUNDED
- graph summary 또는 cluster explanation이 원문 근거 없이 생성됨

## 기록 필드

- `qid`
- `query`
- `graph_failure_type`
- `graph_node_id`
- `graph_edge_id`
- `source_entry_id`
- `source_page`
- `notes`
