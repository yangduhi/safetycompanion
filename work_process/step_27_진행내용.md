# Step 27 진행내용

## 목표

- `G002`를 단일 케이스로 triage한다.
- 진짜 residual bottleneck인지, eval/contract mismatch인지 판정한다.

## 확인 결과

- route: `entity_relation_lookup`
- graph backfill: 성공
- top-3 candidate에는 기존 기대 페이지 `137`, `129`가 모두 포함
- top-1은 page `138` seminar였고, 이 페이지 역시 `THOR`와 `Hybrid III`를 함께 직접 다룸

## 판정

`G002`는 현재 기준으로:

- model failure라기보다
- `eval / answer contract mismatch`

로 보는 것이 더 타당하다.

## 조치

- `graph_hard_questions.jsonl`의 `G002` gold set을
  - `138`
  - `129`
  - `137`
  기준으로 갱신
- 관련 triage 산출물 추가
  - `g002_case_report.md`
  - `g002_route_trace.csv`
  - `g002_candidate_diff.jsonl`

## 기대 효과

- graph lane의 실제 동작과 평가 기준이 일치
- 남은 false residual을 줄여 current graph lane 상태를 더 정확히 표현
