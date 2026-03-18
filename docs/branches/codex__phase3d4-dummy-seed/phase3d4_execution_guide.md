# Phase 3D-4 Execution Guide

## Scope
- dummy family multi-page hard slice만 다룬다.
- focus:
  - seed page priority refinement
  - secondary page compatibility gating
  - page role scoring tuning

## Entry Criteria
- `pytest -q` 통과
- `python -m src.main query "THOR 관련 더미 페이지" --config configs/prod.yaml` 동작
- baseline reference:
  - `docs/baselines/baseline_v5.md`
  - latest multi-page dummy eval

## Implementation Notes
1. query profile에 dummy query mode를 추가한다.
2. multi-page grouping은
   - base rerank
   - group score
   - seed priority score
   - secondary gate
   순서로 분리한다.
3. eval detail CSV에는 seed/secondary 선택 정보를 추가한다.

## Validation
```powershell
pytest -q
python -m src.main eval --config configs/prod.yaml --baseline-label baseline_v6
```

## Success Criteria
- multi-page dummy `top1_hit_rate >= 0.9`
- multi-page dummy `top3_hit_rate == 1.0`
- compare regression 없음
- `EVENT_PARAPHRASE_MISS` 재발 없음
