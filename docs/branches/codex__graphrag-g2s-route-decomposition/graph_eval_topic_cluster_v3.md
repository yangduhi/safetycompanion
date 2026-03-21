# Graph Eval Topic Cluster V3

## Latest Batch Eval

From `outputs/20260320-202645_90cd5e6d`:

- `graph__retrieval_top1_hit_rate__type__topic_cluster_relation = 0.5`
- `graph__retrieval_top3_hit_rate__type__topic_cluster_relation = 0.5`
- `graph__grounded_success_rate__type__topic_cluster_relation = 0.5`

Remaining batch failures:

- `G007 Passive Safety`
- `G004 Euro NCAP` is still an entity-lane issue, not a topic-cluster issue

## Targeted Query Snapshots

### Passive Safety

Interactive `QueryService.retrieve(...)` snapshot now surfaces:

1. page `18` — `Introduction to Passive Safety ...`

This is closer to the intended representative result than earlier behavior.

### Automated Driving

Interactive `QueryService.retrieve(...)` snapshot now surfaces:

1. page `142` — `Briefing on the Worldwide Status of Automated Vehicle Policies ...`

This matches the intended representative lane much better than the earlier seminar/event mix.

## Important Note

There is still an observed discrepancy between:

- direct interactive query snapshots
- batch graph-eval route details

Until that discrepancy is fully resolved, topic-cluster progress should be interpreted using both:

- batch eval metrics
- targeted query snapshots

## Current Assessment

- `Automated Driving` representative selection improved materially
- `Passive Safety` is moving in the right direction but still needs further stabilization in batch eval
