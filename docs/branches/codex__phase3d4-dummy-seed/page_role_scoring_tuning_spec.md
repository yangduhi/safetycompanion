# Page Role Scoring Tuning Spec

## Roles
- `landscape_page`
- `overview_page`
- `spec_page`
- `detail_page`
- `training_page`
- `reference_page`

## Role Intent
- `landscape_page`
  - current dummy landscape, overview matrix, broad family map
- `spec_page`
  - calibration, dimensions, qualification, technical reference
- `detail_page`
  - THOR / HIII / ATD specific content
- `training_page`
  - seminar or partner training page
- `reference_page`
  - index or entity list

## Scoring Intent
- 좋은 group은 role 조합이 자연스럽다.
- seed는 role prior를 크게 반영한다.
- secondary는 role compatibility를 크게 반영한다.
- answer는 항상 `page list -> page role -> summary` 순서를 유지한다.
