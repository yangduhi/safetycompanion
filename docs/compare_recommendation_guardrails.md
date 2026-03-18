# Compare and Recommendation Guardrails

## Compare
- 최소 2 evidence 필요
- 가능하면 서로 다른 entry에서 evidence를 가져온다
- 근거가 1개뿐이면 비교 답변을 확정적으로 작성하지 않는다

## Recommendation
- 추천 사유 2개 이상 필요
- source 2개 이상이 없으면 보수 응답을 사용한다

## 보수 응답 예시
- `비교를 위한 문서 근거가 충분하지 않음`
- `추천 가능하지만 문서 근거가 충분하지 않음`

## 리포트 요구사항
`grounding_details.csv`에는 아래를 포함한다.
- `evidence_count`
- `multi_page_used`
- `route_name`
- `selected_field`
