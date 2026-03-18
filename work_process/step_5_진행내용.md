# Step 5. 멀티레벨 청킹 및 하이브리드 인덱스 구축

## 목표
문서 구조에 맞는 chunk 계층을 만들고, dense retrieval과 lexical lookup이 함께 작동하는 하이브리드 인덱스를 구축한다.

## 선행조건
- `step_4_진행내용.md` 완료

## 핵심 판단
1. 이 PDF는 일반적인 균일 500-token 청킹보다 **entry-aware + field-aware 청킹**이 훨씬 유리하다.
2. 약어, 색인, 캘린더, 표형 지식 페이지는 서로 검색 전략이 다르므로 단일 인덱스로 해결하려고 하면 손실이 크다.

## 필수 작업
1. 아래 chunk 타입을 만든다.
- `entry_overview_chunk`
- `field_chunk`
- `knowledge_table_chunk`
- `calendar_chunk`
- `abbreviation_chunk`
- `index_lookup_chunk`

2. 모든 chunk에 공통 메타데이터를 포함한다.
- `chunk_id`
- `entry_id`
- `entry_bundle_id`
- `pdf_page`
- `printed_page`
- `section_l1`
- `page_type`
- `entry_type`
- `field_name`
- `title`
- `text`
- `is_primary_corpus`

3. 아래 인덱스를 구축한다.
- Dense Entry Index
- Dense Field Index
- BM25 Index
- Abbreviation Lookup Store
- Back Index Lookup Store
- Calendar Lookup Store
- Metadata Filter Store

4. chunk 가중치 전략을 정의한다.
- `title`, `course_contents`, `course_objectives`, `abbreviation`에는 높은 prior
- `calendar`는 일정 질의에서만 우선
- `advertisement`, `terms`, `directory`는 기본 검색 제외 또는 매우 낮은 prior

5. `index_build_manifest`를 남긴다.
- 문서 해시
- 엔트리 수
- chunk 수
- index 생성 시각
- embedding 모델명
- BM25 버전
- lookup store 버전

6. smoke test를 자동화한다.
- 약어형 질문
- 페이지 탐색형 질문
- 세미나 찾기형 질문
- 비교형 질문
- 캘린더 질의

## 설계 원칙
1. 정답 가능성이 높은 구조화 필드를 먼저 chunk로 만들고, 긴 텍스트만 추가 세분화한다.
2. 캘린더와 색인 검색은 dense보다 exact lookup이 먼저 실행되도록 설계한다.
3. 추후 ColBERT류 실험을 위해 chunk 저장 포맷은 late-interaction 친화적으로 유지한다.

## Codex 작업 지시
- `src/retrieval/chunker.py`, `src/retrieval/build_indexes.py`, `src/retrieval/lookup_stores.py`를 구현하라.
- `indexes/` 아래에 dense, bm25, lookup 저장소를 분리하라.
- 인덱스 빌드 결과를 `outputs/<run_id>/index_build_manifest.json`에 남기고, 20개 내외의 smoke test를 자동 실행하라.

## 완료 기준
- 구조화 chunk와 lookup store가 생성됨
- dense와 lexical이 모두 동작함
- 캘린더/색인/약어 질의가 별도 경로로 처리될 수 있는 기반이 마련됨
- smoke test에서 빈 응답 비율이 허용 범위 이내임

## 산출물
- `data/processed/chunks.jsonl`
- `indexes/dense_entry/*`
- `indexes/dense_field/*`
- `indexes/bm25/*`
- `indexes/lookup/*`
- `outputs/<run_id>/index_build_manifest.json`
- `outputs/<run_id>/retrieval_smoke_test.md`

## 검증 포인트
- 같은 질의에서 dense와 BM25가 상보적인 후보를 제공하는가
- 약어/색인/캘린더 질의가 불필요하게 dense semantic retrieval로만 가지 않는가
- chunk 메타데이터만으로도 citation 구성에 필요한 정보가 충분한가
