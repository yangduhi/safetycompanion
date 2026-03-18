# Phase 3 Execution Guide

## 목표
top-1 precision과 citation 정밀도를 높이기 위해 retrieval 상위 선택 계층을 강화한다.

## 이번 반복의 범위
1. reranker hard-negative 구축
2. page/title disambiguation scorer 추가
3. Korean normalization + bilingual bridge
4. multi-page retrieval policy
5. route-aware corpus isolation v2

## 성공 기준
- `retrieval_top1_hit_rate` 개선
- `citation_top1_hit_rate` 개선
- 한국어 질의군의 별도 성능 확인 가능
- multi-page / recommendation 질의군의 별도 성능 확인 가능
