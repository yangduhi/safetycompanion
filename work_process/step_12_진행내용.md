# Step 12. Phase 3C Compare Pair-Ranking 및 Compare Answer Policy

## 목표
`compare` 질의를 독립 문제로 다루고, 두 개 이상의 비교 대상을 안정적으로 식별·회수·정렬·설명할 수 있도록 pair-ranking과 compare 전용 answer policy를 구축한다.

## 선행조건
- `step_11_진행내용.md` 완료
- `docs/baselines/baseline_v3.md` 존재
- mainline 지표가 안정적으로 유지됨

## 핵심 판단
1. 현재 남은 핵심 병목은 compare slice다.
2. compare는 일반 retrieval 문제가 아니라 `target extraction -> distinct evidence pairing -> pair-level ranking -> comparison answer policy`의 묶음 문제다.
3. compare 전용 pair-ranking이 없으면 top-10 안에 정답이 있어도 top-1과 grounded가 동시에 흔들릴 수 있다.

## 필수 작업
1. compare target extraction을 강화한다.
2. compare route 전용 pair-ranking을 구현한다.
3. compare answer policy를 독립 템플릿으로 구현한다.
4. compare pair detail 리포트와 compare grounding 리포트를 추가한다.
5. taxonomy에 `COMPARE_PAIRING_FAIL`를 반영한다.

## 산출물
- `docs/phase3c_execution_guide.md`
- `docs/compare_pairing_spec.md`
- `outputs/<run_id>/compare_eval.md`
- `outputs/<run_id>/compare_pair_details.csv`
- `outputs/<run_id>/compare_grounding_report.md`

## 완료 기준
- compare route에서 최소 2 distinct entry가 선택됨
- compare 질문은 compare 전용 answer policy를 사용함
- compare top-1 / grounded가 baseline보다 개선됨
- mainline 지표를 깨지 않음

## 검증 포인트
- compare 질문이 multi-page/general fallback으로 흐르지 않는가
- pair selection이 두 개 이상의 distinct entry를 보장하는가
- 비교 답변에 근거와 비교 기준이 함께 표시되는가
