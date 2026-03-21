# Euro NCAP Entity Relation Stabilization

## Goal

Improve `entity_relation_lookup` so a query for `Euro NCAP` prefers a representative Euro NCAP entry over:

- broad NCAP overview pages
- multi-program list pages
- highly specific subtopic/protocol pages

## Observed Confusion

Earlier ranking behavior mixed together:

- exact Euro NCAP entries
- broad `NCAP` overview entries
- multi-standard pages (`U.S. NCAP`, `JNCAP`, `KNCAP`, `C-NCAP`, `GTR`, `UN R127`)
- narrow Euro NCAP subtopic pages (`safe driving`, `crash avoidance`, `protocol`, `matrix`)

## Current Heuristics

### Chunk selection

For `entity_relation_lookup` with `standard_topic_relation`, preferred backfill fields are now:

1. `description`
2. `overview`
3. `page_summary`
4. `knowledge_topic`
5. `course_description`
6. `keyword`
7. `facts`

This shifts representative summaries away from generic `page_summary` chunks when a stronger `description` or `overview` exists.

### Ranking

Current scoring adds:

- boost for exact `Euro NCAP` title matches
- extra boost for titles starting with:
  - `Euro NCAP UpDate ...`
  - `Euro NCAP - Compact Course ...`

Current scoring subtracts for:

- broad overview patterns:
  - `NCAP-Tests`
  - `New Car Assessment Programs`
- multi-standard list titles:
  - `U.S. NCAP`
  - `JNCAP`
  - `KNCAP`
  - `C-NCAP`
  - `ASEAN NCAP`
  - `Global NCAP`
  - `LATIN NCAP`
  - `GTR`
  - `UN R127`
- narrow supporting pages:
  - `protocol`
  - `matrix`
  - `frontal impact`
  - `side impact`
  - `whiplash`
  - `pedestrian protection`
  - `crash avoidance`
  - `post-crash`
  - `vehicle assistance`
  - `occupant monitoring`
  - `driver engagement`
  - `commercial van`
  - `truck rating`

## Snapshot After Adjustment

Targeted query: `Find entries related to Euro NCAP`

Top 5:

1. `Euro NCAP UpDate 2026 Get ready for Euro NCAP‘s latest rating revision!` (p.40)
2. `Euro NCAP - Compact Course Description Course Contents` (p.46)
3. `Wissen SafetyWissen.com Euro NCAP / ANCAP Frontal Impact Test Matrix` (p.47)
4. `SafetyWissen.com Wissen Euro NCAP / ANCAP Frontal Impact` (p.50)
5. `Wissen SafetyWissen.com Euro NCAP / ANCAP Frontal Impact` (p.53)

This is closer to the intended representative-vs-supporting split than the prior behavior where broad or mixed NCAP pages dominated.
