# Euro NCAP Entity Typing Spec V2

## Goal

Treat `Euro NCAP` as an exact entity lane, not as a generic NCAP cluster.

## Canonical Categories

### Tier A. `EURO_NCAP_EXACT`

Representative candidates:

- `Euro NCAP UpDate 2026 Get ready for Euro NCAP‘s latest rating revision!`
- `Euro NCAP - Compact Course Description Course Contents`

### Tier B. `NCAP_BROAD_OVERVIEW`

Broad overview candidates:

- pages that explain multiple NCAP programs together
- `NCAP-Tests in Europe, America and Australia`
- `NCAP - New Car Assessment Programs ...`

### Tier C. `NCAP_SIBLING_PROGRAM`

Sibling programs:

- `U.S. NCAP`
- `JNCAP`
- `KNCAP`
- `C-NCAP`
- `ASEAN NCAP`
- `LATIN NCAP`
- `GLOBAL NCAP`
- `Bharat NCAP`

### Tier D. `NCAP_SUPPORTING_CONTEXT`

Supporting pages:

- matrix
- protocol
- rating composition
- frontal/side/whiplash/pedestrian/crash-avoidance detail pages

## Operational Rule

- Tier A is eligible for `representative`
- Tiers B/C/D are `supporting` only

## Latest Outcome

Main graph hard set `G004` now resolves to:

- page `40`
- title `Euro NCAP UpDate 2026 Get ready for Euro NCAP‘s latest rating revision!`

This closes `G004` under the updated exact-entity semantics.
