# Specification

## 1. 목적
이 프로젝트의 1차 목표는 `SafetyCompanion-2026.pdf`에서 세미나, 이벤트, SafetyWissen 지식 페이지를 구조화하여, citation이 강제되는 하이브리드 RAG baseline을 만드는 것이다.

## 2. 범위
포함 범위:
- PDF 구조 감사
- 페이지 유형 분류
- 엔트리 추출
- 약어/색인/캘린더 보조 데이터셋 구축
- 하이브리드 검색
- grounded answer
- baseline 평가
- 운영형 CLI와 재현 실행 경로

비포함 범위:
- baseline 품질 확보 전의 GraphRAG
- 사용자 승인 없는 외부 API 의존
- 광고 페이지를 답변 근거로 사용하는 기능

## 3. 권위 문서 규칙
- 구현과 실행 판단은 `spec.md`를 최상위 기준으로 한다.
- 단계 순서와 게이트는 `plan.md`를 따른다.
- 작업 상태 관리는 `tasks.md`를 따른다.
- `work_process/step_*_진행내용.md`는 단계별 상세 지시서다.

## 4. 입력 데이터 계약
필수 입력:
- 원본 PDF: `data/SafetyCompanion-2026.pdf`

입력 검증 규칙:
- 파일이 존재해야 한다.
- `pdfinfo`로 페이지 수를 확인할 수 있어야 한다.
- text layer가 일부라도 존재해야 한다.
- source hash를 계산할 수 있어야 한다.

입력 변경 규칙:
- 원본 PDF가 바뀌면 새로운 `run_id`를 생성해야 한다.
- 원본 PDF hash가 바뀌면 Step 1부터 다시 수행한다.

## 5. 환경 및 권한 계약
작업 기준 환경:
- OS: Windows + PowerShell
- 작업 루트: `D:\vscode\safetycompanion`

사전 확인이 필요한 런타임:
- `python`
- `pdfinfo`
- `pdftotext`
- `pdftoppm`

선호 도구:
- `uv`

선택 도구:
- OCR 도구
- 로컬 embedding/reranker 모델
- 외부 LLM API

권한 규칙:
- 읽기/쓰기 범위는 현재 워크스페이스 전체
- 파괴적 삭제는 금지
- 기존 산출물 덮어쓰기는 `--force` 또는 명시적 재생성 규칙이 있을 때만 허용

외부 서비스 규칙:
- baseline 구현은 외부 API 없이 동작해야 한다.
- 외부 LLM fallback은 아래 조건이 모두 충족될 때만 허용한다.
- 사용자가 허용함
- 자격 증명이 준비됨
- `configs/*.yaml`에서 명시적으로 활성화됨

## 6. Preflight 명령
아래 명령은 구현 전 반드시 통과해야 한다.

```powershell
python --version
pdfinfo data/SafetyCompanion-2026.pdf
pdftotext -f 1 -l 1 data/SafetyCompanion-2026.pdf -
Test-Path data/SafetyCompanion-2026.pdf
```

Preflight 실패 규칙:
- 필수 명령 실패 시 구현을 시작하지 않는다.
- `uv`는 설치되어 있으면 버전을 기록하고, 없으면 대체 설치 경로를 사용한다.
- 실패 내용은 `outputs/<run_id>/preflight_report.md`에 기록한다.

## 7. 경로 및 산출물 규칙
모든 상대경로는 저장소 루트 기준이다.

안정 산출물:
- `data/raw/*`
- `data/parsed/*`
- `data/processed/*`
- `data/graph/*`
- `indexes/*`

실행별 산출물:
- `outputs/<run_id>/*`

권장 `run_id` 형식:
- `YYYYMMDD-HHMMSS_<sourcehash8>`

선택 미러:
- `outputs/latest/*`

규칙:
- `outputs/<run_id>/...`가 1차 산출물이다.
- `outputs/latest/`는 가장 최근 성공 실행을 가리키는 미러로만 사용한다.

## 8. 데이터 계약 핵심
공통 식별자:
- `document_id`
- `pdf_page`
- `printed_page`
- `entry_bundle_id`
- `entry_id`
- `chunk_id`
- `run_id`

필수 규칙:
- `pdf_page`와 `printed_page`를 혼합하지 않는다.
- printed page가 없으면 `null`을 허용하되, 누락 이유를 기록한다.
- `entry_id`는 엔트리 단위, `entry_bundle_id`는 multi-page 또는 multi-entry 묶음 단위다.

파일 형식 규칙:
- 레코드성 데이터셋은 기본적으로 `.jsonl`
- 스키마/설정은 `.yaml` 또는 `.json`
- 평가/리포트는 `.md`, `.csv`, `.jsonl`

## 9. 성공 기준 및 게이트
Step 3 gate:
- page manifest coverage == 224
- page type taxonomy가 전 페이지에 적용됨

Step 4 gate:
- entry 추출 실패 페이지 목록이 산출됨
- 약어/색인/캘린더 데이터셋이 생성됨

Step 5 gate:
- dense, BM25, lookup store가 모두 생성됨
- smoke test 질문에서 빈 응답률 <= 10%

Step 6 gate:
- citation 없는 응답 테스트가 실패하도록 구현됨
- route trace가 저장됨

Step 7 gate:
- seminar/event title extraction accuracy >= 0.98
- abbreviation exact-match accuracy >= 0.95
- retrieval Recall@10 >= 0.85
- citation page hit rate >= 0.95
- compare/recommendation grounded success rate >= 0.80

Step 8 gate:
- ingest/build-index/query/eval CLI가 재현 가능하게 동작함
- `outputs/<run_id>/run_manifest.json`이 생성됨

Step 9는 선택 단계다.
- Step 7 gate와 Step 8 gate를 모두 통과한 후에만 시작한다.

## 10. 재시도, 롤백, 무효화 규칙
재시도 규칙:
- 일시적 파싱 실패는 최대 2회 재시도한다.
- 외부 의존 실패는 baseline 경로에서 기능 비활성화 후 계속 진행한다.

무효화 규칙:
- Step 1 산출물 변경 시 Step 2-9를 무효화한다.
- Step 2 산출물 변경 시 Step 3-9를 무효화한다.
- Step 3 산출물 변경 시 Step 4-9를 무효화한다.
- Step 4 산출물 변경 시 Step 5-9를 무효화한다.
- Step 5 산출물 변경 시 Step 6-9를 무효화한다.
- Step 6 산출물 변경 시 Step 7-9를 무효화한다.
- Step 7 산출물 변경 시 Step 8-9를 재판정한다.

롤백 규칙:
- 안정 산출물은 기존 파일을 즉시 삭제하지 않는다.
- 실패 실행의 산출물은 `outputs/<run_id>/failed/`로 이동하거나 실패로 마킹한다.
- 최신 성공 실행을 덮어쓰지 않는다.

## 11. 검증 명령 표준
구현 완료 후 지원되어야 하는 표준 검증 명령:

```powershell
python -m src.main preflight
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml
python -m src.main build-indexes --config configs/prod.yaml
python -m src.main query "FMVSS 305a 관련 세미나를 찾아줘" --config configs/prod.yaml
python -m src.main eval --config configs/prod.yaml
python -m pytest
```

`src.main`이 아직 없으면 Step 2 이전에는 Preflight와 문서 산출물 검증만 수행한다.

## 12. 사용자 결정 등록부
아래 항목은 미결정이며, 문서만으로 추정하지 않는다.

| 항목 | 상태 | 임시 운영 규칙 |
|---|---|---|
| 외부 LLM fallback 사용 여부 | Pending | 비활성화 |
| 외부 embedding/reranker API 사용 여부 | Pending | 로컬 또는 미사용 |
| Graph DB 사용 여부 | Pending | 파일 기반 JSONL export만 허용 |
| citation 표시 우선순위 | Pending | `title + pdf_page + printed_page` 동시 표기 |
| 운영 데모 UI 포함 여부 | Pending | CLI만 필수, UI는 선택 |

확정 항목:
- baseline MVP에는 GraphRAG를 포함하지 않는다.
- 광고/약관/디렉터리 페이지는 기본 검색 코퍼스에서 제외한다.
- 실행 산출물은 `outputs/<run_id>/...`에 저장한다.

## 13. 실패 시 예외 처리 원칙
- 입력 PDF 검증 실패: 즉시 중단
- 페이지 타입 taxonomy 미완성: Step 3에서 중단
- 엔트리 추출 누락률 과다: Step 4 재작업
- retrieval 지표 미달: Step 5-6 재작업
- grounding 지표 미달: Step 6 재작업
- Step 7 gate 미통과: Step 8 및 Step 9 진행 금지

## 14. 용어집
- `pdf_page`: PDF 뷰어 기준의 물리 페이지 번호
- `printed_page`: 문서 내부 인쇄 표기 페이지 번호
- `entry_id`: 단일 검색 대상 엔트리 식별자
- `entry_bundle_id`: multi-page 또는 multi-entry 묶음 식별자
- `backfill`: lookup 또는 graph hit 이후 실제 본문 근거 엔트리로 다시 이동하는 절차
- `run_id`: 단일 실행 세션 식별자
