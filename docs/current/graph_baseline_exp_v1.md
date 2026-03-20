# Graph Baseline Exp V1

## Meaning

Stable experimental graph baseline after:

- `Euro NCAP` exact-entity typing / tiering
- `G002` triage alignment
- `Passive Safety` representative stabilization
- `Automated Driving` representative stabilization

## Reference Run

- `outputs/20260320-232620_90cd5e6d`

## Contract Notes

- main graph hard set:
  - `data/eval/graph_hard_questions.jsonl`
- `G002` is interpreted under the current answer contract as
  - "entries where both entities appear together"
  - not strictly "knowledge-only pages"
- for interpretation-only backstop, see:
  - `data/eval/graph_hard_questions_strict_knowledge_only.jsonl`

## Linked Triage / Specs

- `docs/branches/codex__graphrag-g2s-route-decomposition/g002_case_report.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/euro_ncap_entity_typing_spec_v2.md`
- `docs/branches/codex__graphrag-g2s-route-decomposition/euro_ncap_tiering_policy.md`

## Key Metrics

- `graph_route_top1_hit_rate = 1.0`
- `graph_route_top3_hit_rate = 1.0`
- `graph_backfill_success_rate = 1.0`
- `graph_grounded_success_rate = 1.0`
- `graph_regression_on_mainline = 0.0`

## Hard-Set Status

- `G001` pass
- `G002` pass
- `G003` pass
- `G004` pass
- `G005` pass
- `G006` pass
- `G007` pass
- `G008` pass

## Companion Parser Status

ODL remains a separate whitelist-only experimental parser lane.
It is **not** part of this graph baseline promotion decision.

## Git Freeze Guidance

Create a git tag such as `graph-baseline-exp-v1` only after the current code-only baseline commit is created.
Do not tag the dirty worktree state directly.
