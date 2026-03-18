# Error Taxonomy Spec

## 목적
남아 있는 실패를 감이 아니라 구조화된 분류 체계로 기록하고 집계한다.

## 필수 taxonomy
- `ROUTE_WRONG`
- `ANCHOR_NORMALIZATION_FAIL`
- `DISAMBIGUATION_FAIL`
- `COMPARE_ROUTE_MISS`
- `EVENT_PARAPHRASE_MISS`
- `MULTI_PAGE_COLLAPSE`
- `GROUNDING_POLICY_FAIL`

## 분류 원칙
- route가 질문 의도와 어긋나면 `ROUTE_WRONG`
- exact code / title anchor가 복원되지 않으면 `ANCHOR_NORMALIZATION_FAIL`
- top-10은 맞지만 top-1이 틀리면 `DISAMBIGUATION_FAIL`
- compare 질문이 compare route를 타지 못하면 `COMPARE_ROUTE_MISS`
- event paraphrase가 event route를 타지 못하면 `EVENT_PARAPHRASE_MISS`
- multi-page 질문이 single-like collapse를 보이면 `MULTI_PAGE_COLLAPSE`
- page는 맞는데 answer 정책 때문에 grounded 실패면 `GROUNDING_POLICY_FAIL`
