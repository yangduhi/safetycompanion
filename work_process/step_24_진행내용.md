# Step 24 진행내용

## 목표

- interactive vs batch graph eval 불일치 원인을 닫는다.
- ODL whitelist page-level 판정을 확정한다.
- `Passive Safety` representative ranking을 실제 batch eval까지 반영한다.

## 수행 내용

### 1. interactive vs batch diff 추적

- 원인 확인:
  - eval harness 문제가 아니라 manual shell 입력의 한글 인코딩 drift
- 산출물:
  - `docs/branches/codex__graphrag-g2s-route-decomposition/graph_interactive_batch_diff_report.md`
  - `docs/branches/codex__graphrag-g2s-route-decomposition/graph_route_trace_diff.csv`

### 2. ODL whitelist page-level 판정 고정

- 산출물:
  - `docs/current/odl_page_level_verdict_v2.csv`
- 현재 판정:
  - `use_odl_local`: `60, 62, 84, 129, 137`
  - `needs_more_eval`: `61, 85`

### 3. Passive Safety representative 보정

- explicit topic hits를 rerank 전에 seed candidate로 보존
- topic-specific text/title boost 강화
- summit/event penalty 강화
- 산출물:
  - `docs/branches/codex__graphrag-g2s-route-decomposition/passive_safety_representative_spec.md`

## 최신 결과

최신 graph eval run:

- `outputs/20260320-210219_90cd5e6d`

핵심 수치:

- `graph_backfill_success_rate = 1.0`
- `graph_grounded_success_rate = 0.875`
- `graph_route_top1_hit_rate = 0.75`
- `graph_route_top3_hit_rate = 0.875`

route별 상태:

- `G007 Passive Safety`: top1 hit 성공
- `G008 Automated Driving`: top1 hit 성공
- 남은 graph failure: `G004 Euro NCAP`

## 다음 단계

1. `Euro NCAP` entity typing / representative rule 정리
2. generated data와 코드 변경 분리 커밋 전략 적용
3. `G3`는 계속 보류
