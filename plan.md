# Current Plan

이 문서는 초기 부트스트랩 계획서가 아니라, 현재 구현된 SafetyCompanion RAG 시스템을 어떤 순서로 운영하고 개선할지 정리한 실행 계획이다.

## 운영 기본 흐름

모든 표준 실행은 아래 순서를 따른다.

1. `preflight`
2. `ingest`
3. `build-indexes`
4. `query`
5. `eval`

이 순서는 [src/workflows](/D:/vscode/safetycompanion/src/workflows)의 구조와 동일하다. 한 단계의 입력 계약이 바뀌면 다음 단계들도 다시 검증해야 한다.

## 단계별 목적

### 1. Preflight

목적:
- 입력 PDF와 필수 도구 존재 여부 확인
- 실행 전 즉시 실패해야 할 환경 문제 차단

주요 산출물:
- `outputs/<run_id>/preflight_report.md`

### 2. Ingest

목적:
- PDF 페이지를 구조화하고 `page_manifest`, `entries`, `abbreviations`, `back_index`, `calendar_entries`, `page_links` 생성

주요 산출물:
- `data/parsed/page_manifest.jsonl`
- `data/parsed/page_blocks.jsonl`
- `data/processed/entries.jsonl`
- `data/processed/abbreviations.jsonl`
- `data/processed/back_index.jsonl`
- `data/processed/calendar_entries.jsonl`
- `data/processed/page_links.jsonl`
- `outputs/<run_id>/parse_report.md`
- `outputs/<run_id>/extraction_quality_report.md`

### 3. Build Indexes

목적:
- retrieval용 `chunks` 생성
- dense index, BM25 index, lookup store 생성

주요 산출물:
- `data/processed/chunks.jsonl`
- `indexes/dense_entry/index.joblib`
- `indexes/dense_field/index.joblib`
- `indexes/bm25/index.joblib`
- `indexes/lookup/*.json`
- `outputs/<run_id>/retrieval_smoke_test.md`

### 4. Query

목적:
- route 결정, 검색, rerank, grounded answer 생성
- 추적 가능한 query trace 저장

주요 산출물:
- `outputs/<run_id>/query_traces/last_query.json`
- `outputs/<run_id>/grounded_answer_samples.md`

### 5. Eval

목적:
- parse, extraction, retrieval, grounding 품질 평가
- 슬라이스 리포트와 failure case 생성

주요 산출물:
- `outputs/<run_id>/eval_summary.md`
- `outputs/<run_id>/retrieval_report.md`
- `outputs/<run_id>/citation_report.md`
- `outputs/<run_id>/grounding_report.md`
- `outputs/<run_id>/failure_cases.jsonl`

## 현재 우선순위

현재 개선 우선순위는 “새로운 기능 추가”보다 “기존 baseline의 안정화”에 둔다.

1. 문서와 코드 구조 동기화 유지
2. PDF 인코딩 노이즈가 심한 페이지의 파싱/추출 품질 개선
3. hard case와 multi-page case의 retrieval top-1 안정성 유지
4. citation/grounding 회귀 방지를 위한 평가 리포트 활용 강화
5. graph track는 기본 경로를 흔들지 않는 선에서만 제한적으로 유지

## 변경 영향 규칙

아래 규칙은 무엇을 다시 실행해야 하는지 빠르게 판단하기 위한 운영 기준이다.

- `src/parse`, `src/ingest` 변경:
  `ingest -> build-indexes -> query -> eval` 재실행
- `src/retrieval/chunker.py`, `src/retrieval/build_indexes.py`, `src/retrieval/lookup_stores.py` 변경:
  `build-indexes -> query -> eval` 재실행
- `src/retrieval/router.py`, [configs/route_field_priority.yaml](/D:/vscode/safetycompanion/configs/route_field_priority.yaml), `src/retrieval/service.py` 변경:
  `build-indexes`가 필요할 수 있으며 최소 `query -> eval` 재실행
- `src/qa/answer_generator.py` 변경:
  `query -> eval` 재실행
- `src/eval/*` 변경:
  `eval` 재실행
- `configs/project.yaml` 경로 변경:
  영향받는 단계 전체 재점검

## Go / No-Go 기준

아래 조건이 깨지면 다음 기능 확장을 보류한다.

- 표준 CLI 명령이 동작하지 않음
- grounded answer에 citation 누락
- `pdf_page` / `printed_page` 혼동 발생
- evaluation 산출물 생성 실패
- baseline 핵심 지표가 [docs/current/acceptance_criteria.md](/D:/vscode/safetycompanion/docs/current/acceptance_criteria.md)의 최소 기준 미만

## 조건부 트랙

Graph 경로는 [configs/exp_graph.yaml](/D:/vscode/safetycompanion/configs/exp_graph.yaml) 기반의 선택 실험 트랙이다. 기본 운영 계획에는 포함하지 않으며, 아래 조건이 충족될 때만 별도 진행한다.

- 기본 CLI 경로가 안정적일 것
- baseline 회귀가 없을 것
- graph 결과를 비교 평가할 준비가 되었을 것

세부 도입 순서와 게이트는 [docs/current/graph_rag_adoption_plan.md](/D:/vscode/safetycompanion/docs/current/graph_rag_adoption_plan.md)를 따른다.
