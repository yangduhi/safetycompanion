# Step 8. 운영형 CLI 및 재현 실행 경로 구축

## 목표
Step 7 gate를 통과한 baseline을 재현 가능하게 실행하고, 운영형 CLI와 실행 문서를 갖춘다. 이 단계는 필수 단계이며 선택 기능을 포함하지 않는다.

## 선행조건
- `step_7_진행내용.md` 완료
- Step 7 gate 통과

## 핵심 판단
1. baseline이 수치 gate를 통과하지 못한 상태에서 운영형 포장을 시작하면, 불안정한 시스템을 고정하게 된다.
2. 운영 경로는 실험 경로와 분리되어야 한다.

## 필수 작업
1. 운영형 CLI를 구현한다.

```bash
python -m src.main preflight
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml
python -m src.main build-indexes --config configs/prod.yaml
python -m src.main query "FMVSS 305a 관련 세미나를 찾아줘" --config configs/prod.yaml
python -m src.main eval --config configs/prod.yaml
```

2. `configs/prod.yaml`을 작성한다.
- baseline retrieval 경로
- optional feature 비활성화 기본값
- artifact 경로 정책
- run manifest 설정

3. 실행 추적과 관측성을 추가한다.
- `run_id`
- source hash
- config hash
- 단계별 시작/종료 시각
- retrieval source mix
- reranker 사용 여부
- citation 생성 여부

4. 운영 문서를 작성한다.
- 설치 방법
- 실행 방법
- 인덱스 재생성 방법
- 신규 PDF 교체 방법
- 장애 시 점검 순서

5. `outputs/<run_id>/run_manifest.json`을 남긴다.
- git hash는 저장소가 git이 아닐 경우 `null`
- 실패 실행도 상태값과 함께 기록

## 운영 원칙
1. 운영 경로는 baseline 기준으로만 동작해야 한다.
2. 외부 LLM, graph, contextual compression 등 선택 기능은 기본 비활성화다.
3. `outputs/<run_id>/...`를 기본 산출물 경로로 사용한다.
4. 최신 성공 실행을 별도 보존하고, 실패 실행은 덮어쓰지 않는다.

## Codex 작업 지시
- `src/main.py`를 구현하라.
- `configs/prod.yaml`을 작성하라.
- `docs/ops_playbook.md`와 `docs/cli_reference.md`를 작성하라.
- `outputs/<run_id>/run_manifest.json` 생성 규칙을 구현하라.

## 완료 기준
- preflight/ingest/build-indexes/query/eval CLI가 재현 가능하게 동작함
- `run_manifest.json`이 생성됨
- 운영 문서만 읽고 재실행 가능함
- 선택 기능이 baseline 경로에 섞이지 않음

## 산출물
- `src/main.py`
- `configs/prod.yaml`
- `docs/ops_playbook.md`
- `docs/cli_reference.md`
- `outputs/<run_id>/run_manifest.json`

## 검증 포인트
- 동일 PDF와 동일 config에서 재실행이 가능한가
- 실패 실행이 성공 실행을 덮어쓰지 않는가
- optional feature가 기본 비활성화로 유지되는가
- CLI만으로 query/eval 경로를 재현할 수 있는가
