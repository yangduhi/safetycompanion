# Step 14. Phase 3D-2 Dummy Anchor 강화 및 Multi-Page Grouping V3

## 목표
`dummy / THOR / ATD / landscape` 계열 multi-page 질의에서 anchor canonicalization과 page-group coherence를 강화하고, 응답을 page-role 중심 구조로 고정한다.

## 선행조건
- `step_13_진행내용.md` 완료
- `docs/baselines/baseline_v5.md` 존재
- compare는 regression 유지 대상임

## 핵심 판단
1. 남은 주요 실패는 dummy 계열 multi-page grouping 정밀도다.
2. 이 문제는 단일 page relevance보다 `anchor canonicalization + group coherence + page role assignment` 문제다.
3. 따라서 다음 반복의 목표는 average metric 개선이 아니라 multi-page hard slice 안정화다.

## 필수 작업
1. dummy anchor canonicalization v2를 구현한다.
2. multi-page grouping policy v3를 적용한다.
3. page-role 중심 answer policy를 도입한다.
4. taxonomy v3 subtype을 도입한다.
5. multi-page hard set을 별도 파일로 분리하고 평가한다.

## 산출물
- `docs/phase3d2_execution_guide.md`
- `docs/dummy_anchor_spec_v2.md`
- `docs/multi_page_grouping_spec_v3.md`
- `docs/page_role_assignment_spec.md`
- `docs/taxonomy_v3_spec.md`
- `docs/multi_page_dummy_hardset_spec.md`
- `data/eval/multi_page_hard_questions.jsonl`
- `outputs/<run_id>/multi_page_dummy_eval.md`
- `outputs/<run_id>/multi_page_group_details_v2.csv`
- `outputs/<run_id>/dummy_anchor_eval.md`
- `outputs/<run_id>/error_taxonomy_report_v3.md`
- `outputs/<run_id>/compare_regression_report.md`

## 완료 기준
- dummy 계열 canonical cluster가 질의 정규화에 반영됨
- multi-page 응답이 `page list -> page role -> summary` 구조를 따름
- taxonomy가 v3 subtype을 사용함
- dummy / THOR hard slice 개선 또는 실패 원인 명확화

## 검증 포인트
- unrelated page intrusion이 줄어드는가
- THOR / HIII / ATD 관련 질의에서 page role이 자연스럽게 배정되는가
- multi-page hard set 리포트가 별도로 생성되는가
