# Step 6. 질의 라우터, 재순위화, grounded answer 계층 구축

## 목표
질문 유형에 따라 최적의 검색 경로를 선택하고, 근거 페이지를 보존한 상태에서 답변을 생성하는 QA 계층을 구축한다.

## 선행조건
- `step_5_진행내용.md` 완료

## 핵심 판단
1. 이 문서의 질문 유형은 균일하지 않다. 약어 질문, 페이지 찾기, 세미나 요약, 일정 확인, 비교/추천, 관계형 질문은 서로 다른 검색 경로가 필요하다.
2. 최종 답변은 반드시 원문 근거와 연결되어야 하며, lookup store만으로 끝내지 말고 본문 엔트리로 다시 backfill해야 한다.

## 필수 작업
1. 질의 intent router를 구현한다.
- `abbreviation_lookup`
- `page_or_index_lookup`
- `seminar_lookup`
- `event_lookup`
- `calendar_lookup`
- `regulation_knowledge`
- `compare_or_recommend`
- `relationship_query`
- `fallback_general`

2. 질의 전처리를 구현한다.
- 약어 확장
- 규정명/기관명 alias normalization
- 페이지 번호 질의 해석
- 달력형 날짜 질의 해석

3. 후보 수집기를 구현한다.
- dense entry top-k
- dense field top-k
- BM25 top-k
- abbreviation hits
- back index hits
- calendar hits

4. 후보 병합과 reranker를 구현한다.
- RRF 또는 calibrated fusion
- entry/page 중복 정리
- instruction-aware reranker 적용

5. grounded answer composer를 구현한다.
- 답변 본문
- 핵심 근거 bullet
- `title`
- `pdf_page`
- `printed_page`
- 필요 시 `section_l1`
- 불확실 시 `문서상 확인 불가` 또는 `추가 확인 필요` 표기

6. calendar와 index lookup의 backfill 규칙을 구현한다.
- 일정 질문은 calendar hit 후 seminar/event entry로 다시 이동
- index hit는 해당 페이지의 knowledge 또는 seminar 엔트리로 다시 이동

## 답변 가드레일
1. citation 없는 답변 금지
2. 근거 없는 규정형 단정 금지
3. 광고성 페이지 인용 금지
4. 약관/디렉터리 정보는 사용자가 명시적으로 요청한 경우에만 활용

## Codex 작업 지시
- `src/retrieval/router.py`, `src/retrieval/fusion.py`, `src/retrieval/reranker.py`, `src/qa/answer_generator.py`를 구현하라.
- 질의별 route trace를 `outputs/<run_id>/query_traces/`에 저장하라.
- citation이 없는 응답은 테스트에서 실패 처리하라.
- 캘린더/색인 질의가 본문 엔트리 backfill 없이 끝나지 않도록 강제하라.

## 완료 기준
- 주요 질문 유형별 라우팅이 동작함
- 후보 병합과 재순위화가 동작함
- 답변이 항상 근거 페이지와 제목을 포함함
- 캘린더/색인 기반 질의도 본문 엔트리로 연결됨

## 산출물
- `outputs/<run_id>/query_traces/*.json`
- `outputs/<run_id>/grounded_answer_samples.md`
- `tests/test_grounding.py`
- `tests/test_query_routing.py`

## 검증 포인트
- 약어형 질문이 정확히 약어 store를 우선 타는가
- 페이지 번호 질문이 `pdf_page`와 `printed_page`를 혼동하지 않는가
- compare/recommend 질문이 단일 엔트리만 보고 대답하지 않는가
- 답변 citation이 실제 본문 근거와 일치하는가
