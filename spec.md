# Specification

## 1. 목적

이 프로젝트의 목적은 `data/SafetyCompanion-2026.pdf`를 구조화 데이터로 복원하고, 그 위에서 하이브리드 검색과 근거 기반 답변을 제공하는 재현 가능한 CLI 시스템을 운영하는 것이다.

현재 기본 경로는 다음을 포함한다.

- PDF 파싱과 페이지 분류
- 엔트리, 약어, 색인, 캘린더 추출
- 청킹과 인덱스 구축
- 질의 라우팅과 검색
- grounded answer 생성
- 평가 리포트와 baseline snapshot 생성

## 2. 구현 범위

기본 구현 범위:

- [src/parse](/D:/vscode/safetycompanion/src/parse)
- [src/ingest](/D:/vscode/safetycompanion/src/ingest)
- [src/retrieval](/D:/vscode/safetycompanion/src/retrieval)
- [src/qa](/D:/vscode/safetycompanion/src/qa)
- [src/eval](/D:/vscode/safetycompanion/src/eval)
- [src/cli](/D:/vscode/safetycompanion/src/cli)
- [src/workflows](/D:/vscode/safetycompanion/src/workflows)

조건부 범위:

- [src/graph](/D:/vscode/safetycompanion/src/graph) 기반 graph 실험 경로
- 외부 서비스 연동 실험

기본 범위에서 제외:

- 사용자 승인 없는 외부 API 의존
- 광고성 페이지를 일반 retrieval 근거로 사용하는 기능
- graph 경로를 기본 CLI에 강제 포함하는 변경

## 3. 문서 우선순위

현재 기준 문서 우선순위는 아래와 같다.

1. `spec.md`
2. `plan.md`
3. `tasks.md`
4. `docs/current/cli_reference.md`
5. `docs/current/ops_playbook.md`
6. `docs/current/data_contract.md`
7. `docs/current/acceptance_criteria.md`

`work_process/` 문서는 구축 과정의 기록이며, 현재 운영 규칙의 1차 기준은 아니다.

## 4. 환경 계약

작업 기준 환경:

- OS: Windows + PowerShell
- 작업 루트: `D:\vscode\safetycompanion`
- Python: `>= 3.11`

필수 도구:

- `python`
- `pdfinfo`
- `pdftotext`

선택 도구:

- `pdftoppm`
- `uv`
- OCR 도구
- 외부 LLM 또는 외부 reranker API

기본 의존성은 [pyproject.toml](/D:/vscode/safetycompanion/pyproject.toml)에 정의한다.

## 5. 아키텍처 계약

현재 실행 계층은 아래처럼 나뉜다.

- [src/main.py](/D:/vscode/safetycompanion/src/main.py): 진입점
- [src/cli/parser.py](/D:/vscode/safetycompanion/src/cli/parser.py): 명령 파싱
- [src/cli/commands](/D:/vscode/safetycompanion/src/cli/commands): command별 실행 연결
- [src/workflows](/D:/vscode/safetycompanion/src/workflows): 단계별 오케스트레이션
- [src/common/paths.py](/D:/vscode/safetycompanion/src/common/paths.py): 공통 경로 해석
- [src/common/pipeline.py](/D:/vscode/safetycompanion/src/common/pipeline.py): `RunContext`와 run manifest

설계 원칙:

- 엔트리포인트는 얇게 유지한다.
- command 계층은 인자 해석과 workflow 호출만 담당한다.
- workflow 계층은 여러 도메인 모듈을 조합한다.
- 도메인 로직은 `parse`, `ingest`, `retrieval`, `qa`, `eval`에 둔다.
- 경로 조합은 가능한 한 `ProjectPaths`와 config 기반으로 처리한다.

## 6. 설정 계약

설정 체인은 아래와 같다.

- [configs/project.yaml](/D:/vscode/safetycompanion/configs/project.yaml): 기본 경로와 파라미터
- [configs/prod.yaml](/D:/vscode/safetycompanion/configs/prod.yaml): 기본 운영 프로필
- [configs/exp_graph.yaml](/D:/vscode/safetycompanion/configs/exp_graph.yaml): graph 실험 프로필

`load_config()`는 `extends`를 지원한다. 설정 변경 시 경로, feature flag, retrieval 파라미터가 실제 코드와 일치해야 한다.

## 7. 입력 및 산출물 계약

필수 입력:

- `data/SafetyCompanion-2026.pdf`

안정 산출물:

- `data/raw/*`
- `data/parsed/*`
- `data/processed/*`
- `data/eval/*`
- `data/graph/*`
- `indexes/*`

실행별 산출물:

- `outputs/<run_id>/*`

`run_id` 형식:

- `YYYYMMDD-HHMMSS_<sourcehash8>`

run manifest는 최소 아래 필드를 포함해야 한다.

- `run_id`
- `source_file`
- `source_hash`
- `config_file`
- `config_hash`
- `status`
- `steps_completed`
- `artifacts`
- `metrics`

## 8. 표준 명령 계약

지원해야 하는 표준 명령은 아래와 같다.

```powershell
python -m src.main preflight
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml
python -m src.main build-indexes --config configs/prod.yaml
python -m src.main query "FMVSS 305a 관련 세미나를 찾아줘" --config configs/prod.yaml
python -m src.main eval --config configs/prod.yaml
pytest -q
```

각 명령은 [docs/current/cli_reference.md](/D:/vscode/safetycompanion/docs/current/cli_reference.md)에 정의된 입력과 산출물 계약을 따라야 한다.

## 9. 데이터 계약 핵심

공통 식별자:

- `document_id`
- `pdf_page`
- `printed_page`
- `entry_id`
- `entry_bundle_id`
- `chunk_id`
- `run_id`

핵심 규칙:

- `pdf_page`와 `printed_page`를 혼합하지 않는다.
- `printed_page`가 없을 때는 `null`을 허용한다.
- `entry_id`는 검색 단위 엔트리 식별자다.
- `entry_bundle_id`는 multi-page 또는 관련 엔트리 묶음을 표현한다.
- dataset schema는 additive하게 확장될 수 있지만, 공통 핵심 필드는 유지한다.

세부 필드 목록은 [docs/current/data_contract.md](/D:/vscode/safetycompanion/docs/current/data_contract.md)를 따른다.

## 10. Retrieval / Answer 정책 계약

기본 retrieval 경로는 아래 route를 지원한다.

- `abbreviation_lookup`
- `page_or_index_lookup`
- `seminar_lookup`
- `event_lookup`
- `calendar_lookup`
- `compare`
- `recommendation`
- `multi_page_lookup`
- `relationship_query`
- `fallback_general`

route별 허용 코퍼스와 field 우선순위는 [configs/route_field_priority.yaml](/D:/vscode/safetycompanion/configs/route_field_priority.yaml)에 정의한다.

grounded answer 규칙:

- 답변은 가능한 한 citation을 포함해야 한다.
- citation은 기본적으로 `title + pdf_page + printed_page`를 사용한다.
- `printed_page`가 없으면 `pdf_page`만 표기한다.
- 근거가 부족한 compare/recommendation은 보수적 응답을 반환한다.

## 11. 품질 기준

최소 운영 기준은 [docs/current/acceptance_criteria.md](/D:/vscode/safetycompanion/docs/current/acceptance_criteria.md)를 따른다.

핵심 게이트는 아래와 같다.

- page manifest coverage: `224 / 224`
- seminar/event title extraction accuracy: `>= 0.98`
- abbreviation exact-match accuracy: `>= 0.95`
- retrieval Recall@10: `>= 0.85`
- citation page hit rate: `>= 0.95`
- compare/recommendation grounded success rate: `>= 0.80`

고정 baseline 참고값은 [docs/baselines/baseline_v5.md](/D:/vscode/safetycompanion/docs/baselines/baseline_v5.md)에 있다.

## 12. 재실행 및 무효화 규칙

아래 규칙은 현재 운영용 무효화 기준이다.

- parse 또는 ingest 로직 변경:
  `ingest -> build-indexes -> query -> eval`
- chunking, lookup, indexing 변경:
  `build-indexes -> query -> eval`
- route policy, retrieval score 조정 변경:
  최소 `query -> eval`, 필요 시 `build-indexes -> query -> eval`
- answer template 또는 grounding 정책 변경:
  `query -> eval`
- evaluator 또는 리포트 포맷 변경:
  `eval`

실패 실행은 기존 성공 산출물을 덮어쓰지 않는다. 실행 실패 정보는 해당 `outputs/<run_id>/...` 아래에 남겨야 한다.

## 13. 운영 예외 처리

- 입력 PDF가 없으면 즉시 중단
- `pdfinfo` 또는 `pdftotext` 실패 시 `preflight` 단계에서 중단
- citation 없는 응답은 실패로 취급
- 광고/비주요 페이지를 일반 검색 근거로 사용하면 실패로 취급
- 기본 경로가 불안정한 상태에서 graph 경로를 승격하지 않는다

## 14. 현재 알려진 한계

- 일부 페이지는 인코딩 노이즈가 남아 `knowledge` 계열 텍스트 품질이 균일하지 않다.
- 안정 산출물과 실행별 산출물이 완전히 분리된 구조는 아니므로, shared dataset / index 재생성이 이후 질의에 영향을 줄 수 있다.
- graph 코드가 존재하지만 기본 CLI에서 사용되는 기본 경로는 아니다.
