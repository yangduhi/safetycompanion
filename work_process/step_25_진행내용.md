# Step 25 진행내용

## 목표

- `interactive vs batch` 불일치 원인을 최종 확인한다.
- `Passive Safety`와 `Automated Driving` topic lane을 batch 기준으로 끌어올린다.
- `G004 Euro NCAP`를 다음 단일 집중 과제로 분리한다.
- CLI 인코딩 가드레일을 추가한다.

## 수행 내용

### 1. interactive vs batch 원인 확정

- 원인: eval harness가 아니라 manual PowerShell 한국어 입력 인코딩 drift
- 결과:
  - 파일 기반 UTF-8 query와 batch eval은 정렬됨

### 2. topic cluster representative 개선

- explicit topic hits를 rerank 전에 seed candidate로 보존
- `Passive Safety`:
  - page `18`, `20`이 대표 후보로 복귀
- `Automated Driving`:
  - page `145`, `142`가 대표 후보로 정렬

### 3. 최신 graph batch eval

- run: `outputs/20260320-210219_90cd5e6d`
- 수치:
  - `graph_backfill_success_rate = 1.0`
  - `graph_grounded_success_rate = 0.875`
  - `graph_route_top1_hit_rate = 0.75`
  - `graph_route_top3_hit_rate = 0.875`
- 남은 실패:
  - `G004 Euro NCAP`

### 4. CLI 인코딩 가드레일

- `query` 명령에 `--question-file` 추가
- 인코딩 깨짐 의심 시 warning 출력

## 다음 단계

1. `Euro NCAP` entity typing / representative 규칙 정리
2. generated data와 code/docs 분리 커밋 전략 실행
3. ODL는 whitelist lane 유지
4. `G3`는 계속 보류
