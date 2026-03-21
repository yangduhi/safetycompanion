# ODL Page-Level Comparison

## Scope

Whitelist pages only:

- `60`
- `61`
- `62`
- `84`
- `85`
- `129`
- `137`

Comparison source:

- baseline snapshot from `pdftotext`
- ODL whitelist local reparsing

## Judgement Rule

Each page is tagged as one of:

- `keep_baseline`
- `use_odl_local`
- `needs_more_eval`

The judgement is based on:

1. heading / title specificity
2. field boundary stability
3. table-like structure fidelity
4. page summary readability
5. whether ODL introduces obvious collapse or noise

## Page-by-Page Review

### Page 60

- baseline title: `SafetyWissen.com Wissen Euro NCAP / ANCAP Post-Crash Assessment`
- ODL title: `Euro NCAP / ANCAP Post-Crash Assessment Rescue & Extrication Protocol Version 1.1`
- change:
  - title becomes more specific
  - `knowledge_topic` becomes more faithful to the actual protocol page
  - `key_points` preserves protocol line items more cleanly
- judgement: `use_odl_local`

### Page 61

- baseline title: `Wissen SafetyWissen.com Euro NCAP / ANCAP Post-Crash Assessment`
- ODL title: `Euro NCAP / ANCAP Post-Crash Assessment Vehicle Extrication Energy Management1`
- change:
  - title becomes much more specific
  - `table_headers` improve
  - but several `key_points` lines collapse together more aggressively than desired
- judgement: `needs_more_eval`

### Page 62

- baseline title already strong, but the summary is flattened
- ODL separates:
  - `Safe Driving`
  - `Crash Avoidance`
  - `Crash Protection`
  - `Post-Crash Safety`
  more clearly into readable lines
- judgement: `use_odl_local`

### Page 84

- baseline: flattened `Dummy Region Points Criteria`
- ODL: clearer table progression
  - `Dummy`
  - `Region`
  - `Points`
  - `Criteria`
  and better exposure of `THOR 50 %`
- judgement: `use_odl_local`

### Page 85

- ODL improves passenger / dummy labeling:
  - `Front passenger: THOR 50 %`
  - `Rear passenger (left): H III 50 %`
- however:
  - symbol noise remains
  - row/value composition is still partially collapsed
- judgement: `needs_more_eval`

### Page 129

- baseline layout is flattened and crash directions are interleaved
- ODL reorganizes the page into clearer groups:
  - `Frontal Impact`
  - `Side Impact`
  - `Rear Impact`
  - `Child`
- dummy family grouping is more readable
- judgement: `use_odl_local`

### Page 137

- ODL improves table column separation:
  - `Weight (kg)`
  - `Seating Height (cm)`
  - `Instruction for Calibration`
- `mentioned_entities` also becomes slightly richer (`THOR05F`, `THOR50M`)
- still noisy, but more faithful than baseline
- judgement: `use_odl_local`

## Final Recommendation

- `use_odl_local`: `60, 62, 84, 129, 137`
- `needs_more_eval`: `61, 85`
- `keep_baseline`: none in the current whitelist

This means the current whitelist can stay narrow, but page-level review suggests that pages `61` and `85` should remain under explicit observation if ODL is kept enabled.
