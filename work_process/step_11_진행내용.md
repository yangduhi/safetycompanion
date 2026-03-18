# Step 11. Phase 3B Hard-Route Precision 및 Error Taxonomy

## 목표
메인라인 성능을 유지한 채, hard slice에서 남아 있는 route misclassification, exact-anchor miss, compare 실패, event paraphrase 실패를 줄인다.

## 선행조건
- `step_10_진행내용.md` 완료
- `docs/baselines/baseline_v2.md` 존재
- 최신 eval에서 mainline 지표가 안정적으로 유지됨

## 핵심 판단
1. 현재 병목은 broad retrieval이 아니라 hard-route precision이다.
2. 평균 성능보다 `compare`, `adversarial page_lookup`, `adversarial event_lookup`, `exact-anchor query`의 실패 제거가 더 중요하다.
3. Error taxonomy는 이제 디버깅 보조가 아니라 운영 스키마로 승격해야 한다.

## 필수 작업
1. compare intent를 multi-page intent와 분리한다.
2. exact-anchor normalization 계층을 강화한다.
3. event paraphrase alias를 보강한다.
4. adversarial page/event route scoring을 강화한다.
5. hard-route failure를 분류하는 taxonomy를 도입한다.
6. hard slice 전용 eval 리포트를 생성한다.

## 산출물
- `docs/phase3b_execution_guide.md`
- `docs/error_taxonomy_spec.md`
- `docs/hard_route_precision_spec.md`
- `docs/exact_anchor_normalization_spec.md`
- `docs/event_paraphrase_alias_spec.md`
- `docs/compare_route_spec.md`
- `outputs/<run_id>/hard_route_eval.md`
- `outputs/<run_id>/error_taxonomy_report.md`
- `outputs/<run_id>/compare_eval.md`
- `outputs/<run_id>/event_lookup_eval.md`
- `outputs/<run_id>/exact_anchor_eval.md`

## 완료 기준
- `compare` 질의군이 독립 route로 분리됨
- `fmvss305a`류 질의의 exact-anchor miss 감소
- `event paraphrase` 질의군 오분류 감소
- failure taxonomy가 detail CSV와 함께 산출됨

## 검증 포인트
- `compare` route가 `multi_page_lookup`로 새지 않는가
- `event_lookup` 질의가 `fallback_general`로 빠지지 않는가
- exact code query가 title/code-aware hit를 받는가
- mainline 지표를 깨지 않고 hard slice 지표가 개선되는가
