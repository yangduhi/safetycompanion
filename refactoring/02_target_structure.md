# Target Structure

## 목표 원칙

이번 리팩터링은 아래 원칙을 따른다.

1. 엔트리포인트는 얇게 유지한다.
2. CLI 계층은 인자 파싱과 실행 분기만 담당한다.
3. 워크플로 계층은 도메인 모듈 조합과 산출물 작성을 담당한다.
4. 공통 경로 해석은 한곳에서 담당한다.
5. 기존 명령 인터페이스는 유지한다.

## 목표 디렉터리 구조

```text
src/
  main.py
  cli/
    parser.py
    shared.py
    commands/
      preflight.py
      ingest.py
      build_indexes.py
      query.py
      eval.py
  workflows/
    result.py
    preflight.py
    ingest.py
    indexes.py
    query.py
    evaluation.py
  common/
    config.py
    runtime.py
    pipeline.py
    paths.py
    policy.py
```

## 책임 분리

### `src/main.py`

- 애플리케이션 진입점 유지
- parser 생성 호출
- 선택된 command 실행

### `src/cli/*`

- argparse 구성
- command별 인자 처리
- manifest 수명주기 연결
- 성공/실패 exit code 반환

### `src/workflows/*`

- 단계별 실제 실행 절차 관리
- 여러 도메인 모듈 호출
- 단계 산출물과 메트릭 반환

### `src/common/paths.py`

- config 기반 경로 해석
- document, output, index, lookup 경로 중앙화
- 다른 모듈이 하드코딩 경로를 직접 조합하지 않도록 통제

## 유지할 호환성

- `python -m src.main ...` 명령 유지
- 기존 config 구조 유지
- 기존 테스트 기대값 유지
- 기존 route policy와 answer behavior 유지
