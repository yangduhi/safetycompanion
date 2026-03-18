# Phase G2-S Execution Guide

## 목적
relationship 경로를 구조적으로 두 갈래로 분리한다.

## 분리 대상
- `entity_relation_lookup`
- `topic_cluster_lookup`

## 원칙
- entity relation:
  graph-first, backfill-second
- topic cluster:
  topic-filtered hybrid retrieval + graph validator

## 검증
```powershell
pytest -q
python -m src.main build-indexes --config configs/exp_graph.yaml
python -m src.main eval --config configs/exp_graph.yaml
```

## 성공 기준
- entity relation regression 없음
- topic cluster top1 개선
- graph_backfill_success_rate = 1.0 유지
