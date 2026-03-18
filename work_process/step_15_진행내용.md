# Step 15. Phase 3D-3 Dummy Grouping Refinement V2 및 Event Paraphrase Closure

## 목표
dummy / THOR / ATD / landscape 계열 multi-page hard slice의 top-1 grouping 품질을 한 단계 더 끌어올리고, 남아 있는 event paraphrase 잔여 실패를 닫는다.

## 선행조건
- `step_14_진행내용.md` 완료
- `docs/baselines/baseline_v5.md` 존재
- compare는 regression 유지 상태

## 핵심 판단
1. 남은 병목은 recall이 아니라 top-1 grouping coherence다.
2. dummy hard slice는 seed page는 대체로 맞고, secondary page 및 role assignment가 흔들릴 가능성이 높다.
3. `The ADAS Experience 관련 페이지`류 질의는 event alias가 있는데도 multi-page/page path로 새는 잔여 route 문제다.

## 필수 작업
1. dummy anchor cluster canonicalization을 보강한다.
2. page role scoring을 정교화한다.
3. secondary page selection gate를 강화한다.
4. event paraphrase alias와 route bias를 보정한다.
5. multi-page dummy hard set 재평가 및 taxonomy v3를 갱신한다.

## 산출물
- `docs/phase3d3_execution_guide.md`
- `docs/dummy_grouping_refinement_spec.md`
- `outputs/<run_id>/multi_page_dummy_eval.md`
- `outputs/<run_id>/error_taxonomy_report_v3.md`
- `outputs/<run_id>/compare_regression_report.md`

## 완료 기준
- multi-page dummy `top1_hit_rate` 개선
- `EVENT_PARAPHRASE_MISS` 감소 또는 제거
- compare regression 없음
