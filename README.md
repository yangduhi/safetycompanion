# SafetyCompanion RAG Build Instructions

이 워크스페이스는 `data/SafetyCompanion-2026.pdf`를 기반으로 Structure-first RAG 시스템을 구축하기 위한 실행용 문서 세트를 담고 있다. 현재 저장소는 구현보다 작업지시와 실행 규칙을 먼저 고정하는 단계이며, 실제 Codex/에이전트는 아래 문서 우선순위를 따라야 한다.

## 권위 문서 우선순위
1. `spec.md`
2. `plan.md`
3. `tasks.md`
4. `work_process/step_*_진행내용.md`

## 현재 목표
- `SafetyCompanion-2026.pdf`의 구조를 복원한다.
- 세미나, 이벤트, SafetyWissen 지식 페이지를 RAG용 구조화 데이터로 변환한다.
- 하이브리드 검색과 grounded answer를 구현한다.
- baseline 품질을 먼저 확보한 뒤, 필요하면 선택형 GraphRAG를 도입한다.

## 문서 맵
- [spec.md](/D:/vscode/safetycompanion/spec.md): 범위, 환경, 데이터 계약, 성공 기준, 재실행 규칙
- [plan.md](/D:/vscode/safetycompanion/plan.md): 단계 순서, 의존성, go/no-go gate, 실패 시 되돌아갈 단계
- [tasks.md](/D:/vscode/safetycompanion/tasks.md): 실제 작업 체크리스트
- [work_process/README.md](/D:/vscode/safetycompanion/work_process/README.md): step 문서 사용 규칙

## 입력 데이터
- 필수 입력 PDF: [data/SafetyCompanion-2026.pdf](/D:/vscode/safetycompanion/data/SafetyCompanion-2026.pdf)
- 모든 상대경로는 저장소 루트 `D:\vscode\safetycompanion` 기준이다.

## 실행 원칙
- baseline 경로는 오프라인 우선으로 구축한다.
- 외부 LLM, 외부 reranker, 외부 graph DB는 사용자 결정 또는 명시적 설정 없이는 사용하지 않는다.
- `pdf_page`와 `printed_page`를 항상 분리 저장한다.
- `outputs/` 아래 산출물은 `outputs/<run_id>/...` 구조로 저장한다.
- Step 7 gate를 통과하기 전에는 운영화와 선택형 GraphRAG를 시작하지 않는다.

## 빠른 시작
1. [spec.md](/D:/vscode/safetycompanion/spec.md)의 Preflight를 먼저 수행한다.
2. [plan.md](/D:/vscode/safetycompanion/plan.md)의 Phase 0부터 순서대로 진행한다.
3. 각 완료 항목은 [tasks.md](/D:/vscode/safetycompanion/tasks.md)에서 체크한다.
4. 단계별 상세 작업은 `work_process/step_*_진행내용.md`를 참조한다.

## 현재 상태
- 구현 코드는 아직 준비되지 않았을 수 있다.
- 문서 체계는 실행 가능하도록 정비되었지만, 미결정 항목은 `spec.md`의 결정 등록부를 먼저 확인해야 한다.
