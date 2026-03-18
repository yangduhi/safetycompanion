# Branch Scoped Docs

이 폴더는 브랜치별 실험 기록, 브랜치 전용 가이드, 브랜치별 baseline snapshot을 보관하는 공간이다.

현재 해석 규칙:

- `docs/branches/` 아래 문서는 기본적으로 현재 운영 기준 문서가 아니다.
- 이 문서들은 특정 브랜치의 작업 문맥을 복원하기 위한 히스토리/보조 자료로 본다.
- 공통 규칙이나 현재 운영 절차는 항상 `docs/` 루트와 루트 문서를 우선한다.

권장 구조:

```text
docs/
  branches/
    <branch-slug>/
      baselines/
      reports/
      guides/
```

규칙:

- 공통/영구 문서는 `docs/` 루트에 둔다.
- 특정 작업 브랜치에 종속되는 문서는 `docs/branches/<branch-slug>/...`에 둔다.
- 브랜치 문서가 현재 기준으로 승격되면, 내용을 정리한 뒤 `docs/` 루트의 현행 문서로 재작성한다.
- baseline freeze가 브랜치 전용 실험 결과라면 브랜치별 `baselines/` 아래에 저장한다.
