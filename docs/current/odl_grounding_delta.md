# ODL Grounding Delta

## Key Finding

`GROUNDING_POLICY_FAIL: 4` is present in:

- baseline `pdftotext` eval
- ODL full local eval
- ODL whitelist local eval
- ODL whitelist hybrid fallback eval

This means the current grounding policy failure cluster is **pre-existing** and should not be attributed to the ODL parser lane.

## Numeric Delta

| mode | grounded_success_rate | multi_page_hard__grounded_success_rate | GROUNDING_POLICY_FAIL |
| --- | ---: | ---: | ---: |
| baseline | 1.0 | 0.6667 | 4 |
| ODL full local | 1.0 | 0.6667 | 4 |
| ODL whitelist local | 1.0 | 0.6667 | 4 |
| ODL whitelist hybrid fallback | 1.0 | 0.6667 | 4 |

## Consequence

- parser quality improvements may still exist on specific pages
- however, current aggregate grounding metrics do not show a measurable downstream gain yet
- the next parser question is therefore:
  - do pages `60-62`, `84-85`, `129`, `137` show cleaner field boundaries and more stable extracted fields?

## Recommended Next Parser Check

For each whitelist page, compare:

1. title / heading integrity
2. `table_headers` extraction
3. `key_points` extraction
4. `page_summary` stability
5. downstream citation/answer behavior for queries that actually hit that page

The parser lane should only expand if those page-level checks show practical improvement.
