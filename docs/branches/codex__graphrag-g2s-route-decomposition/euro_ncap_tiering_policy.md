# Euro NCAP Tiering Policy

## Retrieval Policy

For an exact `Euro NCAP` query, ranking priority is:

1. representative exact entity page
2. compact / update page
3. broad overview
4. sibling NCAP program
5. matrix / protocol / supporting context

## Answer Policy

Entity-lane answers now separate:

- `representative`
- `supporting`

The answer path returns:

1. representative entry
2. supporting entries

It no longer presents broad overview or sibling program pages at the same level as the representative page.

## Why This Matters

Without tiering, `Euro NCAP` competes against:

- multi-program overview pages
- sibling NCAP programs
- supporting matrix/protocol pages

Even though they are related, they are not equally suitable as the primary answer.

## Current Status

- `G004` in the main graph hard set is now passing
- `euro_ncap_micro_suite.jsonl` is available for focused regression checks
- latest micro-suite report shows no remaining confusion failures
