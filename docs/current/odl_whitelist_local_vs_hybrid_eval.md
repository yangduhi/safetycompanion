# ODL Whitelist Local vs Hybrid Eval

## Scope

- parser lane only
- target pages: `60, 61, 62, 84, 85, 129, 137`
- comparison modes:
  - baseline (`pdftotext` only)
  - ODL full local
  - ODL whitelist local
  - ODL whitelist hybrid

## Runs

- baseline eval:
  - `outputs/20260318-230159_90cd5e6d`
- ODL full local:
  - ingest `outputs/20260320-154702_90cd5e6d`
  - eval `outputs/20260320-154811_90cd5e6d`
- ODL whitelist local:
  - ingest `outputs/20260320-200602_90cd5e6d`
  - eval `outputs/20260320-200653_90cd5e6d`
- ODL whitelist hybrid:
  - ingest `outputs/20260320-201141_90cd5e6d`
  - eval `outputs/20260320-201235_90cd5e6d`

## Summary Table

| mode | ODL reparsed pages | grounded_success_rate | multi_page_hard__grounded_success_rate | GROUNDING_POLICY_FAIL | note |
| --- | ---: | ---: | ---: | ---: | --- |
| baseline | 0 | 1.0 | 0.6667 | 4 | `pdftotext` only |
| ODL full local | 127 | 1.0 | 0.6667 | 4 | broad knowledge-wide experiment |
| ODL whitelist local | 7 | 1.0 | 0.6667 | 4 | whitelist dispatch worked as intended |
| ODL whitelist hybrid | 0 | 1.0 | 0.6667 | 4 | hybrid CLI failed and fell back to `pdftotext` |

## Parse Engine Observations

- ODL full local:
  - `opendataloader: 127`
  - `pdftotext: 97`
- ODL whitelist local:
  - `opendataloader: 7`
  - `pdftotext: 217`
- ODL whitelist hybrid:
  - `pdftotext: 224`
  - `fallback_reason: OpenDataLoader invocation failed: Error running opendataloader-pdf CLI. Return code: 1`

## Interpretation

- whitelist dispatch is functioning correctly
- local ODL is usable on this machine
- hybrid mode is not yet usable in the current environment/config
- the previously suspected `GROUNDING_POLICY_FAIL: 4` is **not introduced by ODL**
- aggregate retrieval and grounding metrics are effectively unchanged across baseline, full-local, and whitelist-local runs

## Decision

- keep ODL as an experimental auxiliary parser lane
- keep the scope narrow with whitelist dispatch
- do **not** expand to all `knowledge` pages based on aggregate metrics alone
- next parser step should focus on page-level extraction fidelity and page-specific downstream grounding checks, not on global retrieval metrics
