# Progress Log

## Baseline

- 작업 시작 시점 `git status --short` 결과는 clean 상태였다.
- 작업 시작 전 `pytest -q` 결과는 `15 passed`였다.

## Planned Changes

- `main.py` 슬림화
- CLI 계층 분리
- workflow 계층 도입
- 경로 중앙화

## Notes

- 이번 리팩터링은 기능 변경보다 구조 정리와 책임 분리가 우선이다.
- 기존 테스트와 CLI 인터페이스를 유지하는 방향으로 진행한다.

## Applied Changes

- `src/main.py`를 얇은 엔트리포인트로 축소했다.
- `src/cli/`를 추가해 parser, command dispatch, manifest 마감 처리를 분리했다.
- `src/workflows/`를 추가해 `preflight`, `ingest`, `build-indexes`, `query`, `eval` 오케스트레이션을 단계별 모듈로 이동했다.
- `src/common/paths.py`를 추가해 document, output, index, lookup, route policy 경로를 중앙화했다.
- `src/retrieval/service.py`, `src/common/pipeline.py`, `src/common/policy.py`가 새 경로 계층을 사용하도록 정리했다.
- 경로 중앙화 동작을 보장하기 위해 `tests/test_project_paths.py`를 추가했다.

## Validation

- `pytest -q` 결과: `16 passed`
- `python -m src.main --help` 정상 동작 확인

## Outcome

- CLI 진입점 파일을 읽지 않고도 command별 실행 흐름을 추적할 수 있게 되었다.
- 경로 규칙 변경 시 수정 지점이 줄어들었다.
- 이후 추가 리팩터링은 `workflows` 내부 세분화나 `eval` 모듈 분리 수준에서 더 안전하게 진행할 수 있다.
