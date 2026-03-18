# Ops Playbook

## 1. 표준 실행

```powershell
python -m src.main preflight
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml
python -m src.main build-indexes --config configs/prod.yaml
python -m src.main query "FMVSS 305a 관련 세미나를 찾아줘" --config configs/prod.yaml
python -m src.main eval --config configs/prod.yaml
```

## 2. 운영 프로필

- 기본 운영: `configs/prod.yaml`
- graph 실험: `configs/exp_graph.yaml`
- 경로/파라미터 원본: `configs/project.yaml`

## 3. 변경 후 재실행 규칙

- parse / ingest 변경:
  `preflight -> ingest -> build-indexes -> eval`
- retrieval / chunking / index 변경:
  `build-indexes -> query -> eval`
- answer formatting 또는 route policy 변경:
  `query -> eval`
- eval / reporting 변경:
  `eval`

## 4. 점검 우선순위

문제가 생기면 아래 순서로 본다.

1. `outputs/<run_id>/run_manifest.json`
2. `outputs/<run_id>/preflight_report.md`
3. `outputs/<run_id>/parse_report.md`
4. `outputs/<run_id>/retrieval_smoke_test.md`
5. `outputs/<run_id>/query_traces/last_query.json`
6. `outputs/<run_id>/eval_summary.md`
7. `outputs/<run_id>/failure_cases.jsonl`

## 5. 장애 유형별 대응

### 환경 장애

증상:
- `preflight` 실패
- `pdfinfo` 또는 `pdftotext` 미탐지

대응:
- 로컬 PATH와 설치 상태 확인
- PDF 파일 경로 확인
- 환경 문제 해결 전 다음 단계 진행 금지

### 파싱 / 추출 장애

증상:
- `page_manifest` 개수 이상
- `entries` 또는 `calendar_entries` 급감
- `page_review_queue.json`에 저신뢰 페이지가 급증

대응:
- `parse_report.md`와 `source_audit_report.md` 확인
- 최근 파싱 규칙 변경 여부 확인
- 필요 시 `ingest`부터 재실행

### Retrieval 장애

증상:
- smoke test 상위 결과 부정확
- `query` 결과가 비어 있거나 route가 이상함

대응:
- `query_traces/last_query.json` 확인
- route policy와 query normalization 로직 확인
- 필요 시 `build-indexes`부터 재실행

### Grounding / Answer 장애

증상:
- citation 누락
- compare / recommendation에서 과도하게 단정적 응답

대응:
- `src/qa/answer_generator.py`와 route policy 확인
- 대표 질의 `query` 재실행
- `eval`로 grounding 회귀 여부 확인

## 6. 운영 원칙

- 실패 실행 산출물도 남겨서 원인 분석 가능성을 유지한다.
- 성공 실행을 수동으로 덮어쓰지 않는다.
- `pdf_page`와 `printed_page`는 항상 분리 검토한다.
- graph 경로는 기본 운영 문제를 가릴 만큼 우선순위를 높이지 않는다.
