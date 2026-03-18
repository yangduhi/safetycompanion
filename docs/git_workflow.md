# Git Workflow

## 기본 원칙
- 기준 브랜치는 `main`
- 모든 작업 브랜치는 `codex/` prefix 사용
- PR base는 항상 `main`

## 현재 상태
- `main` exists locally and tracks `origin/main`
- `codex/bootstrap-rag` keeps the implementation history up to the current baseline

## 이후 작업 흐름
1. `main` 최신화
2. 새 브랜치 생성: `git checkout -b codex/<task-name>`
3. 작업 / 테스트 / 커밋
4. `git push -u origin codex/<task-name>`
5. PR 생성 시 base는 `main`

## 예시
```powershell
git checkout main
git pull
git checkout -b codex/phase4-error-taxonomy
git push -u origin codex/phase4-error-taxonomy
```

## 참고
- 현재 GitHub 저장소의 remote default branch가 아직 `codex/bootstrap-rag`로 보일 수 있다.
- 실제 작업 기준은 `main`으로 전환했고, 이후 PR 생성 시 base를 `main`으로 지정하면 된다.
