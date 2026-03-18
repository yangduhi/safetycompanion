# Resume Checklist

## 목적
프로젝트 구조 리팩토링 후 `codex/phase3d3-dummy-refinement` 브랜치에서 작업을 재개할 때, 무엇부터 확인하고 어떤 순서로 복구/검증/재시작해야 하는지 빠르게 확인하기 위한 체크리스트다.

## 현재 기준점
- active branch: `codex/phase3d3-dummy-refinement`
- latest branch baseline:
  - [baseline_v5.json](/D:/vscode/safetycompanion/docs/branches/codex__phase3d3-dummy-refinement/baselines/baseline_v5.json)
  - [baseline_v5.md](/D:/vscode/safetycompanion/docs/branches/codex__phase3d3-dummy-refinement/baselines/baseline_v5.md)
- branch-specific docs:
  - [phase3d3_execution_guide.md](/D:/vscode/safetycompanion/docs/branches/codex__phase3d3-dummy-refinement/phase3d3_execution_guide.md)
  - [dummy_grouping_refinement_spec.md](/D:/vscode/safetycompanion/docs/branches/codex__phase3d3-dummy-refinement/dummy_grouping_refinement_spec.md)

## 마지막으로 확인된 상태
- mainline: stable
- compare: regression-only monitoring
- event paraphrase: practically closed
- remaining bottleneck: dummy multi-page top-1 grouping
- latest key reports:
  - [multi_page_dummy_eval.md](/D:/vscode/safetycompanion/outputs/20260318-153426_90cd5e6d/multi_page_dummy_eval.md)
  - [error_taxonomy_report_v3.md](/D:/vscode/safetycompanion/outputs/20260318-153426_90cd5e6d/error_taxonomy_report_v3.md)
  - [compare_regression_report.md](/D:/vscode/safetycompanion/outputs/20260318-153426_90cd5e6d/compare_regression_report.md)

## 재개 전 체크
- [ ] 현재 브랜치가 `codex/phase3d3-dummy-refinement`인지 확인
- [ ] 리팩토링으로 이동/이름이 바뀐 경로를 점검
  - `src/`
  - `configs/`
  - `data/eval/`
  - `docs/branches/`
  - `outputs/`
- [ ] `data/SafetyCompanion-2026.pdf` 경로가 유지되는지 확인
- [ ] `configs/project.yaml`의 경로 설정이 여전히 유효한지 확인
- [ ] `python -m pytest`가 통과하는지 확인

## 재개 순서
1. 브랜치 및 기준점 확인
   - `git branch --show-current`
   - `git log --oneline --decorate -5`
2. baseline 문서 확인
   - `baseline_v5`
3. 최신 리포트 확인
   - `multi_page_dummy_eval.md`
   - `error_taxonomy_report_v3.md`
   - `multi_page_group_details_v2.csv`
4. 리팩토링 영향 확인
   - import 경로
   - config path
   - output path
5. smoke test
   - `python -m src.main query "THOR 관련 더미 페이지" --config configs/prod.yaml`
   - `python -m src.main query "dummy landscape 관련 페이지들을 모아서 보여줘" --config configs/prod.yaml`
6. full eval
   - `python -m src.main eval --config configs/prod.yaml --baseline-label baseline_v5`

## 재개 후 우선 작업
- `dummy grouping refinement v3`
  - seed page priority refinement
  - secondary page compatibility gating
  - page role scoring tuning

## 확인해야 할 파일
- query normalization:
  - [query_normalization.py](/D:/vscode/safetycompanion/src/retrieval/query_normalization.py)
- multi-page grouping:
  - [multipage_grouping.py](/D:/vscode/safetycompanion/src/retrieval/multipage_grouping.py)
- retrieval orchestration:
  - [service.py](/D:/vscode/safetycompanion/src/retrieval/service.py)
- multi-page answer policy:
  - [answer_generator.py](/D:/vscode/safetycompanion/src/qa/answer_generator.py)
- taxonomy:
  - [error_taxonomy.py](/D:/vscode/safetycompanion/src/eval/error_taxonomy.py)

## 성공 기준
- `multi_page_dummy top1_hit_rate`가 baseline보다 개선
- `top3/top10` 유지
- `MULTI_PAGE_COLLAPSE__DUMMY_TOPIC_MERGE_FAIL` 감소
- compare regression 없음
- event paraphrase 재발 없음

## 주의사항
- global metric이 높아도 dummy hard slice는 별도로 봐야 한다.
- compare는 더 확장하지 말고 regression만 본다.
- GraphRAG는 여전히 보류한다.
- branch-specific docs는 앞으로도 `docs/branches/<branch-slug>/...`에 저장한다.
