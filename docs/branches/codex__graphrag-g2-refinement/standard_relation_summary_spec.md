# Standard Relation Summary Spec

## 목적
standard relation query에서 가장 설명력이 높은 summary anchor와 evidence field를 먼저 고르기 위한 규칙을 정의한다.

## 우선 신호
- exact standard anchor in title
- exact standard anchor in selected chunk text
- knowledge entry prior
- standard mention density
- `page_summary` / `knowledge_topic` / `overview` field 우선

## 기대 효과
- related entries는 유지하면서도 summary anchor는 더 직접적인 standard 설명 페이지로 이동
- `GRAPH_SUMMARY_UNGROUNDED` 감소
