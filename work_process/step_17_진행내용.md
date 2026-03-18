# Step 17. GraphRAG Phase G0 계획 및 계측 고정

## 목표
GraphRAG를 기본 경로와 분리된 실험 트랙으로 도입하기 위해, 구현 전에 질문셋·평가 계약·최소 graph schema·failure taxonomy를 고정한다.

## 선행조건
- `baseline_v6` 확보
- mainline regression 없음
- compare regression 없음
- multi-page regression 없음

## 핵심 판단
1. GraphRAG는 아직 본선 기능이 아니라 experimental lane이다.
2. 지금 바로 graph retrieval을 기본 query 경로에 연결하지 않는다.
3. G0에서는 구현보다 계약과 계측을 먼저 고정한다.

## 필수 작업
1. `data/eval/graph_hard_questions.jsonl` 초안 작성
2. graph eval / report 계약 문서화
3. minimal graph schema 문서화
4. graph failure taxonomy 문서화
5. 질문셋 계약을 검증하는 최소 코드와 테스트 추가

## 산출물
- `docs/current/graph_rag_adoption_plan.md`
- `docs/current/graph_eval_contract.md`
- `docs/current/minimal_graph_schema.md`
- `docs/current/graph_failure_taxonomy.md`
- `docs/branches/codex__graphrag-plan/phase_g0_execution_guide.md`
- `data/eval/graph_hard_questions.jsonl`
- `src/eval/graph_eval.py`
- `tests/test_graph_g0.py`

## 완료 기준
- graph hard set이 유효한 스키마로 저장됨
- graph eval 계약이 문서로 고정됨
- minimal graph schema와 provenance 규칙이 문서화됨
- graph failure taxonomy가 분리 정의됨
- 관련 테스트 통과
