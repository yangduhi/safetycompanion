# Improvement Plan V2

## 핵심 판단 목록
1. 현재 baseline은 retrieval 자체보다 citation grounding과 answer composition이 더 큰 병목이다.
2. 다음 반복의 1순위는 `baseline freeze + evaluator decouple`이다.
3. field-grounded answer와 span-level evidence extraction이 가장 ROI가 크다.
4. retrieval 개선은 전체 재설계보다 top-1/top-3 precision과 reranker hard-negative tuning에 집중한다.
5. parser/extractor 고도화는 GraphRAG보다 먼저 진행한다.
6. GraphRAG는 citation/grounding이 0.90 근처까지 안정화된 뒤에만 시작한다.

## 단계별 계획

### Phase 1. Baseline Freeze + Evaluator Decouple
- 현재 baseline을 `baseline_v1`로 고정
- easy / medium / hard difficulty 분리
- retrieval / citation / grounding 지표를 분리 기록
- top-1 / top-3 / top-10 기준을 별도 리포트화

완료 기준:
- baseline snapshot 문서 1개
- retrieval report / citation report / grounding report 분리
- hard-set 결과를 따로 확인 가능

### Phase 2. Citation / Grounding 집중 개선
- field-grounded answer 선택 계층 추가
- citation policy 강화
- span-level evidence 저장

완료 기준:
- citation page hit rate 개선
- grounded success rate 개선
- evidence field 추적 가능

### Phase 3. Retrieval 정밀화
- top-1 / top-3 precision 개선
- reranker hard-negative tuning
- exact keyword / page type prior / abbreviation strong signal 반영

완료 기준:
- retrieval top-1 / top-3 개선
- hard-negative 혼동군 분리 가능

### Phase 4. Error Taxonomy 구축
- parser / lookup / rerank / answer generation 오류를 수동+자동 분류
- 실패 30~50개 케이스를 유형별 집계

완료 기준:
- 오류 taxonomy 리포트
- 개선 우선순위의 근거 수치화

### Phase 5. Parser / Extractor 고도화
- 표형 페이지 처리 개선
- field boundary confidence 저장
- parser disagreement log 추가

완료 기준:
- 표형 페이지와 semi-structured 페이지의 구조화 정확도 개선
- field boundary 추적 가능

### Phase 6. Small GraphRAG
- baseline과 분리된 선택형 경로로만 도입
- 관계형/추천형 질의에만 제한 적용

착수 조건:
- citation page hit rate >= 0.90
- grounded success rate >= 0.90

### Phase 7. 운영 고도화
- query observability 강화
- stable / experimental config 분리 유지
- regression gate 자동화
- latency / cost profiling 추가
