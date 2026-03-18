# Dummy Grouping Refinement Spec

## 목표
dummy / THOR / HIII / ATD / landscape 계열 multi-page 질의의 top-1 grouping coherence를 높인다.

## 핵심 축
- seed page priority
- secondary page compatibility
- role combination scoring
- unrelated intrusion penalty

## role 조합 원칙
- `landscape + spec` 조합은 강한 positive signal
- `landscape + training`은 보조 signal
- `criteria + spec` 조합은 strong signal
- `overview + detail`은 generic positive
- unrelated seminar / event page는 strong penalty
