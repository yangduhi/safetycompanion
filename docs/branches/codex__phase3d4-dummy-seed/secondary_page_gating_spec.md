# Secondary Page Gating Spec

## Goal
seed page 뒤에 붙는 secondary page를 더 보수적으로 고른다.

## Acceptance Rules
- candidate는 seed 또는 query의 anchor family와 겹쳐야 한다.
- role compatibility가 음수면 기본적으로 제외한다.
- `NCAP` page는 hard reject한다.
- training page는 query가 training hint를 포함하지 않으면 soft penalty를 준다.

## Positive Pairs
- `landscape_page + spec_page`
- `landscape_page + detail_page`
- `overview_page + spec_page`
- `spec_page + detail_page`
- `detail_page + training_page`

## Negative Pairs
- `dummy + unrelated seminar`
- `dummy + NCAP overview`
- `reference_page` secondary

## Debug Fields
- `accepted_secondary_pages`
- `rejected_secondary_pages`
- `seed_page_selected`
- `seed_score`
- `page_role_summary`
