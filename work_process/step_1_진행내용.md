# Step 1. 원본 PDF 감사 및 RAG 범위 정의

## 목표
`data/SafetyCompanion-2026.pdf`의 실제 구조와 편집 패턴을 먼저 감사하고, 어떤 페이지를 RAG 본문 코퍼스로 포함할지와 어떤 페이지를 보조 룩업 또는 제외 대상으로 둘지를 명확히 정의한다.

## 선행조건
- 없음

## 확인된 문서 특성
1. 원본 PDF는 **224페이지, A5 규격**의 카탈로그형 문서다.
2. 텍스트 레이어가 존재하므로 기본 추출은 가능하지만, 일부 표형 페이지와 이미지 중심 페이지는 추출 품질이 낮다.
3. 문서는 연속 보고서가 아니라 아래처럼 **반복 템플릿이 강한 혼합형 편집물**이다.
- 1-14: 표지, 광고, Navigator, Seminar Guide, 목차, Preface, Benefits, In-house 안내
- 15-128: `Passive Safety` 중심 본문
- 129-140: `Dummy & Crash Testing`
- 141-204: `Active Safety & Automated Driving`
- 205-214: `Simulation & Engineering`
- 215-217: `Important Abbreviations`
- 218: `Terms & Conditions`
- 219-220: `Index`
- 221: `Advertisers Directory`
- 222-223: `Seminar Calendar`
- 224: 후면 광고성 페이지
4. 본문 페이지는 크게 `seminar`, `event`, `SafetyWissen knowledge`, `calendar`, `abbreviations`, `index`, `advertisement/image-heavy`로 나뉜다.
5. 목차와 본문에 쓰인 페이지 번호는 **PDF 페이지 인덱스와 완전히 같지 않다**. 따라서 `pdf_page`와 `printed_page`를 분리해 저장해야 한다.
6. 표지 성격의 앞쪽 페이지만 보면 `Simulation & Engineering` 섹션이 누락되어 보일 수 있으므로, 실제 범위 정의는 **표지보다 목차와 페이지 본문**을 우선한다.
7. 일부 페이지는 같은 페이지 안에 여러 세미나/워크숍이 공존하거나, 하나의 이벤트가 2페이지 이상 이어진다. 따라서 `page`와 `entry`를 동일 개념으로 취급하면 안 된다.

## 핵심 설계 판단
1. RAG 주 코퍼스는 `seminar`, `event`, `knowledge`, `abbreviations`, `index`를 중심으로 구축한다.
2. `calendar`는 일정 질의 대응을 위한 **보조 룩업 코퍼스**로 유지하되, 최종 답변은 반드시 세미나/이벤트 원문 페이지로 다시 backfill한다.
3. `advertisement`, `benefits`, `terms`, `advertisers directory`는 기본 검색 코퍼스에서 제외한다.
4. 텍스트가 거의 없거나 레이아웃이 심하게 깨지는 페이지도 `page_manifest`에서는 반드시 누락 없이 관리한다.
5. 답변은 항상 **근거 페이지와 제목을 함께 제시**하고, 장문 원문 복사는 피한다.

## 필수 작업
1. 원본 PDF 프로파일 문서를 작성한다.
- 전체 페이지 수
- 섹션 범위
- 페이지 유형 taxonomy
- 반복 레이아웃 특징
- 추출 난이도 높은 페이지 유형

2. 페이지 맵을 만든다.
- `pdf_page`
- `printed_page`
- `section_l1`
- `page_type_guess`
- `has_text_layer`
- `low_text_flag`
- `is_primary_corpus`
- `notes`

3. 포함/제외 정책을 문서화한다.
- RAG 본문 코퍼스 포함 대상
- 보조 룩업 대상
- 검색 제외 대상
- 답변 허용 범위

4. 수동 검토용 샘플 페이지 세트를 선정한다.
- 세미나 템플릿 대표 페이지
- 이벤트 대표 페이지
- SafetyWissen 표형 페이지
- 다중 엔트리 페이지
- 광고/저텍스트 페이지
- 약어/색인/캘린더 페이지

5. 목차 기준 페이지 참조가 실제 본문과 맞는지 교차 검증한다.

## Codex 작업 지시
- `pdfinfo`, 텍스트 추출, 필요 시 렌더링 검토를 통해 실제 문서 구조를 먼저 고정하라.
- `pdf_page`와 `printed_page`의 이중 페이지 체계를 모든 후속 단계의 공통 키로 채택하라.
- 광고성 페이지와 본문 페이지를 혼동하지 않도록 `is_primary_corpus` 규칙을 명문화하라.
- 이후 단계가 그대로 참조할 수 있을 정도로 구체적인 `source_page_map` 초안을 작성하라.

## 완료 기준
- 전체 224페이지에 대한 범위와 유형 가설이 정리됨
- 포함/제외 정책이 문서화됨
- `printed_page` 매핑 정책이 확정됨
- 후속 파싱 단계가 참고할 샘플 검토 세트가 확보됨

## 산출물
- `docs/source_document_profile.md`
- `docs/rag_scope.md`
- `data/raw/source_page_map.jsonl`
- `outputs/<run_id>/source_audit_report.md`

## 검증 포인트
- 문서의 실제 섹션 범위가 표지/목차/본문 기준으로 일관되게 설명되는가
- `Simulation & Engineering` 구간이 누락되지 않았는가
- `calendar`, `index`, `advertisement`의 역할이 명확히 분리되었는가
- 후속 단계가 `pdf_page`와 `printed_page`를 혼동하지 않도록 정의되었는가
