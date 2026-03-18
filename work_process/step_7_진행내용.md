# Step 7. 평가, 오류 분석, 품질 개선 루프 구축

## 목표
파싱, 엔트리 추출, retrieval, 답변 grounding을 분리 평가하고, 실패 원인을 체계적으로 분류해 다음 개선 우선순위를 도출한다.

## 선행조건
- `step_6_진행내용.md` 완료

## 핵심 판단
1. 이 프로젝트의 실패는 모델 자체보다 `페이지 복원`, `엔트리 추출`, `lookup 연결`, `citation 정합성`에서 더 자주 발생한다.
2. 특히 SafetyWissen 표형 페이지와 캘린더/색인 기반 질의는 별도 지표가 필요하다.

## 필수 작업
1. 파싱 평가를 수행한다.
- page manifest coverage
- page type accuracy
- seminar/event title extraction accuracy
- table-heavy page extraction warning recall

2. 엔트리 추출 평가를 수행한다.
- 필수 필드 누락률
- bundle 연결 정확도
- calendar-to-entry link accuracy
- abbreviation normalization accuracy

3. retrieval 평가를 수행한다.
- Recall@5
- Recall@10
- MRR
- page hit rate
- exact title hit rate
- abbreviation exact-match accuracy
- calendar lookup accuracy

4. answer 평가를 수행한다.
- groundedness
- citation correctness
- completeness
- hallucination rate
- compare/recommendation 성공률

5. 오류 taxonomy를 구축한다.
- `PAGE_MAP_MISMATCH`
- `PAGE_TYPE_MISCLASSIFIED`
- `TITLE_EXTRACTION_FAIL`
- `TABLE_PARSE_FAIL`
- `MULTI_ENTRY_SPLIT_FAIL`
- `BUNDLE_LINK_FAIL`
- `ACRONYM_NORMALIZATION_FAIL`
- `CALENDAR_LINK_FAIL`
- `RETRIEVAL_MISS_DENSE`
- `RETRIEVAL_MISS_BM25`
- `RERANK_FAIL`
- `GROUNDING_FAIL`

6. 자동 리포트를 생성한다.
- `outputs/<run_id>/eval_summary.md`
- `outputs/<run_id>/error_analysis.csv`
- `outputs/<run_id>/failure_cases.jsonl`

7. 개선 우선순위를 정한다.
- 높은 빈도의 구조 오류
- retrieval miss 유형
- citation 오류
- 그래프 도입 전 해결해야 할 baseline 결함

## 실행 원칙
1. 전체 정확도만 보지 말고 component-wise evaluation을 유지한다.
2. dense only, BM25 only, hybrid, reranker on/off를 비교한다.
3. manual audit sample을 포함해 표형 페이지와 다중 엔트리 페이지를 별도 검증한다.
4. GraphRAG 착수는 baseline이 acceptance criteria를 충족한 뒤 Step 9에서만 허용한다.

## Codex 작업 지시
- `src/eval/retrieval_eval.py`, `src/eval/answer_eval.py`, `src/eval/parse_eval.py`, `src/eval/extraction_eval.py`를 구현하라.
- gold question 외에 adversarial set을 추가해 약어 혼용, 오탈자, 표기 변형, 날짜 질의를 평가하라.
- failure case를 자동 태깅하고, 수정 우선순위를 제안하라.

## 완료 기준
- 파싱, 추출, retrieval, answer 지표가 모두 산출됨
- 주요 실패 원인 상위 목록이 도출됨
- baseline go/no-go 판단이 가능해짐

## 산출물
- `outputs/<run_id>/eval_summary.md`
- `outputs/<run_id>/error_analysis.csv`
- `outputs/<run_id>/failure_cases.jsonl`
- `data/eval/adversarial_questions.jsonl`

## 검증 포인트
- hybrid retrieval의 개선폭이 수치로 확인되는가
- 캘린더/색인 질의의 실패 원인이 별도 분리되는가
- citation 오류가 어디서 발생했는지 추적 가능한가
- baseline 품질 미달 상태에서 GraphRAG 단계로 넘어가지 않도록 통제되는가
