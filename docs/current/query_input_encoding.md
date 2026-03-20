# Query Input Encoding

## Why This Exists

Manual Korean input in PowerShell can produce mojibake when the console encoding path does not match UTF-8 expectations.

## Safe CLI Usage

Prefer:

```powershell
python -m src.main query --question-file path\\to\\question.txt --config configs\\exp_graph.yaml
```

with the question file saved as UTF-8.

## Guardrail

The CLI now:

- supports `--question-file`
- emits a warning when the query string looks encoding-corrupted

This reduces false regressions caused by console input corruption rather than model or retrieval behavior.
