# Phase 2 Execution Guide

## 목표
현재 baseline에서 가장 큰 병목인 citation / grounding / answer composition 계층을 강화한다.

## 이번 반복의 범위
1. span-level evidence 저장
2. route별 field priority policy 고정
3. compare / recommendation 최소 2근거 강제
4. abbreviation deterministic grounding
5. route-aware candidate filtering

## 구현 순서
1. `configs/route_field_priority.yaml` 작성 및 정책 로더 추가
2. retrieval service에서 route별 코퍼스/후보 필터링 적용
3. answer generator에서 route별 evidence selection과 span 추출 적용
4. abbreviation route의 deterministic answer template 적용
5. compare / recommendation guardrail 적용
6. evaluator와 CSV 리포트에 새 메타데이터 반영

## 필수 산출물
- `docs/evidence_policy.md`
- `docs/span_grounding_spec.md`
- `docs/abbreviation_route_spec.md`
- `docs/compare_recommendation_guardrails.md`
- `configs/route_field_priority.yaml`

## 리포트 필수 컬럼
- `route_name`
- `selected_field`
- `evidence_count`
- `span_present`
- `template_answer_used`
- `multi_page_used`

## 성공 기준
- abbreviation route는 deterministic answer 사용 시 source title과 page를 항상 포함
- compare / recommendation은 최소 2 근거가 없으면 보수 응답
- grounding details에서 span 누락 여부를 확인 가능
- citation / grounding 지표가 baseline_v1 이상 유지 또는 개선
