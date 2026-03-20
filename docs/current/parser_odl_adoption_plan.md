# OpenDataLoader PDF Adoption Plan

작성 기준일: 2026-03-20

## 1. 목적

이 문서는 SafetyCompanion에 `opendataloader-pdf`를 **기본 파서 교체가 아니라 `knowledge` 페이지 전용 실험 보조 파서**로 도입하기 위한 운영 계획서다.

핵심 원칙은 아래와 같다.

1. `prod` 파서는 계속 `pdftotext -layout`를 유지한다.
2. ODL는 `knowledge` / layout-heavy 페이지에만 제한 적용한다.
3. `abbreviation`, `calendar`, `index` 추출기는 1차 실험 범위에서 제외한다.
4. 실험 평가는 parser 품질 자체보다 downstream grounding 영향까지 함께 본다.

## 2. 현재 상태

현재 기본 경로:

- parser: `pdftotext -layout`
- entry extraction: line-based heuristic
- `knowledge` 페이지는 표/목록 구조가 평탄화되는 경우가 많음

현재 보조 파서 상태:

- [opendataloader_parser.py](/D:/vscode/safetycompanion/src/parse/opendataloader_parser.py)
- [pdf_parser.py](/D:/vscode/safetycompanion/src/parse/pdf_parser.py)
- [ingest.py](/D:/vscode/safetycompanion/src/workflows/ingest.py)
- [test_aux_parser.py](/D:/vscode/safetycompanion/tests/test_aux_parser.py)

즉, 코드는 이미 존재하고 현재 필요한 것은 **실험 레인을 안정적으로 운영하는 계획과 config 기준**이다.

## 3. 도입 범위

### 포함

- `knowledge` 페이지
- layout-heavy / table-heavy 페이지
- selected page-type auxiliary parser dispatch

### 제외

- `seminar`
- `event`
- `abbreviations`
- `calendar`
- `index`

## 4. 실행 설정

공통 실험 config:
- [exp_parser_odl.yaml](/D:/vscode/safetycompanion/configs/exp_parser_odl.yaml)

local heuristic 실험:
- [exp_parser_odl_local.yaml](/D:/vscode/safetycompanion/configs/exp_parser_odl_local.yaml)

hybrid 실험:
- [exp_parser_odl_hybrid.yaml](/D:/vscode/safetycompanion/configs/exp_parser_odl_hybrid.yaml)

whitelist 실험:
- [exp_parser_odl_whitelist.yaml](/D:/vscode/safetycompanion/configs/exp_parser_odl_whitelist.yaml)

## 5. 전제 조건

### 로컬 환경

- Python 3.11 확인됨
- `java` 미설치
- `opendataloader-pdf` 미설치
- PDF 메타데이터:
  - `Tagged: no`

의미:
- 현재 문서군에서는 `use_struct_tree`보다 heuristic / hybrid path가 더 중요하다.
- 실험 전 Java 11+와 `opendataloader-pdf` 설치를 먼저 확인해야 한다.

## 6. 실행 단계

### Phase P0. 환경 준비

- Java 11+ 설치 확인
- `opendataloader-pdf` 설치 확인
- `opendataloader-pdf --help` 동작 확인

### Phase P1. Local heuristic 실험

명령:

```powershell
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/exp_parser_odl_local.yaml
python -m src.main build-indexes --config configs/exp_parser_odl_local.yaml
python -m src.main eval --config configs/exp_parser_odl_local.yaml
```

초기 비교 대상:
- `p.60-62`
- `p.84-85`
- `p.129`
- `p.137`

### Phase P1-W. Whitelist 실험

명령:

```powershell
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/exp_parser_odl_whitelist.yaml
python -m src.main build-indexes --config configs/exp_parser_odl_whitelist.yaml
python -m src.main eval --config configs/exp_parser_odl_whitelist.yaml
```

의도:
- `knowledge` 전체가 아니라 우선 개선 가능성이 높은 페이지군에만 보조 파서를 적용
- parser 품질 향상이 downstream grounding에도 실제로 도움이 되는지 측정

### Phase P2. Hybrid 실험

명령:

```powershell
python -m src.main ingest --pdf data/SafetyCompanion-2026.pdf --config configs/exp_parser_odl_hybrid.yaml
python -m src.main build-indexes --config configs/exp_parser_odl_hybrid.yaml
python -m src.main eval --config configs/exp_parser_odl_hybrid.yaml
```

### Phase P3. 적용 범위 재조정

만약 전체 `knowledge` 적용이 noisy하면:
- whitelist page군만 재파싱
- 또는 `min_word_count` / page type 조건을 더 보수적으로 조정

## 7. 평가 기준

### parser-level

- `table_headers` 안정성
- `key_points` 품질
- `page_summary` 대표성
- reading order 보존

### downstream-level

- `grounding_details.csv`
- `multi_page_eval.md`
- `multi_page_dummy_eval.md`
- `knowledge_table_chunk` 품질

## 8. 성공 기준

- `knowledge` 페이지의 table/list fidelity 개선
- `page_summary` 품질 개선
- downstream grounding failure 감소
- 기본 `prod` 경로 regression 없음

## 9. 롤백 규칙

- ODL 실험은 `prod`를 덮어쓰지 않는다.
- 실험 결과가 불안정하면 auxiliary parser를 끈 config로 즉시 복귀한다.
- `strict: false`를 기본으로 유지해 parser 실패 시 기본 결과를 보존한다.

## 10. 최종 판단

SafetyCompanion에서 ODL는 “새 기본 파서”가 아니라, **`knowledge` 페이지용 실험 보조 파서**가 맞다.

따라서 최적의 다음 단계는:
1. 환경 준비
2. local heuristic 실험
3. hybrid 비교
4. whitelist 또는 gating 재조정
