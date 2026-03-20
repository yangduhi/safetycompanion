# Step 26 진행내용

## 목표

- `G004 Euro NCAP`를 exact-entity semantics로 닫는다.
- representative / supporting tier를 retrieval과 answer path에 함께 반영한다.
- `Euro NCAP` 전용 micro-suite를 추가한다.

## 수행 내용

### 1. query profile 보강

- `standard_entity_target` 추가
- `EURO NCAP` exact entity를 query profile에서 별도 인식

### 2. entity tiering 반영

- `service.py`
  - `EURO_NCAP_EXACT`
  - `NCAP_BROAD_OVERVIEW`
  - `NCAP_SIBLING_PROGRAM`
  - `NCAP_SUPPORTING_CONTEXT`
  구조를 반영
- representative tier가 supporting tier보다 앞서도록 정렬 버그 수정

### 3. answer path tiering

- `answer_generator.py`
  - representative 1개
  - supporting 1~2개
  구조로 entity answer 정리

### 4. routing guardrail

- `router.py`
  - graph relation class가 잡히면 entity/topic lane이 generic event fallback보다 우선

### 5. eval 데이터/산출물

- `data/eval/graph_hard_questions.jsonl`
  - `G004` gold semantics를 exact entity 기준으로 갱신
- `data/eval/euro_ncap_micro_suite.jsonl`
  추가
- 최신 run:
  - `outputs/20260320-222529_90cd5e6d`

## 결과

### Main graph hard set

- `G004 Euro NCAP`: 해결
- `G007 Passive Safety`: 유지
- `G008 Automated Driving`: 유지

### 최신 main graph 지표

- `graph_route_top1_hit_rate = 0.875`
- `graph_route_top3_hit_rate = 1.0`
- `graph_backfill_success_rate = 1.0`
- `graph_grounded_success_rate = 0.875`

남은 failure는 현재 `G002` 한 건이다.

### Euro NCAP micro-suite

- `graph_eval_entity_relation_v5.md`: all pass
- `euro_ncap_confusion_report_v2.md`: no failures

## 다음 단계

1. `G002`가 진짜 잔여 병목인지 재판정
2. code / docs / generated data 분리 커밋 전략 적용
3. ODL whitelist lane 동결 유지
4. `G3`는 계속 보류
