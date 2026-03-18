# Ops Playbook

## Standard Run
```powershell
python -m src.main preflight
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml
python -m src.main build-indexes --config configs/prod.yaml
python -m src.main eval --config configs/prod.yaml
```

## Query
```powershell
python -m src.main query "FMVSS 305a 관련 세미나를 찾아줘" --config configs/prod.yaml
```

## Rebuild Rules
- If parsing logic changes, rerun ingest and build-indexes
- If chunking or retrieval logic changes, rerun build-indexes
- If evaluation logic changes, rerun eval

## Failure Handling
- Keep failed runs under `outputs/<run_id>/`
- Do not overwrite successful runs
- Check `preflight_report.md`, `parse_report.md`, and `eval_summary.md` first
