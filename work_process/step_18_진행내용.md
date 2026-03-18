# Step 18. GraphRAG Phase G1 Minimal Graph Index

## 목표
기본 경로와 분리된 graph artifact를 생성하고, G2에서 사용할 최소 node / edge / provenance 기반을 마련한다.

## 선행조건
- `step_17_진행내용.md` 완료
- `graph_hard_questions.jsonl` validation 통과
- `configs/exp_graph.yaml` 존재

## 핵심 판단
1. G1에서는 graph retrieval을 query 경로에 연결하지 않는다.
2. G1의 목적은 `nodes.jsonl`, `edges.jsonl`, `graph_schema.md`를 안정적으로 만드는 것이다.
3. graph는 `Entry`, `Topic`, `DummyFamily`, `Standard`, `Organization`만 포함하는 얕은 schema로 시작한다.

## 필수 작업
1. graph node extractor 구현
2. graph relation extractor 구현
3. `build-indexes --config configs/exp_graph.yaml`에서 graph artifact 생성
4. graph schema report 생성
5. graph build 테스트 추가

## 산출물
- `data/graph/nodes.jsonl`
- `data/graph/edges.jsonl`
- `outputs/<run_id>/graph_schema.md`
- `docs/branches/codex__graphrag-minimal-graph/phase_g1_execution_guide.md`

## 완료 기준
- graph artifact 생성 성공
- provenance 필드 누락 없음
- `pytest -q` 통과
- `build-indexes --config configs/exp_graph.yaml` 통과
