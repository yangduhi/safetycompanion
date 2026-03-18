# Step 4. 엔트리 추출 및 보조 데이터셋 구축

## 목표
페이지 수준 구조를 바탕으로, 검색과 답변에 직접 쓰일 **entry 레코드**와 약어/색인/캘린더 같은 보조 데이터셋을 만든다.

## 선행조건
- `step_3_진행내용.md` 완료

## 핵심 판단
1. 이 문서는 페이지 단위 검색보다 **entry 단위 정규화 품질**이 더 중요하다.
2. 세미나/이벤트/지식 페이지는 서로 필드 구조가 다르므로 하나의 느슨한 스키마로 뭉개면 검색 품질이 떨어진다.
3. 캘린더, 색인, 약어집은 주 코퍼스가 아니라도 retrieval routing에 매우 강력한 힌트가 된다.

## 필수 작업
1. `seminar`, `event`, `knowledge` 페이지에서 엔트리를 추출한다.
- `entry_bundle_id`
- `entry_id`
- `page_start_pdf`
- `page_end_pdf`
- `printed_pages`
- `entry_type`
- `section_l1`
- `title`
- `subtitle`
- `is_new`
- `summary`
- `fields`
- `facts`
- `source_pages`

2. 세미나/이벤트 페이지에서는 아래 필드를 우선 추출한다.
- `course_description`
- `course_objectives`
- `who_should_attend`
- `course_contents`
- `facts`
- `date`
- `location`
- `duration`
- `price`
- `course_code`
- `instructors`
- `partner`

3. SafetyWissen 페이지에서는 아래 필드를 우선 추출한다.
- `knowledge_topic`
- `standard_or_program`
- `table_headers`
- `key_points`
- `page_summary`
- `mentioned_entities`

4. 다중 엔트리와 multi-page bundle을 처리한다.
- 한 페이지에 세미나가 2개 이상 있으면 separate `entry_id` 부여
- 2페이지 이상 이어지는 이벤트는 하나의 `entry_bundle_id`로 묶기
- continuation 페이지는 상위 bundle과 연결

5. 보조 데이터셋을 생성한다.
- `abbreviations.jsonl`: `abbr`, `expansion`, `aliases`, `section_hint`
- `back_index.jsonl`: `keyword`, `target_printed_pages`, `target_pdf_pages`
- `calendar_entries.jsonl`: `date`, `location`, `title`, `target_page`
- `page_links.jsonl`: 목차/색인/캘린더에서 본문으로 가는 참조 링크

6. 정규화와 검증을 구현한다.
- 약어/표기 변형 정규화
- 기관명/규정명 canonicalization
- 누락 필드 검증
- 잘못된 페이지 참조 검증
- 일정과 세미나 페이지의 상호 참조 검증

## 개선 포인트
1. 기존 초안보다 `calendar`를 정식 데이터셋으로 승격한다.
2. 단일 페이지 기반 `entry_id`만으로는 부족하므로 `entry_bundle_id`를 추가한다.
3. SafetyWissen 페이지는 일반 문단이 아니라 표/비교표가 많으므로 `table_headers`, `key_points` 같은 필드를 별도 둔다.

## Codex 작업 지시
- `src/ingest/entry_extractor.py`, `src/ingest/abbreviation_extractor.py`, `src/ingest/index_extractor.py`, `src/ingest/calendar_extractor.py`를 구현하라.
- 출력은 JSONL 중심으로 저장하라.
- `outputs/<run_id>/extraction_quality_report.md`에 필드별 누락률, 정규화 수, 참조 링크 성공률을 기록하라.

## 완료 기준
- 세미나/이벤트/지식 엔트리가 구조화 레코드로 변환됨
- 약어/색인/캘린더 데이터셋이 별도 생성됨
- 다중 엔트리와 multi-page bundle이 누락 없이 연결됨
- 페이지 참조가 자동 검증됨

## 산출물
- `data/processed/entries.jsonl`
- `data/processed/abbreviations.jsonl`
- `data/processed/back_index.jsonl`
- `data/processed/calendar_entries.jsonl`
- `data/processed/page_links.jsonl`
- `outputs/<run_id>/extraction_quality_report.md`

## 검증 포인트
- page 139 같은 다중 엔트리 페이지가 분리 추출되는가
- 이벤트 연속 페이지가 하나의 bundle로 묶이는가
- 캘린더의 페이지 참조가 실제 세미나/이벤트 엔트리로 연결되는가
- 약어와 색인 페이지의 참조 페이지가 실제 본문과 일치하는가
