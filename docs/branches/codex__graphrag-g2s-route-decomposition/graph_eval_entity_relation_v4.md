# Graph Eval Entity Relation V4

Latest entity-lane batch eval comes from:

- `outputs/20260320-210219_90cd5e6d/graph_eval_entity_relation.md`

## Metrics

- `graph_backfill_success_rate = 1.0`
- `graph_grounded_success_rate = 0.8333`
- `graph_route_top1_hit_rate = 0.6667`
- `graph_route_top3_hit_rate = 0.8333`
- `graph_regression_on_mainline = 0.0`

## Status

- `FMVSS 208`: passing
- `Humanetics Europe GmbH`: passing
- `GlobalAutoRegs.com`: passing
- `Euro NCAP`: remaining failure

## Interpretation

The entity lane is now largely stable.
The remaining work is concentrated in `G004 Euro NCAP`, which is now clearly a representative / typing problem rather than a general graph-retrieval problem.
