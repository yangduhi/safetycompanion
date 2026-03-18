# Data Contract

## Common IDs
- `document_id`: fixed document identifier
- `pdf_page`: physical page number in the PDF
- `printed_page`: printed page number inside the document, nullable
- `entry_id`: unique retrieval unit identifier
- `entry_bundle_id`: bundle for multi-page or grouped entries
- `chunk_id`: retrieval chunk identifier
- `run_id`: execution identifier

## File Formats
- Record datasets use `jsonl`
- Config files use `yaml`
- Reports use `md`, `csv`, or `jsonl`

## Page Manifest
Required fields:
- `document_id`
- `pdf_page`
- `printed_page`
- `page_type`
- `section_l1`
- `title`
- `text`
- `word_count`
- `is_primary_corpus`
- `extraction_quality`
- `page_bundle_role`

## Entry Record
Required fields:
- `document_id`
- `entry_id`
- `entry_bundle_id`
- `entry_type`
- `title`
- `section_l1`
- `source_pages`
- `printed_pages`
- `summary`
- `fields`

## Chunk Record
Required fields:
- `chunk_id`
- `entry_id`
- `entry_bundle_id`
- `chunk_type`
- `pdf_page`
- `printed_page`
- `title`
- `field_name`
- `text`

## Citation Rule
All end-user answers must include:
- title
- `pdf_page`
- `printed_page` if available
