# Compare Pairing Spec

## 목적
compare 질의에서 서로 다른 두 대상에 대한 근거를 안정적으로 회수하고, pair 단위로 정렬한다.

## Pairing 규칙
- compare target은 최소 2개 필요
- 가능한 한 target A와 target B 각각에 대응하는 distinct entry를 선택
- 같은 entry만 반복 선택하는 경우 pair 실패로 본다
- pair ranking은 아래 요소를 사용한다.
  - target coverage
  - distinct entry count
  - route policy field priority
  - pair relevance score

## Compare Answer Policy
- 한 줄 결론
- 비교 대상 2개 명시
- 각 대상의 핵심 근거 요약
- 공통점 / 차이점
- 근거 citation

## Failure State
- target extraction 실패
- pair coverage 부족
- distinct entry 부족
- evidence 부족

이 경우 `비교를 위한 문서 근거가 충분하지 않음`을 반환한다.
