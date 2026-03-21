# Passive Safety Representative Spec

## Goal

Make `topic_cluster_lookup` return a foundational Passive Safety representative entry instead of merely related seminars or events.

## Representative Preference

Prefer:

1. `Introduction to Passive Safety`
2. `International Safety and Crash-Test Regulations`
3. broad foundational seminars with explicit Passive Safety framing

Demote:

- summit / conference style event pages
- homologation or self-certification side topics when they outrank foundational entries
- narrow technical subtopics such as:
  - `Side Impact`
  - `Pedestrian Protection`
  - `Whiplash`
  - `Child Protection`

## Implemented Changes

- top explicit topic hits are now preserved as seed candidates before rerank
- topic-specific boosts now use text as well as title
- summit/event style pages receive stronger penalties
- foundational Passive Safety phrasing receives stronger boosts

## Latest Result

File-loaded `G007` query now returns:

1. page `18`
2. page `20`

This is the intended representative ordering for the current hard set.
