# Step 19. GraphRAG Phase G2 Relationship Route + Backfill

## 목표
`relationship_query`에서만 graph retrieval을 사용하고, graph hit를 반드시 원문 entry/page evidence로 backfill한다.

## 선행조건
- `step_18_진행내용.md` 완료
- `data/graph/nodes.jsonl`, `data/graph/edges.jsonl` 생성 성공
- `configs/exp_graph.yaml`에서 graph artifact 생성 확인

## 핵심 판단
1. G2 초기 범위는 `direct relation lookup`까지만 지원한다.
2. graph는 후보 탐색만 담당하고, 최종 답변은 원문 evidence를 사용한다.
3. 기본 `prod` 경로에는 graph를 자동 사용하지 않는다.

## 필수 작업
1. relationship route detection 강화
2. graph node/edge 매칭 기반 entry candidate 회수
3. graph candidate -> entry chunk backfill 구현
4. graph eval / graph failure report 생성
5. graph route 테스트 추가

## 산출물
- `docs/branches/codex__graphrag-relationship-route/phase_g2_execution_guide.md`
- `outputs/<run_id>/graph_eval.md`
- `outputs/<run_id>/graph_route_details.csv`
- `outputs/<run_id>/graph_failure_cases.jsonl`

## 완료 기준
- `relationship_query`가 graph hard set에서 동작
- graph backfill success 확인
- mainline regression 없음
- `pytest -q` 통과
