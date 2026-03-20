# Generated Data Commit Strategy

## Principle

Do not mix generated parser/index artifacts into code-review commits unless the team explicitly wants a baseline freeze.

## Current Working Sets

### Code / config / docs

- parser lane code and configs
- graph ranking code
- experiment docs and branch-scoped specs

### Generated tracked data

- `data/parsed/page_manifest.jsonl`
- `data/parsed/page_blocks.jsonl`
- `data/processed/entries.jsonl`
- `data/processed/chunks.jsonl`

### Runtime-only artifacts

- `data/graph/`
- `outputs/<run_id>/...`

## Recommended Split

1. parser code/config/docs commit
2. graph stabilization code/docs commit
3. generated data freeze commit only if intentionally approved

## Immediate Guidance

- keep `outputs/*` as the source of experiment evidence
- avoid committing `data/graph/`
- if a clean PR is needed, regenerate baseline parser data before staging tracked generated files
