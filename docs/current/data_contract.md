# Data Contract

이 문서는 현재 저장소에서 실제로 사용되는 핵심 데이터셋과 산출물 계약을 요약한다. 세부 필드는 additive하게 확장될 수 있지만, 아래 핵심 필드와 의미는 유지해야 한다.

## 1. 공통 식별자

- `document_id`: 문서 식별자
- `pdf_page`: PDF 기준 물리 페이지 번호
- `printed_page`: 문서 내부 인쇄 페이지 번호, 없으면 `null`
- `entry_id`: retrieval 대상 엔트리 식별자
- `entry_bundle_id`: multi-page 또는 관련 엔트리 묶음 식별자
- `chunk_id`: retrieval chunk 식별자
- `run_id`: 실행 식별자

## 2. 주요 파일 경로

- `data/raw/source_page_map.jsonl`
- `data/parsed/page_manifest.jsonl`
- `data/parsed/page_blocks.jsonl`
- `data/processed/entries.jsonl`
- `data/processed/abbreviations.jsonl`
- `data/processed/back_index.jsonl`
- `data/processed/calendar_entries.jsonl`
- `data/processed/page_links.jsonl`
- `data/processed/chunks.jsonl`
- `data/graph/nodes.jsonl`
- `data/graph/edges.jsonl`
- `outputs/<run_id>/run_manifest.json`

## 3. Page Manifest

핵심 필드:

- `document_id`
- `pdf_page`
- `printed_page`
- `page_type`
- `section_l1`
- `title`
- `text`
- `raw_text`
- `word_count`
- `extraction_quality`
- `is_primary_corpus`
- `page_bundle_role`

설명:

- 모든 페이지는 `page_type`을 가져야 한다.
- retrieval 대상이 아닌 페이지도 manifest에는 포함된다.
- `is_primary_corpus`는 기본 검색 코퍼스 포함 여부를 나타낸다.

## 4. Entry Record

핵심 필드:

- `document_id`
- `entry_id`
- `entry_bundle_id`
- `entry_type`
- `title`
- `subtitle`
- `is_new`
- `section_l1`
- `summary`
- `source_pages`
- `printed_pages`
- `fields`
- `facts`

설명:

- `entry_type`은 주로 `seminar`, `event`, `knowledge` 중 하나다.
- `fields`는 route별 retrieval 우선순위에 사용되는 구조화 필드 모음이다.
- `facts`는 선택 확장 필드다.

## 5. Chunk Record

핵심 필드:

- `entry_id`
- `entry_bundle_id`
- `title`
- `pdf_page`
- `printed_page`
- `section_l1`
- `entry_type`
- `chunk_id`
- `chunk_type`
- `field_name`
- `text`
- `is_primary_corpus`

설명:

- `chunk_type`은 `entry_overview_chunk`, `field_chunk`, `calendar_chunk`, `index_lookup_chunk` 등으로 구분된다.
- `field_name`은 grounded answer와 route별 evidence 선택에 직접 사용된다.

## 6. Run Manifest

핵심 필드:

- `run_id`
- `source_file`
- `source_hash`
- `config_file`
- `config_hash`
- `git_commit`
- `started_at`
- `finished_at`
- `status`
- `steps_completed`
- `artifacts`
- `metrics`
- `notes`

설명:

- 실행별 산출물 인덱스 역할을 한다.
- `artifacts`는 상대경로 문자열 목록이다.
- `metrics`는 단계별 수집 지표를 포함한다.

## 7. Citation 계약

최종 답변은 최소 아래 정보를 담아야 한다.

- `title`
- `pdf_page`
- `printed_page`가 있으면 함께 표기

권장 표기:

- `Title (pdf p.X, printed p.Y, field field_name)`

## 8. 호환성 규칙

- `pdf_page`와 `printed_page`의 의미를 바꾸지 않는다.
- 기존 핵심 필드는 이름을 임의 변경하지 않는다.
- 새로운 필드 추가는 허용하지만, 기존 evaluator와 query path를 깨지 않아야 한다.

## 9. Graph Artifact Contract

graph 실험 config에서만 아래 산출물을 사용한다.

### Graph Node

핵심 필드:

- `node_id`
- `node_type`
- `name`
- `canonical_name`
- `source_entry_ids`
- `source_pages`
- `source_fields`
- `confidence`

### Graph Edge

핵심 필드:

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

설명:

- graph edge는 반드시 provenance를 가져야 한다.
- graph 결과는 최종 답변 전에 entry/page evidence로 backfill되어야 한다.
