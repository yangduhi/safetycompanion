# Step 2. 저장소 골격, 데이터 계약, 성공 기준 정의

## 목표
Step 1에서 확정한 문서 특성을 기준으로, 재현 가능한 저장소 구조와 공통 데이터 계약, 평가 기준, 초기 gold question 세트를 만든다.

## 선행조건
- `step_1_진행내용.md` 완료

## 이 단계가 필요한 이유
1. 이 프로젝트는 일반 QA가 아니라 **문서 구조 복원형 RAG**이므로, 초기에 데이터 계약을 고정하지 않으면 단계별 산출물이 서로 맞물리지 않는다.
2. PDF 페이지 번호 체계가 이중이므로, 스키마 수준에서 이를 강제하지 않으면 citation 검증이 깨진다.
3. GraphRAG와 실험 트랙은 나중에 붙일 수 있어도, 저장소 구조와 평가 기준은 처음부터 고정되어야 한다.

## 필수 작업
1. 아래 저장소 구조를 만든다.

```text
project/
├─ data/
│  ├─ raw/
│  ├─ parsed/
│  ├─ processed/
│  ├─ graph/
│  └─ eval/
├─ indexes/
├─ src/
│  ├─ ingest/
│  ├─ parse/
│  ├─ retrieval/
│  ├─ qa/
│  ├─ graph/
│  └─ eval/
├─ configs/
├─ notebooks/
├─ tests/
├─ outputs/
└─ docs/
```

2. `README.md`에 아래를 명시한다.
- 프로젝트 목적
- 문서 특성: catalog/handbook형 혼합 PDF
- 기본 전략: structure-first RAG, hybrid retrieval, optional small GraphRAG
- 답변 원칙: citation 필수, 불확실성 명시, 광고/약관 비우선

3. `docs/data_contract.md`를 작성한다.
- 공통 식별자: `document_id`, `pdf_page`, `printed_page`, `entry_bundle_id`, `entry_id`, `chunk_id`
- 공통 메타데이터: `section_l1`, `page_type`, `source_hash`, `extraction_quality`, `is_primary_corpus`
- citation 표기 규칙: `pdf_page`와 `printed_page`를 함께 보관하고 출력 규칙을 분리

4. `configs/project.yaml`을 작성한다.
- 문서 경로
- 언어
- 페이지 타입 taxonomy
- 포함/제외 정책
- 파서 설정
- retrieval 설정
- 평가셋 경로

5. `docs/acceptance_criteria.md`를 작성한다.
- page manifest coverage: 224/224
- seminar/event title extraction accuracy 목표
- abbreviation exact-match accuracy 목표
- retrieval Recall@10 목표
- citation page hit rate 목표
- compare/recommendation grounded success 기준

6. `data/eval/gold_questions.jsonl` 초안을 만든다.
- 약어형 10
- 페이지/색인 탐색형 10
- 세미나/이벤트 탐색형 10
- 규정/지식 요약형 10
- 비교/추천형 10
- 일정/캘린더형 5
- 관계형 5

7. 실행 추적용 manifest 규칙을 정한다.
- input PDF hash
- config hash
- parse/index/graph 버전
- evaluation summary

## 개선 포인트
1. 기존 초안보다 앞당겨서 `data_contract`를 명시한다.
2. 질문 유형에 `calendar/date lookup`을 정식 추가한다.
3. 문서 특성상 `pdf_page`와 `printed_page`를 분리하지 않으면 안 되므로, 이를 모든 산출물의 필수 필드로 강제한다.

## Codex 작업 지시
- 이후 단계에서 재사용할 경로와 스키마를 이 단계에서 전부 고정하라.
- 빈 파일만 만들지 말고 실제 예시 레코드와 필드 정의를 채워 넣어라.
- `python -m src.main --help` 수준의 최소 엔트리포인트를 염두에 두고 구조를 설계하라.

## 완료 기준
- 저장소 구조가 재현 가능하게 정의됨
- 공통 데이터 계약이 문서화됨
- 평가 기준과 gold question 초안이 준비됨
- 모든 후속 산출물이 참조할 수 있는 config 골격이 확정됨

## 산출물
- `README.md`
- `configs/project.yaml`
- `docs/data_contract.md`
- `docs/acceptance_criteria.md`
- `data/eval/gold_questions.jsonl`
- `docs/run_manifest.schema.json`

## 검증 포인트
- 후속 단계 산출물의 키가 충돌 없이 연결되는가
- `pdf_page`와 `printed_page`를 모두 잃지 않도록 계약이 정의되었는가
- gold question 분포가 실제 PDF의 질의 패턴을 반영하는가
