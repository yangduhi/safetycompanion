# Minimal Graph Schema

## 목적
G1에서 구현할 최소 graph index의 노드/엣지/증거 규칙을 고정한다.

## G1 최소 노드

- `Entry`
- `Topic`
- `DummyFamily`
- `Standard`
- `Organization`

## G1 최소 엣지

- `BELONGS_TO_TOPIC`
- `MENTIONS_DUMMY`
- `MENTIONS_STANDARD`
- `MENTIONS_ORG`
- `RELATED_TO_ENTRY`

## 노드 공통 필드

- `node_id`
- `node_type`
- `name`
- `source_entry_ids`
- `source_pages`
- `confidence`

## 엣지 공통 필드

- `edge_id`
- `edge_type`
- `source_id`
- `target_id`
- `source_entry_id`
- `source_page`
- `source_field`
- `provenance_text`
- `extraction_method`
- `confidence`

## provenance 규칙

- 모든 edge는 최소 하나의 `source_entry_id`와 `source_page`를 가져야 한다.
- `provenance_text`는 원문 요약 또는 추출 span이어야 하며 빈 문자열이면 안 된다.
- `extraction_method`는 최소 `heuristic`, `rule`, `llm` 중 하나를 사용한다.

## G1 제외 대상

- `Instructor`
- `TAUGHT_BY`
- global summary node
- synthetic summary edge

이 항목들은 G2 이후 필요성이 입증된 뒤 추가한다.
