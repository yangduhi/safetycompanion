# Evidence Policy

## 원칙
- 답변은 선택된 evidence field와 span에 근거해야 한다.
- route와 맞지 않는 코퍼스는 최종 후보 상단으로 올라오지 않도록 제한한다.
- page citation만 맞는 상태를 grounded success로 간주하지 않는다.

## Route별 우선 field
- `abbreviation_lookup`: `expansion` > `overview`
- `page_or_index_lookup`: `page_summary` > `knowledge_topic` > `overview` > `keyword` > `facts`
- `seminar_lookup`: `course_description` > `course_objectives` > `course_contents` > `overview` > `facts`
- `event_lookup`: `description` > `overview` > `contents`
- `calendar_lookup`: `course_description` > `description` > `overview` > `schedule`
- `compare_or_recommend`: `course_description` > `course_contents` > `description` > `overview` > `page_summary`
- `relationship_query`: `page_summary` > `description` > `course_description` > `overview` > `keyword`

## Guardrails
- route와 맞지 않는 entry type은 기본적으로 필터링한다.
- compare / recommendation은 최소 2 근거가 없으면 보수 응답한다.
- abbreviation은 자유 생성보다 deterministic template를 우선 사용한다.
