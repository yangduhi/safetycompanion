# Phase G2 Refinement Execution Guide

## 목적
G2 direct relation lookup을 유지한 채 topic cluster ranking과 standard summary ordering을 개선한다.

## 범위
- `topic_cluster_relation` 대표 엔트리 ranking 보정
- `standard_topic_relation` backfill ordering 보정
- graph route 세부 리포트 분리

## 비범위
- G3 multi-page expansion
- graph cluster summary
- prod 기본 경로 승격

## 검증
```powershell
pytest -q
python -m src.main build-indexes --config configs/exp_graph.yaml
python -m src.main eval --config configs/exp_graph.yaml
```

## 성공 기준
- `graph_backfill_success_rate = 1.0` 유지
- `graph_route_top1_hit_rate` 개선
- `topic_cluster_relation` slice 개선
