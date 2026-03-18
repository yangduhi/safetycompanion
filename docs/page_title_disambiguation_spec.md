# Page and Title Disambiguation Spec

## 목적
유사 topic, 유사 title, 같은 도메인 내 다른 section 때문에 발생하는 top-1 오류를 줄인다.

## feature 후보
- exact title token overlap
- normalized title alias hit
- standard code exact hit
- acronym exact hit
- page lookup prior
- page type prior
- section prior
- sibling mismatch penalty

## 적용 위치
- reranker 이후의 얇은 보정 scorer
- 또는 reranker 내부 additive feature
