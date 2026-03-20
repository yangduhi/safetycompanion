# Generated Data Handling

## Current Situation

Parser and graph experiments modify tracked generated files such as:

- `data/parsed/page_manifest.jsonl`
- `data/parsed/page_blocks.jsonl`
- `data/processed/entries.jsonl`
- `data/processed/chunks.jsonl`

This makes it easy to mix:

- code changes
- experiment output changes
- baseline data changes

## Rule

Generated data must be treated as a separate review surface.

## Recommended Workflow

1. make code/doc changes first
2. run experiment and inspect generated data separately
3. keep only baseline-freeze or explicitly approved generated artifacts
4. avoid mixing parser experiment outputs and graph stabilization changes in one commit

## For ODL Experiments

- whitelist/local runs are acceptable as working data for evaluation
- before graph-only evaluation, restore baseline parser output or clearly mark the parser lane in use
- hybrid failures should be documented, not silently ignored

## For Graph Experiments

- graph eval should be run on a known parser baseline unless parser impact is the explicit subject of the experiment

## Commit Guidance

- code/docs commit
- experiment-data freeze commit, only if intentionally preserved
