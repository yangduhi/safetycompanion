# Step 13. Phase 3D Multi-Page Hard Slice Stabilization 및 Taxonomy V2

## 목표
남아 있는 `MULTI_PAGE_COLLAPSE` 계열 실패를 줄이고, multi-page / dummy hard slice를 운영 가능한 수준으로 안정화한다.

## 선행조건
- `step_12_진행내용.md` 완료
- `docs/baselines/baseline_v4.md` 존재
- compare는 regression 대상 수준으로 안정화됨

## 핵심 판단
1. 남은 대표 실패는 broad retrieval 문제가 아니라 `multi-page grouping` 문제다.
2. THOR / dummy / ATD / landscape 계열은 page-grouping과 entity anchor가 함께 작동해야 한다.
3. taxonomy는 이제 단일 라벨이 아니라 subtype까지 운영 수준으로 내려가야 한다.

## 필수 작업
1. multi-page hard set을 확장한다.
2. dummy / THOR anchor 강화를 적용한다.
3. multi-page grouping policy v2를 도입한다.
4. taxonomy subtype을 도입한다.
5. compare는 regression 확인만 수행한다.

## 산출물
- `docs/phase3d_execution_guide.md`
- `docs/multi_page_hardset_spec.md`
- `docs/taxonomy_v2_spec.md`
- `docs/dummy_anchor_spec.md`
- `docs/multi_page_grouping_spec.md`
- `docs/compare_regression_spec.md`
- `outputs/<run_id>/multi_page_eval.md`
- `outputs/<run_id>/multi_page_group_details.csv`
- `outputs/<run_id>/dummy_hardslice_eval.md`
- `outputs/<run_id>/error_taxonomy_report_v2.md`
- `outputs/<run_id>/compare_regression_report.md`

## 완료 기준
- multi-page hard set 확대
- `MULTI_PAGE_COLLAPSE` 원인 subtype 분해
- THOR / dummy / ATD 계열의 page grouping 안정화
- compare regression 없음

## 검증 포인트
- multi-page 질의에서 page list가 먼저 안정적으로 고정되는가
- dummy / THOR 계열에서 관련 페이지 cluster가 자연스럽게 묶이는가
- taxonomy가 subtype 수준으로 구분되는가
