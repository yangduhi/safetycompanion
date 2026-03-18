# Span Grounding Spec

모든 evidence item은 가능하면 아래 필드를 포함한다.

- `evidence_text`
- `evidence_field`
- `evidence_start`
- `evidence_end`
- `evidence_page`
- `evidence_confidence`

## 규칙
- `evidence_text`는 선택된 field 텍스트의 일부여야 한다.
- `evidence_start`와 `evidence_end`는 해당 field 텍스트 기준 문자 offset이다.
- span을 찾지 못하면 전체 field의 앞부분을 fallback으로 사용하되 `span_present=false`로 기록한다.
- grounding 평가에서는 page만 맞는 경우와 span까지 확보된 경우를 구분한다.
