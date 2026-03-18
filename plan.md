# Execution Plan

## 규칙
- 모든 단계는 순차 실행한다.
- 각 단계는 이전 단계의 gate를 통과해야만 시작할 수 있다.
- 실패 시 다음 단계로 넘어가지 않고, 아래의 되돌아갈 단계로 복귀한다.

## Current Improvement Cycle
현재 개선 사이클의 우선순위는 아래 문서를 따른다.
- [improvement_plan_v2.md](/D:/vscode/safetycompanion/docs/improvement_plan_v2.md)

즉시 수행 대상:
1. Baseline Freeze + Evaluator Decouple
2. Citation / Grounding 집중 개선
3. Retrieval top-1 / top-3 정밀화

## Phase 0. Preflight
목적:
- 입력 파일, 필수 도구, 권한, 기본 런타임을 확인한다.

입력:
- `data/SafetyCompanion-2026.pdf`
- `spec.md`

필수 검증:
```powershell
python --version
pdfinfo data/SafetyCompanion-2026.pdf
pdftotext -f 1 -l 1 data/SafetyCompanion-2026.pdf -
```

산출물:
- `outputs/<run_id>/preflight_report.md`

되돌아갈 단계:
- 없음

## Phase 1. 원본 감사
상세 문서:
- [step_1_진행내용.md](/D:/vscode/safetycompanion/work_process/step_1_진행내용.md)

다음 단계 진입 조건:
- source audit 산출물 완료
- `pdf_page`/`printed_page` 정책 확정

실패 시:
- Phase 1 재실행

## Phase 2. 저장소 계약 고정
상세 문서:
- [step_2_진행내용.md](/D:/vscode/safetycompanion/work_process/step_2_진행내용.md)

다음 단계 진입 조건:
- `README.md`, `spec.md`, `plan.md`, `tasks.md` 존재
- `configs/project.yaml` 경로/스키마 정의 완료

실패 시:
- Phase 2 재실행

## Phase 3. PDF 구조 복원
상세 문서:
- [step_3_진행내용.md](/D:/vscode/safetycompanion/work_process/step_3_진행내용.md)

다음 단계 진입 조건:
- page manifest coverage == 224
- 저신뢰 페이지 queue 생성 완료

실패 시 되돌아갈 단계:
- Phase 1 또는 Phase 2

## Phase 4. 엔트리/보조 데이터셋 추출
상세 문서:
- [step_4_진행내용.md](/D:/vscode/safetycompanion/work_process/step_4_진행내용.md)

다음 단계 진입 조건:
- `entries.jsonl`, `abbreviations.jsonl`, `back_index.jsonl`, `calendar_entries.jsonl` 생성
- 참조 링크 검증 완료

실패 시 되돌아갈 단계:
- Phase 3

## Phase 5. 청킹/인덱스 구축
상세 문서:
- [step_5_진행내용.md](/D:/vscode/safetycompanion/work_process/step_5_진행내용.md)

다음 단계 진입 조건:
- dense, BM25, lookup store 생성
- smoke test 빈 응답률 <= 10%

실패 시 되돌아갈 단계:
- Phase 4

## Phase 6. QA 계층 구축
상세 문서:
- [step_6_진행내용.md](/D:/vscode/safetycompanion/work_process/step_6_진행내용.md)

다음 단계 진입 조건:
- route trace 저장 가능
- citation 없는 응답 테스트 실패 처리 구현

실패 시 되돌아갈 단계:
- Phase 5

## Phase 7. 평가 및 gate 판정
상세 문서:
- [step_7_진행내용.md](/D:/vscode/safetycompanion/work_process/step_7_진행내용.md)

필수 gate:
- seminar/event title extraction accuracy >= 0.98
- abbreviation exact-match accuracy >= 0.95
- retrieval Recall@10 >= 0.85
- citation page hit rate >= 0.95
- compare/recommendation grounded success rate >= 0.80

실패 시 되돌아갈 단계:
- 실패 유형에 따라 Phase 3, 4, 5, 6 중 해당 단계

## Phase 8. 운영형 CLI 및 재현 실행 경로
상세 문서:
- [step_8_진행내용.md](/D:/vscode/safetycompanion/work_process/step_8_진행내용.md)

다음 단계 진입 조건:
- CLI preflight/ingest/build-indexes/query/eval 경로 동작
- run manifest 생성

실패 시 되돌아갈 단계:
- Phase 5, 6, 7 중 해당 단계

## Phase 9. 선택형 GraphRAG
상세 문서:
- [step_9_진행내용.md](/D:/vscode/safetycompanion/work_process/step_9_진행내용.md)

시작 조건:
- Phase 7 gate 통과
- Phase 8 완료
- 사용자 또는 설정에서 graph track 허용

실패 시 되돌아갈 단계:
- Phase 9만 롤백
- baseline 경로는 유지
