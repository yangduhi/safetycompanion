# Task Checklist

## 사용 규칙
- 각 항목은 완료 시 체크한다.
- 차단 이슈가 생기면 `outputs/<run_id>/blocking_issues.md`에 기록한다.
- 미결정 항목은 `spec.md`의 결정 등록부 상태를 먼저 확인한다.

## Phase 0. Preflight
- [ ] `data/SafetyCompanion-2026.pdf` 존재 확인
- [ ] `python --version` 통과
- [ ] `pdfinfo data/SafetyCompanion-2026.pdf` 통과
- [ ] `pdftotext -f 1 -l 1 data/SafetyCompanion-2026.pdf -` 통과
- [ ] `outputs/<run_id>/preflight_report.md` 작성

## Phase 1. 원본 감사
- [ ] `docs/source_document_profile.md` 작성
- [ ] `docs/rag_scope.md` 작성
- [ ] `data/raw/source_page_map.jsonl` 작성
- [ ] `outputs/<run_id>/source_audit_report.md` 작성
- [ ] `pdf_page`/`printed_page` 정책 확정

## Phase 2. 저장소 계약 고정
- [ ] `README.md` 최신화
- [ ] `spec.md` 최신화
- [ ] `plan.md` 최신화
- [ ] `tasks.md` 최신화
- [ ] `configs/project.yaml` 작성
- [ ] `docs/data_contract.md` 작성
- [ ] `docs/acceptance_criteria.md` 작성
- [ ] `docs/run_manifest.schema.json` 작성
- [ ] `data/eval/gold_questions.jsonl` 작성

## Phase 3. PDF 구조 복원
- [ ] `data/parsed/page_manifest.jsonl` 생성
- [ ] `data/parsed/page_blocks.jsonl` 생성
- [ ] `outputs/<run_id>/parse_report.md` 생성
- [ ] `outputs/<run_id>/page_review_queue.json` 생성
- [ ] `notebooks/01_parse_inspection.ipynb` 준비
- [ ] page manifest coverage == 224 확인

## Phase 4. 엔트리 및 보조 데이터셋 추출
- [ ] `data/processed/entries.jsonl` 생성
- [ ] `data/processed/abbreviations.jsonl` 생성
- [ ] `data/processed/back_index.jsonl` 생성
- [ ] `data/processed/calendar_entries.jsonl` 생성
- [ ] `data/processed/page_links.jsonl` 생성
- [ ] `outputs/<run_id>/extraction_quality_report.md` 생성
- [ ] 다중 엔트리/연속 페이지 bundle 검증

## Phase 5. 청킹 및 인덱스 구축
- [ ] `data/processed/chunks.jsonl` 생성
- [ ] `indexes/dense_entry/` 생성
- [ ] `indexes/dense_field/` 생성
- [ ] `indexes/bm25/` 생성
- [ ] `indexes/lookup/` 생성
- [ ] `outputs/<run_id>/index_build_manifest.json` 생성
- [ ] `outputs/<run_id>/retrieval_smoke_test.md` 생성

## Phase 6. QA 계층 구축
- [ ] `src/retrieval/router.py` 구현
- [ ] `src/retrieval/fusion.py` 구현
- [ ] `src/retrieval/reranker.py` 구현
- [ ] `src/qa/answer_generator.py` 구현
- [ ] `outputs/<run_id>/query_traces/` 생성
- [ ] `outputs/<run_id>/grounded_answer_samples.md` 생성
- [ ] `tests/test_grounding.py` 작성
- [ ] `tests/test_query_routing.py` 작성

## Phase 7. 평가 및 판정
- [ ] `src/eval/parse_eval.py` 구현
- [ ] `src/eval/extraction_eval.py` 구현
- [ ] `src/eval/retrieval_eval.py` 구현
- [ ] `src/eval/answer_eval.py` 구현
- [ ] `data/eval/adversarial_questions.jsonl` 작성
- [ ] `outputs/<run_id>/eval_summary.md` 생성
- [ ] `outputs/<run_id>/error_analysis.csv` 생성
- [ ] `outputs/<run_id>/failure_cases.jsonl` 생성
- [ ] Step 7 gate 통과 여부 기록

## Phase 8. 운영형 CLI 및 재현 실행 경로
- [ ] `src/main.py` 구현
- [ ] `configs/prod.yaml` 작성
- [ ] `docs/ops_playbook.md` 작성
- [ ] `docs/cli_reference.md` 작성
- [ ] `outputs/<run_id>/run_manifest.json` 생성
- [ ] 표준 검증 명령 실행

## Phase 9. 선택형 GraphRAG
- [ ] graph track 사용 여부 결정 확인
- [ ] `src/graph/entity_extractor.py` 구현
- [ ] `src/graph/relation_extractor.py` 구현
- [ ] `src/graph/graph_builder.py` 구현
- [ ] `src/graph/graph_retriever.py` 구현
- [ ] `configs/exp_graph.yaml` 작성
- [ ] `data/graph/nodes.jsonl` 생성
- [ ] `data/graph/edges.jsonl` 생성
- [ ] `outputs/<run_id>/graph_schema.md` 생성
- [ ] `outputs/<run_id>/graph_samples.md` 생성

## 차단 항목
- [ ] 미결정 사용자 항목 없음
- [ ] baseline gate 미통과 상태에서 Phase 8 이상으로 진행하지 않음
