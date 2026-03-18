# Step 16. Phase 3D-4 Dummy Grouping Refinement V3

## 목표
dummy / THOR / ATD / landscape 계열 multi-page hard slice에서 남아 있는 top-1 grouping 흔들림을 줄인다.

## 선행조건
- `step_15_진행내용.md` 완료
- 리팩토링 후 `pytest -q` 및 기본 query smoke test 통과
- `docs/baselines/baseline_v5.md` 기준점 확인

## 핵심 판단
1. 남은 병목은 retrieval recall이 아니라 seed page와 secondary page를 고르는 최종 grouping decision이다.
2. `MULTI_PAGE_COLLAPSE__DUMMY_TOPIC_MERGE_FAIL`는 seed 우선순위와 secondary gate가 충분히 분리되지 않아 생길 가능성이 높다.
3. compare는 유지 검증만 수행하고, 이번 반복은 dummy family hard slice에만 집중한다.

## 필수 작업
1. seed page priority를 query mode별로 분리한다.
2. secondary page compatibility gate를 추가한다.
3. page role scoring을 seed/secondary 단계에서 각각 사용한다.
4. seed/secondary 선택 로그를 eval CSV에 남긴다.
5. `multi_page_dummy_eval`와 taxonomy를 다시 평가한다.

## 산출물
- `docs/branches/codex__phase3d4-dummy-seed/phase3d4_execution_guide.md`
- `docs/branches/codex__phase3d4-dummy-seed/dummy_seed_priority_spec.md`
- `docs/branches/codex__phase3d4-dummy-seed/secondary_page_gating_spec.md`
- `docs/branches/codex__phase3d4-dummy-seed/page_role_scoring_tuning_spec.md`
- `outputs/<run_id>/multi_page_dummy_eval_v3.md`
- `outputs/<run_id>/multi_page_group_details_v4.csv`
- `outputs/<run_id>/error_taxonomy_report_v4.md`

## 완료 기준
- multi-page dummy `top1_hit_rate`가 baseline 대비 개선
- `top3/top10` 유지
- `MULTI_PAGE_COLLAPSE__DUMMY_TOPIC_MERGE_FAIL` 감소
- compare regression 없음
- event paraphrase 재발 없음
