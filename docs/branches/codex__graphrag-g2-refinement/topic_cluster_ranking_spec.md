# Topic Cluster Ranking Spec

## 목적
topic cluster relation에서 “그 주제를 가장 잘 대표하는 엔트리”를 상단에 올리는 규칙을 정의한다.

## 주요 신호
- `BELONGS_TO_TOPIC` 매칭
- query topic phrase와 title / summary overlap
- entry type prior
  - seminar > knowledge > event
- non-topic edge count
  - standard / org / dummy 연결이 많은 entry는 centrality 가산
- field preference
  - `overview`, `page_summary`, `knowledge_topic`

## 감점
- topic phrase가 거의 없는 entry
- event-only 일반 안내 성격 페이지
- summary는 넓지만 대표성이 낮은 page
