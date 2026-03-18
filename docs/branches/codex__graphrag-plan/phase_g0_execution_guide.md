# Phase G0 Execution Guide

## 목적
GraphRAG 구현 전에 질문셋, 평가 계약, 최소 graph schema, failure taxonomy를 고정한다.

## 범위
- `graph_hard_questions.jsonl` 작성
- graph eval/report 계약 정의
- minimal graph schema 정의
- graph failure taxonomy 정의
- 최소 검증 코드와 테스트 추가

## 비범위
- graph retriever를 query 경로에 연결하지 않음
- graph answer를 직접 생성하지 않음
- multi-page secondary expansion에 graph를 연결하지 않음

## 성공 기준
- hard set validation 통과
- graph eval contract 문서 완성
- minimal graph schema 문서 완성
- graph failure taxonomy 문서 완성
- `pytest -q` 통과
