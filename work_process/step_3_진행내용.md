# Step 3. PDF 구조 복원 및 페이지 유형 분류

## 목표
PDF를 단순 텍스트 묶음이 아니라 **페이지 단위 구조 문서**로 복원하고, 모든 페이지를 후속 처리 가능한 형태로 정규화한다.

## 선행조건
- `step_1_진행내용.md` 완료
- `step_2_진행내용.md` 완료

## 핵심 판단
1. 이 문서는 표, 다단 편집, 이벤트 소개, 광고 페이지가 섞인 카탈로그형 PDF이므로, 일반적인 균일 청킹 전에 **페이지 구조 복원**이 먼저 필요하다.
2. `page_manifest`는 텍스트가 적은 페이지도 빠짐없이 가져야 하며, 추출 품질이 낮은 페이지를 분리해 후속 review queue로 보내야 한다.

## 필수 작업
1. PDF 파서 파이프라인을 구현한다.
- 페이지 번호 보존
- 텍스트 블록 추출
- 블록 reading order 추정
- 제목/부제/머리글/바닥글 분리
- 표/리스트/캡션 후보 식별
- 이미지 또는 저텍스트 영역 여부 기록

2. 페이지 타입 taxonomy를 아래처럼 확정한다.
- `cover_or_brand`
- `navigator_or_guide`
- `toc`
- `preface_or_meta`
- `seminar`
- `event`
- `knowledge`
- `abbreviations`
- `index`
- `calendar`
- `terms`
- `advertisers_directory`
- `advertisement`
- `low_text_image`

3. 모든 페이지에 대해 최소 메타데이터를 저장한다.

```json
{
  "pdf_page": 141,
  "printed_page": 141,
  "page_type": "seminar",
  "section_l1": "Active Safety & Automated Driving",
  "title": "Automated Driving - Safeguarding and Market Introduction",
  "text_blocks": [],
  "extraction_quality": "high",
  "is_primary_corpus": true,
  "page_bundle_role": "single_entry"
}
```

4. `page_bundle_role`를 함께 정한다.
- `single_entry`
- `multi_entry`
- `continuation`
- `non_retrieval`

5. 파싱 품질 점검 리포트를 생성한다.
- 전체 페이지 수
- 타입별 페이지 수
- 제목 추출 실패 목록
- 저텍스트 페이지 목록
- 표형 페이지 추출 의심 목록
- 목차/색인/캘린더 참조 충돌 목록

6. 저신뢰 페이지 review queue를 만든다.
- 표가 심하게 깨진 SafetyWissen 페이지
- 텍스트가 없는 광고/이미지 페이지
- 다중 엔트리로 보이는 세미나 페이지
- continuation 판단이 애매한 이벤트 페이지

## 구현 원칙
1. 기본은 text layer 기반 추출로 간다.
2. OCR 또는 vision 기반 보정은 저품질 페이지에만 제한적으로 쓴다.
3. 페이지 분류는 규칙 기반 1차 후 필요 시 경량 LLM 또는 별도 보정기로 2차 정제한다.
4. `pdf_page`와 `printed_page`를 모두 저장하지 않는 레코드는 실패로 본다.

## Codex 작업 지시
- `src/parse/pdf_parser.py`와 `src/parse/page_classifier.py`를 구현하라.
- `data/parsed/page_manifest.jsonl`과 `data/parsed/page_blocks.jsonl`를 분리 저장하라.
- 시각 검토를 위한 `notebooks/01_parse_inspection.ipynb`를 만들고, 핵심 샘플 페이지를 바로 점검할 수 있게 하라.
- 저신뢰 페이지는 `outputs/<run_id>/page_review_queue.json`로 자동 수집하라.

## 완료 기준
- 224페이지 전부에 대한 `page_manifest`가 생성됨
- 페이지 타입과 섹션 분류가 완료됨
- 저신뢰 페이지 queue가 분리됨
- 후속 엔트리 추출이 가능한 수준으로 제목/구조가 복원됨

## 산출물
- `data/parsed/page_manifest.jsonl`
- `data/parsed/page_blocks.jsonl`
- `outputs/<run_id>/parse_report.md`
- `outputs/<run_id>/page_review_queue.json`
- `notebooks/01_parse_inspection.ipynb`

## 검증 포인트
- manifest 페이지 수가 원본 PDF와 정확히 같은가
- `Simulation & Engineering` 구간이 빠지지 않았는가
- `seminar`, `event`, `knowledge`, `calendar`, `advertisement`가 혼동 없이 구분되는가
- 표형 SafetyWissen 페이지의 추출 품질 경고가 누락되지 않았는가
