# CLI Reference

## 공통 규칙

- 기본 진입점은 `python -m src.main`
- 운영 기본 config는 `configs/prod.yaml`
- graph 실험 config는 `configs/exp_graph.yaml`
- 모든 실행은 `outputs/<run_id>/...` 아래에 실행별 산출물을 남긴다
- 안정 데이터와 인덱스는 `data/*`, `indexes/*`에 갱신된다

## `preflight`

용도:
- 입력 PDF와 필수 도구 존재 여부 확인

명령:

```powershell
python -m src.main preflight
python -m src.main preflight --config configs/prod.yaml
```

주요 산출물:
- `outputs/<run_id>/preflight_report.md`
- `outputs/<run_id>/run_manifest.json`

## `ingest`

용도:
- 페이지 파싱, 엔트리 추출, 약어/색인/캘린더 생성

명령:

```powershell
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml
```

주요 산출물:
- `data/parsed/page_manifest.jsonl`
- `data/parsed/page_blocks.jsonl`
- `data/raw/source_page_map.jsonl`
- `data/processed/entries.jsonl`
- `data/processed/abbreviations.jsonl`
- `data/processed/back_index.jsonl`
- `data/processed/calendar_entries.jsonl`
- `data/processed/page_links.jsonl`
- `outputs/<run_id>/parse_report.md`
- `outputs/<run_id>/extraction_quality_report.md`
- `outputs/<run_id>/page_review_queue.json`
- `outputs/<run_id>/source_audit_report.md`

## `build-indexes`

용도:
- 청크 생성과 retrieval index 구축

명령:

```powershell
python -m src.main build-indexes --config configs/prod.yaml
python -m src.main build-indexes --config configs/exp_graph.yaml
```

주요 산출물:
- `data/processed/chunks.jsonl`
- `indexes/dense_entry/index.joblib`
- `indexes/dense_field/index.joblib`
- `indexes/bm25/index.joblib`
- `indexes/lookup/abbreviations.json`
- `indexes/lookup/back_index.json`
- `indexes/lookup/calendar.json`
- `outputs/<run_id>/index_build_manifest.json`
- `outputs/<run_id>/retrieval_smoke_test.md`

graph 실험 config 사용 시 추가 산출물:
- `data/graph/nodes.jsonl`
- `data/graph/edges.jsonl`
- `outputs/<run_id>/graph_schema.md`

## `query`

용도:
- route 결정, 검색, grounded answer 생성

명령:

```powershell
python -m src.main query "FMVSS 305a 관련 세미나를 찾아줘" --config configs/prod.yaml
python -m src.main query "AEB 는 무엇인가?" --config configs/prod.yaml
```

주요 산출물:
- `outputs/<run_id>/query_traces/last_query.json`
- `outputs/<run_id>/grounded_answer_samples.md`

출력 특징:
- 답변 문자열
- route 정보
- selected evidence
- citation 표기

## `eval`

용도:
- parse / extraction / retrieval / grounding 품질 평가

명령:

```powershell
python -m src.main eval --config configs/prod.yaml
python -m src.main eval --config configs/prod.yaml --baseline-label baseline_v6
python -m src.main eval --config configs/exp_graph.yaml
```

주요 산출물:
- `outputs/<run_id>/eval_summary.md`
- `outputs/<run_id>/retrieval_report.md`
- `outputs/<run_id>/citation_report.md`
- `outputs/<run_id>/grounding_report.md`
- `outputs/<run_id>/retrieval_details.csv`
- `outputs/<run_id>/citation_details.csv`
- `outputs/<run_id>/grounding_details.csv`
- `outputs/<run_id>/failure_cases.jsonl`
- 선택 시 `docs/baselines/<label>.json`, `docs/baselines/<label>.md`

graph 실험 config 사용 시 추가 산출물:
- `outputs/<run_id>/graph_eval.md`
- `outputs/<run_id>/graph_route_details.csv`
- `outputs/<run_id>/graph_failure_cases.jsonl`

## 테스트

```powershell
pytest -q
```

현재 테스트는 최소 아래 영역을 확인한다.

- query routing
- grounded answer formatting
- 공통 경로 계약
