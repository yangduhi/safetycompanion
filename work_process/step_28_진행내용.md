# Step 28 진행내용

## 목표

- 현재 dirty worktree를 안전하게 백업한다.
- `stable experimental` 기준선을 문서로 고정한다.
- `code / docs / generated data` 분리 커밋 계획을 파일 단위로 명시한다.

## 수행 내용

### 1. 백업 아티팩트 생성

- `tmp/handoff/dirty_worktree.patch`
- `tmp/handoff/dirty_tracked_files.txt`
- `tmp/handoff/dirty_untracked_files.txt`
- `tmp/handoff/stash_create_oid.txt`

현재 `git stash create` OID:

- `96535885dc364e684839d727646954a460eb4ef0`

### 2. baseline 문서 보강

- `docs/current/graph_baseline_exp_v1.md`
  - 기준 run
  - hard set contract
  - `G002` triage 해석
  - strict knowledge-only 보조 셋 링크
  - tag 생성 시점 가이드 추가

### 3. strict interpretation helper set 추가

- `data/eval/graph_hard_questions_strict_knowledge_only.jsonl`

용도:

- `G002`처럼 semantics가 넓은 질문에 대해
- "knowledge-only로 보면 어떻게 보이는지" 해석 보조용

### 4. split manifest / PR stack 문서화

- `docs/current/split_commit_manifest.md`
- `docs/current/pr_stack_plan.md`

## 현재 권장 상태

- graph: `stable experimental baseline`
- ODL: `whitelist-only auxiliary parser lane`
- G3: 보류
- 다음 실무 우선순위:
  - code-only 커밋
  - docs-only 커밋
  - generated-data 분리
