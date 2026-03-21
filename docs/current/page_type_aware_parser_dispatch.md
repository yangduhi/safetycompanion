# Page-Type-Aware Parser Dispatch

## 목적

parser 선택은 retrieval route 기준이 아니라 ingest 시점의 `page_type` 기준으로 수행해야 한다. 이 문서는 그 dispatch 원칙을 고정한다.

## 기본 원칙

1. 전체 PDF는 먼저 `pdftotext -layout`로 파싱한다.
2. 1차 분류 결과에서 page별 `page_type`을 얻는다.
3. 특정 `page_type`만 auxiliary parser 대상 후보로 선택한다.
4. 보조 파서가 성공한 페이지에 한해 manifest / blocks를 교체한다.
5. 실패 시 `strict: false`면 기본 결과를 유지한다.

## 현재 dispatch 규칙

### primary

- parser: `pdftotext -layout`
- 대상: 전체 PDF

### auxiliary

- parser: `opendataloader-pdf`
- 대상 page type:
  - `knowledge`
- gate:
  - `min_word_count`
  - 실험 config에서 `enabled: true`

## 제외 대상

아래는 1차 auxiliary parser 대상에서 제외한다.

- `seminar`
- `event`
- `abbreviations`
- `calendar`
- `index`

이유:
- 후속 추출기가 기존 `raw_text` 레이아웃에 강하게 의존함

## 산출물 영향

보조 파서가 성공하면 아래 필드에 영향이 간다.

- `page_manifest.parser_engine`
- `page_manifest.parser_mode`
- `page_manifest.primary_parser_engine`
- `page_blocks.parser_engine`
- downstream `entries.jsonl`의 `knowledge` 계열 필드

## 운영 주의

- auxiliary parser 실험은 `prod` 경로와 분리한다.
- parser dispatch는 retrieval route와 혼동하지 않는다.
- 이 구조를 “route-aware parser selection”이 아니라 “page-type-aware parser dispatch”로 부른다.
