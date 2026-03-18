# Branch Scoped Docs

브랜치별로 생성되거나 갱신되는 문서와 baseline snapshot은 아래 경로에 저장한다.

```text
docs/
  branches/
    <branch-slug>/
      baselines/
      reports/
      guides/
```

규칙:
- 공통/영구 문서는 `docs/` 루트에 둔다
- 특정 작업 브랜치에 종속되는 문서는 `docs/branches/<branch-slug>/...`에 둔다
- baseline freeze는 항상 브랜치별 `baselines/` 아래에 저장한다
