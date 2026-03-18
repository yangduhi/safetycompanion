# Docs Guide

이 디렉터리는 SafetyCompanion 프로젝트의 운영 문서, 구현 참조 스펙, 과거 실험 기록을 함께 담고 있다. 현재는 핵심 운영 문서를 `docs/current/`로 분리해 관리하고, 나머지 문서는 참조 스펙 또는 히스토리 문서로 해석한다.

## 읽는 순서

현재 프로젝트를 이해하거나 수정할 때는 아래 순서를 권장한다.

1. [README.md](/D:/vscode/safetycompanion/README.md)
2. [spec.md](/D:/vscode/safetycompanion/spec.md)
3. [plan.md](/D:/vscode/safetycompanion/plan.md)
4. [tasks.md](/D:/vscode/safetycompanion/tasks.md)
5. [docs/current/README.md](/D:/vscode/safetycompanion/docs/current/README.md)
6. [docs/current/cli_reference.md](/D:/vscode/safetycompanion/docs/current/cli_reference.md)
7. [docs/current/ops_playbook.md](/D:/vscode/safetycompanion/docs/current/ops_playbook.md)
8. [docs/current/data_contract.md](/D:/vscode/safetycompanion/docs/current/data_contract.md)
9. [docs/current/acceptance_criteria.md](/D:/vscode/safetycompanion/docs/current/acceptance_criteria.md)
10. [docs/current/rag_upgrade_strategy.md](/D:/vscode/safetycompanion/docs/current/rag_upgrade_strategy.md)
11. [docs/DOC_STATUS.md](/D:/vscode/safetycompanion/docs/DOC_STATUS.md)

## 현재 유효한 문서

현재 유효한 문서는 두 부류다.

- 운영 기준 문서:
  현재 코드와 실행 경로를 직접 설명하는 문서
- 구현 참조 스펙:
  현재 코드에 반영된 정책이나 휴리스틱을 세부 설명하는 문서

대표 운영 기준 문서:

- [docs/current/cli_reference.md](/D:/vscode/safetycompanion/docs/current/cli_reference.md)
- [docs/current/ops_playbook.md](/D:/vscode/safetycompanion/docs/current/ops_playbook.md)
- [docs/current/data_contract.md](/D:/vscode/safetycompanion/docs/current/data_contract.md)
- [docs/current/acceptance_criteria.md](/D:/vscode/safetycompanion/docs/current/acceptance_criteria.md)
- [docs/run_manifest.schema.json](/D:/vscode/safetycompanion/docs/run_manifest.schema.json)

대표 구현 참조 스펙:

- [docs/evidence_policy.md](/D:/vscode/safetycompanion/docs/evidence_policy.md)
- [docs/compare_recommendation_guardrails.md](/D:/vscode/safetycompanion/docs/compare_recommendation_guardrails.md)
- [docs/multi_page_policy.md](/D:/vscode/safetycompanion/docs/multi_page_policy.md)
- [docs/route_corpus_isolation_v2.md](/D:/vscode/safetycompanion/docs/route_corpus_isolation_v2.md)
- [docs/multi_page_grouping_spec_v3.md](/D:/vscode/safetycompanion/docs/multi_page_grouping_spec_v3.md)
- [docs/taxonomy_v3_spec.md](/D:/vscode/safetycompanion/docs/taxonomy_v3_spec.md)

## 히스토리 문서

히스토리 문서는 아래 성격 중 하나에 해당한다.

- 과거 단계별 실행 가이드
- 현행 버전으로 대체된 구버전 스펙
- 특정 브랜치에서만 의미가 있는 작업 기록
- 과거 baseline snapshot

대표 히스토리 문서:

- `phase*_execution_guide.md`
- `*_v2.md` 중 현행 상위 버전으로 대체된 문서
- [docs/improvement_plan_v2.md](/D:/vscode/safetycompanion/docs/improvement_plan_v2.md)
- [docs/baselines/baseline_v1.md](/D:/vscode/safetycompanion/docs/baselines/baseline_v1.md) ~ [docs/baselines/baseline_v4.md](/D:/vscode/safetycompanion/docs/baselines/baseline_v4.md)
- [docs/branches](/D:/vscode/safetycompanion/docs/branches) 아래 브랜치 전용 산출물

히스토리 문서는 삭제 대상이 아니라, 과거 판단 배경과 실험 이력을 보존하는 참고 자료다. 다만 현재 구현의 동작 여부를 판단할 때는 1차 기준으로 사용하지 않는다.

## Baseline 문서 해석

- [docs/baselines/baseline_v5.md](/D:/vscode/safetycompanion/docs/baselines/baseline_v5.md):
  현재 기준선으로 참고하는 최신 frozen snapshot
- `baseline_v1` ~ `baseline_v4`:
  과거 반복의 비교용 히스토리 snapshot

## 브랜치 문서 해석

[docs/branches](/D:/vscode/safetycompanion/docs/branches)는 브랜치별 실험 기록과 브랜치 전용 baseline을 담는 공간이다. 기본적으로 현재 운영 기준 문서가 아니라, 작업 문맥 복원용 보조 자료로 본다.

## 최종 기준

문서 간 설명이 충돌하면 아래 우선순위를 따른다.

1. 루트 문서: `README.md`, `spec.md`, `plan.md`, `tasks.md`
2. 운영 문서: `docs/current/cli_reference.md`, `docs/current/ops_playbook.md`, `docs/current/data_contract.md`, `docs/current/acceptance_criteria.md`
3. 현재 유효 참조 스펙
4. 히스토리 문서
