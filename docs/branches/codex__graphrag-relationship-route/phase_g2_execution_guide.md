# Phase G2 Execution Guide

## 목적
`relationship_query`에 한해 graph retrieval과 source evidence backfill을 연결한다.

## 범위
- direct relation lookup only
- graph node match -> entry hit -> chunk backfill
- graph eval / failure report 생성

## 비범위
- graph cluster summary
- global graph summary
- multi-page secondary expansion
- 기본 `prod` query 경로에 graph 자동 연결

## 검증
```powershell
pytest -q
python -m src.main build-indexes --config configs/exp_graph.yaml
python -m src.main eval --config configs/exp_graph.yaml
python -m src.main query "THOR와 관련된 엔트리를 보여줘" --config configs/exp_graph.yaml
```

## 성공 기준
- graph hard set이 별도 리포트로 생성됨
- relationship query가 backfill evidence를 반환함
- mainline regression 없음
