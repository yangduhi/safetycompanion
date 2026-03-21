# Graph Interactive vs Batch Diff Report

## Conclusion

The previously observed mismatch between interactive snapshots and batch graph eval was **not** caused by a route/eval harness divergence.

The main cause was:

- manual shell-entered Korean query text was corrupted by the PowerShell console encoding path
- batch eval used the UTF-8 query loaded from `data/eval/graph_hard_questions.jsonl`

Once the interactive check used the same file-loaded query string, the route behavior aligned with batch eval.

## What Was Verified

### Passive Safety

- manual shell literal query could drift into mojibake and produce misleading interactive results
- file-loaded query from `graph_hard_questions.jsonl` now resolves to:
  - page `18` at top
- latest batch eval run:
  - `outputs/20260320-210219_90cd5e6d`
  - `G007` top result: page `18`

### Automated Driving

- file-loaded query resolves to:
  - page `145` at top
  - page `142` immediately behind it
- latest batch eval run:
  - `outputs/20260320-210219_90cd5e6d`
  - `G008` top result: page `145`

## Latest Graph Metrics

From `outputs/20260320-210219_90cd5e6d/graph_eval.md`:

- `graph_backfill_success_rate = 1.0`
- `graph_grounded_success_rate = 0.875`
- `graph_route_top1_hit_rate = 0.75`
- `graph_route_top3_hit_rate = 0.875`

## Remaining Failure

The remaining graph failure is currently:

- `G004 Euro NCAP`

So the next graph lane question is no longer measurement consistency.
It is now a pure entity-lane representative / typing issue.
