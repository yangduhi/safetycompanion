# Phase 3D-2 Execution Guide

## 목표
dummy anchor 강화와 multi-page grouping refinement를 통해 남아 있는 hard slice를 줄인다.

## 이번 반복의 범위
1. dummy anchor canonicalization v2
2. co-occurrence 기반 group score
3. page-role 중심 multi-page answer
4. taxonomy v3
5. multi-page hard set 분리

## 성공 기준
- `MULTI_PAGE_COLLAPSE__DUMMY_TOPIC_MERGE_FAIL` 감소
- `ANCHOR_NORMALIZATION_FAIL` 감소
- multi-page answer에 page role이 항상 포함
