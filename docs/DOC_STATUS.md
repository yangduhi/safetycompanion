# Document Status

이 문서는 `docs/` 아래 문서의 현재 상태를 정리한 색인이다.

상태 정의:

- `Current`:
  현재 코드와 운영 기준에 직접 연결된 문서
- `History`:
  과거 단계, 구버전 스펙, 이전 baseline, 브랜치 전용 기록

현재 운영 문서는 혼선을 줄이기 위해 `docs/current/` 아래에 별도 보관한다.

## Current

| 문서 | 역할 |
|---|---|
| `current/acceptance_criteria.md` | 현재 품질 게이트와 운영 readiness 기준 |
| `current/cli_reference.md` | 현재 CLI 명령과 산출물 계약 |
| `current/data_contract.md` | 현재 데이터셋과 manifest 계약 |
| `current/ops_playbook.md` | 현재 운영/재실행/장애 대응 가이드 |
| `current/README.md` | 핵심 운영 문서 관리 규칙 |
| `current/rag_upgrade_strategy.md` | 현재 구조 기준의 RAG 고도화 전략 문서 |
| `run_manifest.schema.json` | run manifest 스키마 |
| `git_workflow.md` | 저장소 작업 흐름 참고 |
| `source_document_profile.md` | 입력 PDF의 특성 메모 |
| `rag_scope.md` | 문서 범위와 retrieval 관점 메모 |
| `abbreviation_route_spec.md` | abbreviation route 참조 스펙 |
| `compare_pairing_spec.md` | compare pair selection 참조 스펙 |
| `compare_recommendation_guardrails.md` | compare/recommendation 보수 응답 규칙 |
| `compare_regression_spec.md` | compare slice 회귀 감시 기준 |
| `compare_route_spec.md` | compare route 분리 규칙 |
| `dummy_anchor_spec_v2.md` | dummy anchor 현행 정규화 규칙 |
| `error_taxonomy_spec.md` | 에러 분류 상위 체계 |
| `event_paraphrase_alias_spec.md` | event 질의 alias 처리 규칙 |
| `evidence_policy.md` | evidence 선택과 grounding 정책 |
| `exact_anchor_normalization_spec.md` | exact anchor 정규화 규칙 |
| `hard_negative_spec.md` | hard negative 조정 기준 |
| `hard_route_precision_spec.md` | hard route precision 튜닝 기준 |
| `korean_query_normalization_spec.md` | 한국어 질의 정규화 규칙 |
| `multi_page_dummy_hardset_spec.md` | dummy 계열 hard set 정의 |
| `multi_page_grouping_spec_v3.md` | 현행 multi-page grouping 규칙 |
| `multi_page_hardset_spec.md` | multi-page hard set 정의 |
| `multi_page_policy.md` | multi-page route와 답변 원칙 |
| `page_role_assignment_spec.md` | multi-page 응답의 page role 규칙 |
| `page_title_disambiguation_spec.md` | page title disambiguation 규칙 |
| `route_corpus_isolation_v2.md` | route별 코퍼스 격리 규칙 |
| `span_grounding_spec.md` | span 기반 grounding 규칙 |
| `taxonomy_v3_spec.md` | 현행 세부 taxonomy 확장 규칙 |
| `baselines/baseline_v5.md` | 최신 frozen baseline 스냅샷 |
| `baselines/baseline_v5.json` | 최신 frozen baseline 메트릭 원본 |
| `branches/README.md` | 브랜치 문서 저장 규칙 |

## History

| 문서 | 이유 |
|---|---|
| `improvement_plan_v2.md` | 과거 반복 계획 문서 |
| `dummy_anchor_spec.md` | `dummy_anchor_spec_v2.md`로 대체됨 |
| `multi_page_grouping_spec.md` | `multi_page_grouping_spec_v3.md`로 대체됨 |
| `taxonomy_v2_spec.md` | `taxonomy_v3_spec.md`로 대체됨 |
| `phase2_execution_guide.md` | 구축 단계 실행 가이드 이력 |
| `phase3_execution_guide.md` | 구축 단계 실행 가이드 이력 |
| `phase3b_execution_guide.md` | 구축 단계 실행 가이드 이력 |
| `phase3c_execution_guide.md` | 구축 단계 실행 가이드 이력 |
| `phase3d_execution_guide.md` | 구축 단계 실행 가이드 이력 |
| `phase3d2_execution_guide.md` | 구축 단계 실행 가이드 이력 |
| `baselines/baseline_v1.md` | 과거 baseline snapshot |
| `baselines/baseline_v1.json` | 과거 baseline snapshot |
| `baselines/baseline_v2.md` | 과거 baseline snapshot |
| `baselines/baseline_v2.json` | 과거 baseline snapshot |
| `baselines/baseline_v3.md` | 과거 baseline snapshot |
| `baselines/baseline_v3.json` | 과거 baseline snapshot |
| `baselines/baseline_v4.md` | 과거 baseline snapshot |
| `baselines/baseline_v4.json` | 과거 baseline snapshot |
| `branches/codex__phase3d3-dummy-refinement/phase3d3_execution_guide.md` | 브랜치 전용 작업 기록 |
| `branches/codex__phase3d3-dummy-refinement/dummy_grouping_refinement_spec.md` | 브랜치 전용 실험 스펙 |
| `branches/codex__phase3d3-dummy-refinement/resume_checklist.md` | 브랜치 전용 재개 메모 |
| `branches/codex__phase3d3-dummy-refinement/baselines/baseline_v5.md` | 브랜치 전용 snapshot |
| `branches/codex__phase3d3-dummy-refinement/baselines/baseline_v5.json` | 브랜치 전용 snapshot |

## 분류 규칙

아래에 해당하면 보통 `History`로 분류한다.

- `phase*execution_guide` 계열
- 더 높은 버전 문서에 대체된 구버전 스펙
- 브랜치 전용 폴더 아래 문서
- 최신 기준선보다 오래된 baseline snapshot

반대로 아래는 `Current`로 유지한다.

- 현재 코드 구조와 직접 연결된 운영 문서
- 현재 구현에 반영된 정책/휴리스틱 스펙
- 최신 baseline과 schema 문서
