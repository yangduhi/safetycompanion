# Task Checklist

이 문서는 초기 구축 체크리스트가 아니라, 현재 구현된 프로젝트를 유지·개선하기 위한 운영 체크리스트다.

## 1. 현재 완료된 기반

- [x] `preflight -> ingest -> build-indexes -> query -> eval` 기본 CLI 경로 구현
- [x] `src/cli`, `src/workflows`, `src/common/paths.py` 기반 구조 리팩터링 완료
- [x] `data/parsed`, `data/processed`, `indexes`, `outputs` 산출물 체계 유지
- [x] route policy 기반 retrieval / grounded answer 경로 구현
- [x] evaluation 리포트 및 baseline snapshot 생성 경로 구현
- [x] 테스트 스위트로 routing / grounding / path contract 검증
- [x] 상위 문서와 운영 문서 재정비

## 2. 변경 후 기본 검증 체크리스트

모든 코드 변경 후 최소 아래 항목을 확인한다.

- [ ] `pytest -q`
- [ ] `python -m src.main --help`
- [ ] 변경 범위에 맞는 재실행 단계 결정
- [ ] 필요한 `outputs/<run_id>/...` 산출물 확인
- [ ] 관련 문서 업데이트 여부 확인

## 3. 변경 범위별 재실행 체크

### Parse / Ingest 변경 시

- [ ] `python -m src.main preflight`
- [ ] `python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml`
- [ ] `python -m src.main build-indexes --config configs/prod.yaml`
- [ ] `python -m src.main eval --config configs/prod.yaml`

### Retrieval / Chunking / Index 변경 시

- [ ] `python -m src.main build-indexes --config configs/prod.yaml`
- [ ] 대표 질의 `query` 실행
- [ ] `python -m src.main eval --config configs/prod.yaml`

### Answer / Grounding 정책 변경 시

- [ ] 대표 질의 `query` 실행
- [ ] `python -m src.main eval --config configs/prod.yaml`
- [ ] citation 문구와 `pdf_page` / `printed_page` 표기 확인

### Eval / Reporting 변경 시

- [ ] `python -m src.main eval --config configs/prod.yaml`
- [ ] `eval_summary.md`, `retrieval_report.md`, `grounding_report.md` 확인

## 4. 현재 활성 backlog

- [ ] 인코딩 노이즈가 심한 `knowledge` 페이지의 파싱 품질 개선
- [ ] hard case와 multi-page case의 top-1 안정성 회귀 감시 강화
- [ ] `run_manifest.json`의 `git_commit` 채움 여부 결정 및 구현
- [ ] shared dataset / index와 run-scoped 산출물의 경계 문서화 강화
- [ ] graph track를 기본 경로와 명확히 분리하는 운영 규칙 보강

## 5. 문서 유지보수 체크

- [ ] [README.md](/D:/vscode/safetycompanion/README.md)와 실제 CLI 구조 일치
- [ ] [plan.md](/D:/vscode/safetycompanion/plan.md)와 현재 운영 우선순위 일치
- [ ] [spec.md](/D:/vscode/safetycompanion/spec.md)와 코드 계약 일치
- [ ] [docs/current/cli_reference.md](/D:/vscode/safetycompanion/docs/current/cli_reference.md)와 실제 명령 옵션 일치
- [ ] [docs/current/data_contract.md](/D:/vscode/safetycompanion/docs/current/data_contract.md)와 실제 레코드 필드 일치

## 6. 조건부 트랙

- [ ] graph 실험 필요성 재확인
- [ ] `configs/exp_graph.yaml` 기반 분기만 사용
- [ ] baseline 회귀가 없을 때만 graph 산출물 비교
- [ ] `docs/current/graph_rag_adoption_plan.md` 기준으로 graph hard set 작성
- [ ] minimal graph index schema 정의
- [ ] `relationship_query` 한정 graph backfill 실험
- [ ] `docs/current/graph_eval_contract.md` 기준으로 graph eval/report 포맷 고정
- [ ] `docs/current/graph_failure_taxonomy.md` 기준으로 graph 실패 분류 분리
