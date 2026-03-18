# Dummy Seed Priority Spec

## Goal
dummy multi-page query에서 그룹 대표 페이지를 더 안정적으로 고른다.

## Query Modes
- `landscape`
  - `dummy landscape`, `current dummy landscape` 중심
- `specific_anchor`
  - `THOR`, `HIII`, `ATD` 같이 특정 더미 family 중심
- `mixed`
  - specific anchor와 generic dummy가 함께 있는 경우
- `training`
  - dummy training/seminar를 명시한 경우
- `generic_dummy`
  - 더미 일반 페이지 묶음

## Seed Heuristics
- `specific_anchor`
  - `spec_page`, `detail_page` 우선
  - `landscape_page`는 명시적 landscape 표현이 없으면 감점
- `landscape`
  - `landscape_page` 우선
  - `training_page`는 seed로 감점
- `mixed`
  - `spec_page`와 `landscape_page`를 모두 강하게 본다

## Strong Penalties
- `NCAP` intrusion
- unrelated seminar/training seed
- reference/index page seed
