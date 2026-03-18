# Acceptance Criteria

## Baseline Gates
- Page manifest coverage: `224 / 224`
- Seminar and event title extraction accuracy: `>= 0.98`
- Abbreviation exact-match accuracy: `>= 0.95`
- Retrieval Recall@10: `>= 0.85`
- Citation page hit rate: `>= 0.95`
- Compare and recommendation grounded success rate: `>= 0.80`

## Guardrails
- Answers without citations are failures
- Answers using advertisement pages as evidence are failures
- `pdf_page` and `printed_page` confusion is a failure

## Operational Readiness
- `python -m src.main preflight` succeeds
- `python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/prod.yaml` succeeds
- `python -m src.main build-indexes --config configs/prod.yaml` succeeds
- `python -m src.main query "<question>" --config configs/prod.yaml` returns grounded output
- `python -m src.main eval --config configs/prod.yaml` writes evaluation artifacts
