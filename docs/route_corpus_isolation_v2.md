# Route Corpus Isolation V2

## 목적
route와 맞지 않는 코퍼스가 top 후보를 오염시키는 문제를 줄인다.

## 원칙
- `abbreviation_lookup`: abbreviation corpus only, 필요 시 fallback
- `page_or_index_lookup`: index / page summary / title-heavy corpus 우선
- `seminar_lookup`: seminar corpus 우선
- `event_lookup`: event corpus 우선
- `recommendation`: seminar / event only
- `multi_page_lookup`: knowledge + seminar 혼합 허용

## 기대 효과
- route contamination 감소
- top-1 precision 개선
- grounding 계층 안정화
