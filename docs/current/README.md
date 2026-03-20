# Current Managed Docs

이 폴더는 현재 운영에 직접 영향을 주는 핵심 문서를 별도로 관리하기 위한 공간이다. 아래 문서들은 코드 변경 시 우선적으로 함께 검토해야 하는 “운영 기준 문서”다.

## 포함 문서

- `cli_reference.md`
- `ops_playbook.md`
- `data_contract.md`
- `acceptance_criteria.md`
- `aux_parser_experiment.md`
- `rag_upgrade_strategy.md`
- `graph_rag_adoption_plan.md`
- `graph_eval_contract.md`
- `minimal_graph_schema.md`
- `graph_failure_taxonomy.md`
- `parser_odl_adoption_plan.md`
- `page_type_aware_parser_dispatch.md`

## 관리 원칙

- CLI 인터페이스가 바뀌면 `cli_reference.md`를 갱신한다.
- 운영 절차나 재실행 규칙이 바뀌면 `ops_playbook.md`를 갱신한다.
- 데이터 필드, manifest, citation 규칙이 바뀌면 `data_contract.md`를 갱신한다.
- 품질 게이트나 baseline 기준이 바뀌면 `acceptance_criteria.md`를 갱신한다.
- 보조 파서 실험 범위나 실행 방식이 바뀌면 `aux_parser_experiment.md`를 갱신한다.
- 중장기 RAG 개선 방향과 우선순위가 바뀌면 `rag_upgrade_strategy.md`를 갱신한다.
- GraphRAG 도입 게이트나 단계별 범위가 바뀌면 `graph_rag_adoption_plan.md`를 갱신한다.
- graph eval/report 포맷이 바뀌면 `graph_eval_contract.md`를 갱신한다.
- graph node/edge/provenance 규칙이 바뀌면 `minimal_graph_schema.md`를 갱신한다.
- graph 실패 분류 체계가 바뀌면 `graph_failure_taxonomy.md`를 갱신한다.
- ODL 도입 정책이 바뀌면 `parser_odl_adoption_plan.md`를 갱신한다.
- page-type-aware parser dispatch 규칙이 바뀌면 `page_type_aware_parser_dispatch.md`를 갱신한다.

## 해석 우선순위

현재 운영 문서를 읽을 때는 이 폴더를 `docs/` 루트의 일반 스펙 문서보다 우선한다.
