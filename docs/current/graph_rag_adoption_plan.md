# GraphRAG Adoption Plan

작성 기준일: 2026-03-18

## 1. 목적

이 문서는 SafetyCompanion RAG에 GraphRAG를 언제, 어떤 범위로, 어떤 게이트를 통과한 뒤 도입할지 정리한 운영 계획서다.

핵심 원칙은 아래와 같다.

1. GraphRAG는 기본 경로를 대체하지 않는다.
2. GraphRAG는 relationship / multi-hop / cluster summary 성격의 질문에서만 먼저 실험한다.
3. baseline regression이 없을 때만 실험 범위를 넓힌다.

## 2. 현재 상태 요약

현재 기본 경로는 이미 안정적이다.

- 기준 baseline: `baseline_v6`
- mainline retrieval / grounding: 안정
- compare: regression-only 관리 가능
- dummy multi-page hard slice: 최근 반복에서 닫힘

반면 현재 graph 구현은 아직 운영 준비 상태가 아니다.

- [entity_extractor.py](/D:/vscode/safetycompanion/src/graph/entity_extractor.py):
  엔트리를 거의 그대로 node로 승격
- [relation_extractor.py](/D:/vscode/safetycompanion/src/graph/relation_extractor.py):
  `section_l1` 기반의 얕은 relation만 생성
- [graph_retriever.py](/D:/vscode/safetycompanion/src/graph/graph_retriever.py):
  `provenance_text` substring 매칭 수준

즉, 현재 graph track는 “기능 골격” 수준이지 운영 가능한 GraphRAG는 아니다.

## 3. 도입 이유와 제약

GraphRAG는 장기적으로 아래 질문군에 가치가 있다.

- 특정 topic에 속한 관련 엔트리 묶음
- standard / dummy family / organization 간 관계 탐색
- multi-hop relation 기반 secondary expansion
- corpus-wide theme / topic map 요약

하지만 지금 바로 기본 경로에 넣으면 아래 위험이 있다.

1. 기본 retrieval/grounding과 graph 기여가 섞여 원인 분리가 어려워진다.
2. 현재 graph 코드가 너무 단순해 false-positive relation이 섞일 수 있다.
3. backfill 없는 graph answer는 grounding 규칙을 약화시킬 수 있다.

따라서 GraphRAG는 별도 실험 트랙으로 도입하고, 기본 경로에 섞지 않는다.

## 4. 단계별 도입 범위

### Phase G0. 계획 및 계측

목표:
- graph 실험 전용 hard set과 평가 포맷을 고정

산출물:
- `data/eval/graph_hard_questions.jsonl`
- `outputs/<run_id>/graph_eval.md`
- `outputs/<run_id>/graph_failure_cases.jsonl`

### Phase G1. Minimal Graph Index

목표:
- 현재 구조화 데이터에서 의미 있는 최소 graph를 생성

권장 node:
- `Entry`
- `Topic`
- `DummyFamily`
- `Standard`
- `Organization`

권장 edge:
- `BELONGS_TO_TOPIC`
- `MENTIONS_STANDARD`
- `MENTIONS_DUMMY`
- `MENTIONS_ORG`
- `RELATED_TO_ENTRY`

### Phase G2. Relationship Route 전용 Graph Retrieval

목표:
- `relationship_query`에서만 graph retrieval 사용

초기 허용 질문:
- “A와 B의 관계”
- “같이 언급되는 엔트리”
- “어떤 topic에 속한 세미나/지식 페이지”
- “특정 standard / dummy family와 연관된 엔트리”

즉, G2 초기 범위는 `direct relation lookup`까지만 지원한다.

금지:
- 일반 `seminar_lookup`
- 일반 `page_or_index_lookup`
- `abbreviation_lookup`
- `calendar_lookup`
- `compare` 기본 경로 대체
- graph cluster summary
- topic map 설명
- corpus-wide 흐름 요약

### Phase G3. Multi-page Secondary Expansion

목표:
- base retriever가 찾은 seed 뒤에 graph로 secondary candidate를 확장

사용 방식:
1. 기본 retriever가 seed entry/page를 찾음
2. graph가 관련 entry / topic / dummy family를 통해 secondary candidate 제안
3. 최종 답변은 반드시 원문 evidence로 backfill

### Phase G4. Optional Global Graph Summaries

질문 예시:
- “이 카탈로그의 passive safety 학습 흐름을 요약해줘”
- “dummy 관련 topic map을 보여줘”

현재 프로젝트에서는 장기 옵션이다.

## 5. 도입 게이트

아래 조건을 모두 만족할 때만 GraphRAG 구현을 시작한다.

1. 기본 CLI 경로 안정
   - `preflight`, `ingest`, `build-indexes`, `query`, `eval` 정상
2. baseline 회귀 없음
   - latest baseline >= `baseline_v6`
3. regression suite 안정
   - mainline regression 없음
   - compare regression 없음
   - multi-page regression 없음
4. graph 대상 질문군이 별도 eval set으로 분리돼 있을 것
5. graph 산출물이 기본 경로와 분리된 위치에 저장될 것

## 6. 구현 원칙

### 6.1 기본 경로와 분리

- 기본 경로: `configs/prod.yaml`
- graph 실험 경로: [exp_graph.yaml](/D:/vscode/safetycompanion/configs/exp_graph.yaml)

기본 CLI는 graph를 자동 사용하지 않는다.

### 6.2 graph artifact 분리

권장 저장 위치:

- `data/graph/nodes.jsonl`
- `data/graph/edges.jsonl`
- `outputs/<run_id>/graph_schema.md`
- `outputs/<run_id>/graph_eval.md`
- `outputs/<run_id>/graph_failure_cases.jsonl`

### 6.3 route 제한

graph는 아래 route에서만 고려한다.

- `relationship_query`
- `multi_page_lookup` 일부

graph를 아래 route에 바로 붙이지 않는다.

- `abbreviation_lookup`
- `calendar_lookup`
- `page_or_index_lookup`
- `seminar_lookup`
- `compare`

### 6.4 answer 계약 유지

GraphRAG를 붙여도 아래는 유지한다.

- citation 형식 유지
- grounded answer는 source page 기반이어야 함
- graph가 찾은 candidate도 원문 evidence로 backfill되어야 함

## 7. 평가 설계

### 7.1 필수 질문군

`graph_hard_questions.jsonl`에는 최소 아래 유형이 있어야 한다.

- dummy family relation
- standard-topic relation
- organization-entry relation
- topic cluster relation

초기 G0에서는 위 4유형만 유지한다.

### 7.2 필수 지표

- `graph_route_top1_hit_rate`
- `graph_route_top3_hit_rate`
- `graph_augmented_secondary_page_hit_rate`
- `graph_grounded_success_rate`
- `graph_backfill_success_rate`
- `graph_regression_on_mainline`

### 7.3 승격 기준

GraphRAG를 다음 단계로 승격하려면 아래를 만족해야 한다.

- graph route의 특정 질문군에서 baseline 대비 개선
- mainline route regression 없음
- citation 품질 저하 없음
- graph failure가 explainable taxonomy로 남음

## 8. 실행 순서

### Step G1
- graph hard set 작성
- graph eval/report 포맷 작성
- graph artifact 경로 고정

### Step G2
- node / edge schema 강화
- 최소 shallow graph 생성기 개선

### Step G3
- `relationship_query`에 graph retriever 연결
- graph result -> source entry/page backfill 구현

### Step G4
- `multi_page_lookup`의 secondary expansion에 graph 보조 적용
- graph on/off A/B 비교

### Step G5
- 충분한 개선이 확인될 때만 `prod` 승격 검토

## 9. 브랜치 전략

권장 브랜치 흐름:

1. `codex/graphrag-plan`
2. `codex/graphrag-minimal-graph`
3. `codex/graphrag-relationship-route`
4. `codex/graphrag-multipage-expansion`

각 단계는 stacked PR로 유지하는 편이 안전하다.

## 10. 지금 당장 하지 말아야 할 것

- graph를 기본 query 경로에 바로 연결
- graph candidate를 원문 backfill 없이 답변에 직접 사용
- LLM relation extraction을 baseline 없이 먼저 도입
- global graph summary를 먼저 구현
- `Instructor` node를 G1에 먼저 추가

## 11. 최종 결론

지금 SafetyCompanion 프로젝트에서 GraphRAG는 “당장 필요한 기본 기능”이 아니라, 안정된 baseline 위에서 relationship / multi-hop / graph-assisted expansion을 실험하는 다음 단계다.

따라서 현재 최적 전략은 아래 순서다.

1. baseline_v6 유지
2. graph hard set 분리
3. minimal graph index 구축
4. relationship route부터 제한 도입
5. mainline regression 없을 때만 multi-page 보조로 확장
