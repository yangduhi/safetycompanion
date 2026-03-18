# Topic Cluster Lookup Spec

## 대상
- `Passive Safety topic`
- `Automated Driving topic`

## 경로
1. base retrieval에서 topic-filtered candidate 생성
2. `section/title/entry_type` 중심 representative ranking
3. graph는 cluster membership validator와 secondary signal로만 사용
4. 원문 evidence backfill
5. summary 생성

## 목적
graph-only topic traversal 대신, 대표성 있는 엔트리를 더 안정적으로 고른다.
