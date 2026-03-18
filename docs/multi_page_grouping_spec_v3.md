# Multi Page Grouping Spec V3

## 목표
multi-page 질의에서 seed page를 고정하고, 관련 secondary page를 coherence 기준으로 추가한다.

## 정책
1. seed page 확정
2. secondary page 후보 수집
3. page role assignment
4. near-duplicate 제거
5. final group freeze
6. answer generation

## group score 구성 예시
- `anchor_match_score`
- `co_occurrence_score`
- `section_cohesion_score`
- `dummy_topic_prior`
- `duplicate_penalty`
- `unrelated_intrusion_penalty`
