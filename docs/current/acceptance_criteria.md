# Acceptance Criteria

## 1. 최소 운영 게이트

기본 경로가 “정상 동작”으로 간주되려면 아래 기준을 만족해야 한다.

- page manifest coverage: `224 / 224`
- seminar / event title extraction accuracy: `>= 0.98`
- abbreviation exact-match accuracy: `>= 0.95`
- retrieval Recall@10: `>= 0.85`
- citation page hit rate: `>= 0.95`
- compare / recommendation grounded success rate: `>= 0.80`

## 2. 답변 품질 가드레일

아래 경우는 실패로 본다.

- citation 없는 최종 답변
- 광고/비주요 페이지를 일반 retrieval 근거로 사용
- `pdf_page`와 `printed_page`를 혼동한 표기
- compare / recommendation에서 근거 부족인데도 확정적 결론 제시

## 3. 운영 readiness

아래 명령이 정상 동작해야 한다.

```powershell
python -m src.main preflight
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml
python -m src.main build-indexes --config configs/prod.yaml
python -m src.main query "FMVSS 305a 관련 세미나를 찾아줘" --config configs/prod.yaml
python -m src.main eval --config configs/prod.yaml
pytest -q
```

## 4. 현재 참고 기준

고정 기준선은 [docs/baselines/baseline_v5.md](/D:/vscode/safetycompanion/docs/baselines/baseline_v5.md)다. 이 스냅샷은 현재 저장소가 한 번 이상 달성한 참조 성능이며, 문서상 참고 기준으로 사용한다.

대표 참고값:

- `page_manifest_coverage = 224`
- `entry_count = 177`
- `abbreviation_count = 365`
- `calendar_entry_count = 88`
- `recall_at_10 = 1.0`
- `citation_page_hit_rate = 1.0`
- `grounded_success_rate = 1.0`

## 5. 문서 기준

기능이 바뀌었는데 아래 문서가 그대로면 acceptance를 충족하지 못한 것으로 본다.

- `README.md`
- `spec.md`
- `plan.md`
- `tasks.md`
- `docs/current/cli_reference.md`
- `docs/current/data_contract.md`
