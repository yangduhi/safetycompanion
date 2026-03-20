# Auxiliary Parser Experiment

## 목적

`pdftotext` 기본 경로는 유지하면서, layout-heavy `knowledge` 페이지에만 `opendataloader-pdf`를 보조 파서로 적용해 A/B 실험을 수행한다.

## 실험 config

- local heuristic:
  - [exp_parser_odl_local.yaml](/D:/vscode/safetycompanion/configs/exp_parser_odl_local.yaml)
- hybrid:
  - [exp_parser_odl_hybrid.yaml](/D:/vscode/safetycompanion/configs/exp_parser_odl_hybrid.yaml)

## 현재 동작 방식

1. 기본 ingest는 여전히 `pdftotext -layout`로 전체 PDF를 파싱한다.
2. 1차 분류 결과에서 `page_type == knowledge`인 페이지 중 `min_word_count` 이상인 페이지를 후보로 고른다.
3. 후보 페이지에만 `opendataloader-pdf --pages ...`를 호출해 재파싱한다.
4. 재파싱이 성공한 페이지만 `page_manifest` / `page_blocks`에서 교체한다.
5. 보조 파서 실행 실패 시, `strict: false`이면 기본 결과를 유지하고 `parse_report.md`에 fallback 이유를 남긴다.

## 실행 예시

```powershell
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/exp_parser_odl_local.yaml
python -m src.main build-indexes --config configs/exp_parser_odl_local.yaml
python -m src.main eval --config configs/exp_parser_odl_local.yaml --baseline-label baseline_odl_local
```

Hybrid 모드:

```powershell
opendataloader-pdf-hybrid --port 5002
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/exp_parser_odl_hybrid.yaml
```

## 확인 포인트

- `outputs/<run_id>/parse_report.md`
  - `Parser Engines`
  - `Auxiliary Parser`
- `data/processed/entries.jsonl`
  - `knowledge` 페이지의 `table_headers`, `key_points`, `page_summary`
- `outputs/<run_id>/grounding_details.csv`
  - multi-page grounding failure 감소 여부
- `outputs/<run_id>/multi_page_eval.md`
- `outputs/<run_id>/multi_page_dummy_eval.md`

## 주의

- 현재 SafetyCompanion 2026 PDF는 tagged PDF가 아니므로 `use_struct_tree` 이득은 제한적이다.
- `abbreviations`, `calendar`, `index` 추출기는 고정폭 `raw_text` 전제를 많이 사용하므로 1차 실험 범위에서 제외한다.
