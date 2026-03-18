# Step 9. 선택형 Small GraphRAG 도입

## 목표
baseline 경로를 유지한 상태에서, 관계형/추천형 질의 보조를 위한 소형 GraphRAG를 선택적으로 추가한다.

## 선행조건
- `step_8_진행내용.md` 완료
- Step 7 gate 통과 유지
- graph track 사용 허용

## 핵심 판단
1. 이 PDF는 교육 카탈로그이므로 GraphRAG는 주 검색 경로가 아니라 보조 계층이어야 한다.
2. GraphRAG 실패가 baseline 경로를 깨뜨리면 안 된다.

## 필수 작업
1. Small GraphRAG 범위를 아래로 제한한다.
- `Course/Event -> Topic`
- `Course/Event -> Standard/Regulation`
- `Course/Event -> Test Method`
- `Course/Event -> Instructor`
- `Abbreviation -> Expansion`
- `Topic -> Related Topic`

2. 그래프 스키마를 설계한다.
- 노드: `Course`, `Event`, `KnowledgeTopic`, `Standard`, `TestMethod`, `Instructor`, `Organization`, `Abbreviation`
- 엣지: `BELONGS_TO_TOPIC`, `COVERS_STANDARD`, `COVERS_METHOD`, `TAUGHT_BY`, `MENTIONS_ORG`, `ABBREVIATES_TO`, `RELATED_TO`
- 모든 edge에 `source_page`, `provenance_text`, `confidence`를 저장

3. 그래프 구축과 retrieval을 구현한다.
- entity extraction
- relation extraction
- graph export
- path retrieval
- text backfill

4. graph 기능은 설정으로만 활성화한다.
- `configs/exp_graph.yaml`
- baseline `configs/prod.yaml`은 그대로 유지

## 운영 원칙
1. 그래프만으로 답하지 말고 반드시 텍스트 근거를 backfill한다.
2. graph track 실패 시 baseline query 경로는 계속 사용 가능해야 한다.
3. graph 산출물은 `data/graph/`와 `outputs/<run_id>/graph_*.md`에 저장한다.

## Codex 작업 지시
- `src/graph/entity_extractor.py`, `src/graph/relation_extractor.py`, `src/graph/graph_builder.py`, `src/graph/graph_retriever.py`를 구현하라.
- `configs/exp_graph.yaml`을 작성하라.
- 그래프의 모든 edge에 provenance를 남겨라.
- graph 경로의 평가 결과를 baseline과 분리해 기록하라.

## 완료 기준
- graph 기능이 baseline과 분리되어 on/off 가능함
- relationship/recommendation 질의에서 graph path를 사용할 수 있음
- 모든 graph 답변이 최종적으로 텍스트 citation을 포함함

## 산출물
- `src/graph/entity_extractor.py`
- `src/graph/relation_extractor.py`
- `src/graph/graph_builder.py`
- `src/graph/graph_retriever.py`
- `configs/exp_graph.yaml`
- `data/graph/nodes.jsonl`
- `data/graph/edges.jsonl`
- `outputs/<run_id>/graph_schema.md`
- `outputs/<run_id>/graph_samples.md`

## 검증 포인트
- graph 기능을 꺼도 baseline이 그대로 동작하는가
- graph path가 실제 본문 근거 페이지로 되돌아가는가
- graph가 recommendation/relationship 질의에서 baseline 대비 유의미한 개선을 보이는가
