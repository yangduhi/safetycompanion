# Phase G1 Execution Guide

## 목적
GraphRAG의 최소 graph index를 구현하고 `exp_graph.yaml`에서만 artifact를 생성한다.

## 구현 범위
- node:
  - `Entry`
  - `Topic`
  - `DummyFamily`
  - `Standard`
  - `Organization`
- edge:
  - `BELONGS_TO_TOPIC`
  - `MENTIONS_DUMMY`
  - `MENTIONS_STANDARD`
  - `MENTIONS_ORG`
  - `RELATED_TO_ENTRY`

## 구현 원칙
- graph는 기본 경로에 자동 연결하지 않는다.
- graph artifact는 `data/graph/*`와 `outputs/<run_id>/graph_schema.md`로 분리 저장한다.
- 모든 edge는 provenance 필드를 가진다.

## 검증
```powershell
pytest -q
python -m src.main build-indexes --config configs/exp_graph.yaml
```

## 다음 단계
- `codex/graphrag-relationship-route`
- `relationship_query` 한정 graph retrieval + backfill
