# Multi Page Grouping Spec

## 목표
multi-page 질의에서 entry보다 page-group을 먼저 안정화한다.

## 정책
- multi-page route는 top-n page candidate를 먼저 고른다
- page-group은 topic cohesion / anchor overlap / section continuity를 반영한다
- near-duplicate page는 dedup한다
- 응답 순서:
  1. 관련 페이지 목록
  2. 각 페이지 역할
  3. 통합 요약
