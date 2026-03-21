# Step 23 진행내용

## 목표

- ODL parser lane를 whitelist 실험으로 좁혀 local/hybrid를 비교한다.
- Graph `entity_relation_lookup`에서 `Euro NCAP` exact entity 대표성을 강화한다.

## 수행 내용

### 1. ODL whitelist 비교

- 추가 config:
  - `configs/exp_parser_odl_whitelist_hybrid.yaml`
- 실행:
  - whitelist local ingest/build-indexes/eval
  - whitelist hybrid ingest/build-indexes/eval
- 결과 정리 문서:
  - `docs/current/odl_whitelist_local_vs_hybrid_eval.md`
  - `docs/current/odl_grounding_delta.md`
  - `docs/current/odl_whitelist_page_report.csv`

### 2. Graph Euro NCAP entity lane 보정

- `src/retrieval/service.py`
  - `entity_relation_lookup` + `standard_topic_relation`일 때 대표 summary field 우선순위 재조정
  - `Euro NCAP` exact entity 대표 페이지 boost
  - broad/multi-standard/subtopic page penalty 추가
- 결과 정리 문서:
  - `docs/branches/codex__graphrag-g2s-route-decomposition/entity_relation_euro_ncap_spec.md`

## 핵심 수치

### ODL

- baseline:
  - `grounded_success_rate = 1.0`
  - `multi_page_hard__grounded_success_rate = 0.6667`
  - `GROUNDING_POLICY_FAIL = 4`
- ODL full local:
  - reparsed `127` pages
  - `grounded_success_rate = 1.0`
  - `GROUNDING_POLICY_FAIL = 4`
- ODL whitelist local:
  - reparsed `7` pages
  - `grounded_success_rate = 1.0`
  - `GROUNDING_POLICY_FAIL = 4`
- ODL whitelist hybrid:
  - reparsed `0` pages
  - hybrid CLI 실패 후 `pdftotext` fallback
  - `grounded_success_rate = 1.0`
  - `GROUNDING_POLICY_FAIL = 4`

### Graph

Targeted query snapshot after Euro NCAP tuning:

1. `Euro NCAP UpDate 2026 Get ready for Euro NCAP‘s latest rating revision!`
2. `Euro NCAP - Compact Course Description Course Contents`
3. `Wissen SafetyWissen.com Euro NCAP / ANCAP Frontal Impact Test Matrix`

## 결론

- ODL는 whitelist lane로 통제 가능한 parser 실험이 됐다.
- 현재 aggregate grounding 기준으로는 baseline 대비 개선/악화가 보이지 않는다.
- `GROUNDING_POLICY_FAIL: 4`는 ODL가 만든 신규 문제가 아니라 baseline에도 존재한다.
- Graph `entity_relation_lookup`은 `Euro NCAP` representative ranking이 이전보다 representative page 쪽으로 이동했다.

## 다음 단계

1. ODL:
   - whitelist 페이지별 field boundary / table extraction 품질을 개별 점검
2. Graph:
   - `Passive Safety`
   - `Automated Driving`
   topic representative ranking 보정
3. `G3`는 계속 보류
