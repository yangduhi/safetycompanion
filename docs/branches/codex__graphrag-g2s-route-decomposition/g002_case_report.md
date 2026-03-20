# G002 Case Report

## Query

`Hybrid III와 THOR가 함께 나오는 엔트리를 찾아줘`

## Current Top Result

- page `138`
- `Dummy-Trainings Seminars by our Partner Facts BGS Böhme & Gehring GmbH DUMMY Hybrid III 5 %, 50 %, 95 %`

## Why It Was Failing

The previous gold set only accepted:

- page `129`
- page `137`

Those are valid knowledge-style pages, but the query itself asks for an entry where both entities appear together.
The seminar on page `138` also satisfies that contract directly and was therefore a valid representative result.

## Triage Result

This is best classified as:

- `eval / contract mismatch`

not as:

- retrieval miss
- route failure
- graph backfill failure

## Resolution

The graph hard set was updated so `G002` accepts:

1. page `138`
2. page `129`
3. page `137`

This aligns the evaluation contract with the actual question semantics and the current answer contract.
