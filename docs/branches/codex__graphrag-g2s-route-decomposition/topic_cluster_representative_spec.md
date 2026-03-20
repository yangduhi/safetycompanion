# Topic Cluster Representative Ranking

## Problem

`topic_cluster_lookup` is not a pure graph traversal problem.
It is a representative-selection problem over a topic-filtered candidate pool.

## Current Lane Rule

- base retrieval creates candidates
- topic filters and explicit topic hits enrich them
- graph acts only as a validator / support signal
- final ranking should prefer representative entries over merely related ones

## Representative Criteria

### Positive signals

- strong topic phrase overlap
- overview / course-description / description fields
- foundational seminar or knowledge pages
- topic-defining phrasing in title or text

### Negative signals

- narrowly scoped protocol / matrix pages
- cluster-adjacent event pages
- highly specific subtopic pages when the query asks for a core topic entry

## Current Topic-Specific Heuristics

### Passive Safety

Prefer:

- `Introduction to Passive Safety`
- `International Safety and Crash-Test Regulations`

Demote:

- summit / conference pages
- narrow subtopic pages (`side impact`, `pedestrian protection`, `whiplash`, `child protection`)
- `Basics of Homologation` as a supporting page rather than the cluster representative

### Automated Driving

Prefer:

- `Briefing on the Worldwide Status of Automated Vehicle Policies`
- `The requirements by New Car Assessment Programs regarding safety-supporting driver assistance systems for passenger cars`
- `Levels of Driving Automation`

Demote:

- `Experts' Dialogue` event pages
- highly generic or subtopic-specific technical pages unless they are the only strong candidates

## Current Snapshot

- `Passive Safety` now surfaces page `18` as the top representative in targeted query checks
- `Automated Driving` now surfaces page `142` at the top
- page `145` is present as a strong explicit candidate and should be monitored in the next full graph eval
