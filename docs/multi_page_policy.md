# Multi Page Policy

## 목적
정답이 여러 페이지에 걸친 질의를 single-page top-1 문제로 오인하지 않도록 분리 처리한다.

## 규칙
- multi-page intent를 별도로 감지한다.
- multi-page route에서는 top-n merge를 허용한다.
- 서로 다른 page 또는 entry를 유지하도록 diversity를 적용한다.
- evidence dedup는 유지한다.

## 답변 원칙
- 먼저 관련 페이지 목록을 구조화해서 보여준다.
- 이후 요약을 덧붙인다.
