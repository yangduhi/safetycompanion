# Abbreviation Route Spec

## 목표
약어 질의는 retrieval보다 정의 anchoring이 중요하므로 deterministic lookup을 우선 사용한다.

## 규칙
- abbreviation dataset exact hit 시 자유 생성보다 template answer를 우선 사용한다.
- answer는 반드시 아래를 포함한다.
  - abbreviation
  - expansion
  - source title
  - page
- route는 `abbreviation_lookup`으로 고정한다.
- unrelated seminar / knowledge page는 top 후보에서 제외한다.

## 예시
- `ATD는 Anthropomorphic Test Device입니다. 출처: Important Abbreviations (pdf p.215, printed p.215).`
