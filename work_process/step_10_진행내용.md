# Step 10. Phase 3A Top-1 Precision 정밀화

## 목표
Phase 2에서 확인된 grounding 개선을 유지한 상태에서, top-1 precision 병목을 줄이기 위해 retrieval 상위 정밀도 계층을 강화한다.

## 선행조건
- `step_8_진행내용.md` 완료
- `docs/improvement_plan_v2.md` 기준 Phase 2 작업 반영 완료
- 최신 baseline freeze 존재

## 핵심 판단
1. 현재 병목은 문서를 전혀 못 찾는 문제가 아니라 top-10 안의 정답을 top-1/top-3로 끌어올리지 못하는 문제다.
2. 특히 한국어 page lookup, 한국어 seminar paraphrase, multi-page, recommendation이 취약군이다.
3. 따라서 retrieval 재구축보다 `disambiguation + hard-negative + Korean normalization + multi-page policy + route-aware corpus isolation v2`가 우선이다.

## 필수 작업
1. reranker hard-negative 세트를 구축한다.
- 규정번호 유사군
- NCAP 프로그램 유사군
- safety domain 유사군
- dummy 용어 유사군
- 유사 제목군
- 한국어 paraphrase 유사군

2. page/title disambiguation scorer를 추가한다.
- exact title overlap
- normalized alias match
- page_type prior
- section prior
- standard / acronym exact hit
- competing sibling penalty

3. Korean query normalization / bilingual bridge를 추가한다.
- spaced acronym collapse
- route-aware lexical expansion
- domain lexicon expansion
- bilingual search query 생성

4. multi-page retrieval policy를 도입한다.
- multi-page intent 감지
- top-n merge 허용
- section diversity 고려
- evidence dedup 유지

5. route-aware corpus isolation v2를 적용한다.
- `page_or_index_lookup`
- `seminar_lookup`
- `event_lookup`
- `abbreviation_lookup`
- `recommendation`
- `multi_page_lookup`

## 산출물
- `docs/phase3_execution_guide.md`
- `docs/hard_negative_spec.md`
- `docs/page_title_disambiguation_spec.md`
- `docs/korean_query_normalization_spec.md`
- `docs/multi_page_policy.md`
- `docs/route_corpus_isolation_v2.md`
- `outputs/<run_id>/retrieval_top1_details.csv`
- `outputs/<run_id>/retrieval_top3_details.csv`
- `outputs/<run_id>/korean_query_eval.md`
- `outputs/<run_id>/multi_page_eval.md`
- `outputs/<run_id>/recommendation_eval.md`
- `outputs/<run_id>/reranker_ablation.md`

## 완료 기준
- `retrieval_top1_hit_rate` 개선
- `citation_top1_hit_rate` 개선
- 한국어 취약군 성능이 별도 리포트에서 확인 가능
- multi-page와 recommendation이 별도 KPI로 측정 가능

## 검증 포인트
- route와 맞지 않는 코퍼스가 top-1을 차지하는 비율이 줄어드는가
- 유사 규정/유사 title 혼동이 줄어드는가
- 한국어 paraphrase 질의의 top-1 성능이 좋아지는가
- multi-page 질의에서 single-page 강제 선택이 줄어드는가
