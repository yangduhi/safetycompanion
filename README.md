# SafetyCompanion RAG

`SafetyCompanion-2026.pdf`를 대상으로 하는 구조 우선형 RAG CLI 프로젝트다. 이 저장소는 PDF를 구조화 데이터로 복원하고, 하이브리드 검색과 근거 기반 답변을 제공하며, 동일한 입력에 대해 재현 가능한 평가 산출물을 남기는 것을 목표로 한다.

현재 기본 경로는 오프라인 우선이다. 기본 검색은 TF-IDF + SVD, BM25, lookup store, 휴리스틱 라우팅, 규칙 기반 grounded answer로 구성되어 있으며, Graph 경로는 선택 실험용으로만 유지된다.

## 현재 상태

- `python -m src.main preflight|ingest|build-indexes|query|eval` 전체 경로가 구현되어 있다.
- 리팩터링을 통해 엔트리포인트, CLI 계층, 워크플로 계층, 공통 경로 계층이 분리되었다.
- 기본 데이터셋과 인덱스, 평가 산출물, baseline 스냅샷이 저장소에 포함되어 있다.
- 테스트 스위트는 라우팅, grounded answer, 경로 계약을 검증한다.

## 핵심 구조

- [src/main.py](/D:/vscode/safetycompanion/src/main.py): 진입점
- [src/cli](/D:/vscode/safetycompanion/src/cli): argparse와 command dispatch
- [src/workflows](/D:/vscode/safetycompanion/src/workflows): 단계별 오케스트레이션
- [src/common](/D:/vscode/safetycompanion/src/common): config, runtime, paths, manifest 공통 계층
- [src/parse](/D:/vscode/safetycompanion/src/parse): PDF 파싱과 페이지 분류
- [src/ingest](/D:/vscode/safetycompanion/src/ingest): 엔트리, 약어, 색인, 캘린더 추출
- [src/retrieval](/D:/vscode/safetycompanion/src/retrieval): 청킹, 인덱스, 라우팅, 검색, fusion, rerank
- [src/qa](/D:/vscode/safetycompanion/src/qa): grounded answer 생성
- [src/eval](/D:/vscode/safetycompanion/src/eval): 평가 및 리포트 작성
- [src/graph](/D:/vscode/safetycompanion/src/graph): 선택형 graph 실험 코드

## 표준 실행 흐름

```powershell
python -m src.main preflight
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml
python -m src.main build-indexes --config configs/prod.yaml
python -m src.main query "FMVSS 305a 관련 세미나를 찾아줘" --config configs/prod.yaml
python -m src.main eval --config configs/prod.yaml
pytest -q
```

각 명령은 `outputs/<run_id>/...` 아래에 실행별 산출물을 남긴다. 단, 검색에 사용되는 안정 데이터와 인덱스는 `data/processed/*`, `indexes/*`처럼 공유 위치에 저장되므로 재빌드 시 이후 질의 결과에 영향을 줄 수 있다.

## 현재 기준 문서

- [docs/README.md](/D:/vscode/safetycompanion/docs/README.md): `docs/` 디렉터리 사용 가이드
- [docs/DOC_STATUS.md](/D:/vscode/safetycompanion/docs/DOC_STATUS.md): 현재 유효 문서와 히스토리 문서 분류표
- [docs/current/README.md](/D:/vscode/safetycompanion/docs/current/README.md): 핵심 운영 문서 관리 규칙
- [spec.md](/D:/vscode/safetycompanion/spec.md): 현재 아키텍처, 계약, 운영 규칙
- [plan.md](/D:/vscode/safetycompanion/plan.md): 현재 운영 흐름과 개선 우선순위
- [tasks.md](/D:/vscode/safetycompanion/tasks.md): 현재 상태 체크리스트와 활성 backlog
- [docs/current/cli_reference.md](/D:/vscode/safetycompanion/docs/current/cli_reference.md): 명령별 입력과 산출물
- [docs/current/ops_playbook.md](/D:/vscode/safetycompanion/docs/current/ops_playbook.md): 재실행, 점검, 장애 대응 가이드
- [docs/current/data_contract.md](/D:/vscode/safetycompanion/docs/current/data_contract.md): 데이터셋과 산출물 계약
- [docs/current/acceptance_criteria.md](/D:/vscode/safetycompanion/docs/current/acceptance_criteria.md): 품질 게이트와 운영 readiness 기준
- [refactoring/README.md](/D:/vscode/safetycompanion/refactoring/README.md): 최근 구조 리팩터링 문서

## 구성 파일

- [configs/project.yaml](/D:/vscode/safetycompanion/configs/project.yaml): 기본 경로와 retrieval 파라미터
- [configs/prod.yaml](/D:/vscode/safetycompanion/configs/prod.yaml): 기본 운영 프로필
- [configs/exp_graph.yaml](/D:/vscode/safetycompanion/configs/exp_graph.yaml): graph 실험 프로필
- [configs/route_field_priority.yaml](/D:/vscode/safetycompanion/configs/route_field_priority.yaml): route별 허용 코퍼스와 field 우선순위

## 현재 주의할 점

- 일부 PDF 페이지는 텍스트 레이어 품질이 낮아 인코딩 노이즈가 남아 있다.
- `pdf_page`와 `printed_page`는 항상 분리해서 다뤄야 한다.
- 기본 CLI 경로는 graph 모듈을 사용하지 않는다.
- baseline은 로컬 경로만으로 동작해야 하며, 외부 API 의존은 선택 기능이다.

## 참고 스냅샷

저장소에는 baseline 스냅샷이 이미 포함되어 있다. 최신 고정 스냅샷은 [docs/baselines/baseline_v5.md](/D:/vscode/safetycompanion/docs/baselines/baseline_v5.md)이며, 이 문서는 현재 구현이 한 번 이상 달성한 품질 기준을 보여준다. 운영 중에는 최신 실행 산출물과 frozen baseline을 함께 확인하는 것을 권장한다.
