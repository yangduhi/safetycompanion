# Hard Route Precision Spec

## 대상 slice
- compare
- event paraphrase
- exact-anchor page lookup
- adversarial page lookup

## 목적
정답이 top-10 안에 있을 때 top-1로 끌어올리는 정밀화 계층을 강화한다.

## 핵심 수단
- route 분리
- anchor normalization
- route-aware scorer
- disambiguation feature
