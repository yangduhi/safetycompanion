# Compare Regression Spec

## 목표
compare slice는 이번 반복에서 개선 대상이 아니라 regression 감시 대상으로 둔다.

## 체크 항목
- compare top1 유지
- compare grounded success 유지
- compare pair selection 유지

## 규칙
- multi-page 개선 중 compare 지표가 떨어지면 회귀로 본다
