# Execution Plan

## Phase 1. 문서화

- 현재 구조 문제를 기록한다.
- 목표 구조와 책임 분리 기준을 문서화한다.
- 이번 턴에서 실제 적용하는 범위를 명확히 고정한다.

## Phase 2. 엔트리포인트 분리

- `src/main.py`에서 command 로직을 제거한다.
- CLI parser와 command dispatch를 `src/cli`로 이동한다.

성공 기준:

- `src/main.py`는 진입점 역할만 수행한다.
- 기존 CLI 인터페이스는 유지된다.

## Phase 3. 워크플로 계층 도입

- `preflight`, `ingest`, `build-indexes`, `query`, `eval`의 오케스트레이션을 `src/workflows`로 이동한다.
- command 모듈은 workflow 호출과 결과 처리만 담당한다.

성공 기준:

- 도메인 로직을 읽기 위해 더 이상 `main.py`를 볼 필요가 없다.

## Phase 4. 경로 중앙화

- `src/common/paths.py`를 도입한다.
- 인덱스와 lookup 경로의 직접 조합을 제거한다.
- route policy 경로 해석도 중앙화한다.

성공 기준:

- 경로 규칙 변경 시 수정 지점이 명확하다.

## Phase 5. 검증

- `pytest -q`
- `python -m src.main --help`

추가 점검:

- import 오류가 없어야 한다.
- 기존 테스트가 모두 통과해야 한다.
