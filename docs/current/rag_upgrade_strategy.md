# RAG Upgrade Strategy

작성 기준일: 2026-03-18

이 문서는 현재 SafetyCompanion RAG 구현을 분석하고, 외부 연구/산업 자료를 바탕으로 이 프로젝트에 적합한 고도화 방향을 제안한다. 목적은 “유행하는 RAG 기법 나열”이 아니라, 현재 데이터 구성과 실제 병목에 맞는 우선순위를 정하는 것이다.

## 1. 현재 시스템 요약

현재 구현은 아래 구조를 따른다.

- 입력: `data/SafetyCompanion-2026.pdf`
- 파싱/추출: `src/parse`, `src/ingest`
- 검색: `src/retrieval`
- 답변 생성: `src/qa`
- 평가: `src/eval`
- 오케스트레이션: `src/workflows`, `src/cli`

기본 검색 방식은 아래와 같다.

- sparse: BM25
- dense: TF-IDF + SVD 기반 local dense store
- fusion: RRF 계열 결합
- routing: rule-based route 분기
- rerank: heuristic rerank
- answer: deterministic / template-aware grounded answer

즉, 현재 시스템은 “오프라인 우선 + 강한 구조화 + 규칙 기반 통제”에 강점이 있고, 외부 API나 대형 신경 IR 모델에 의존하지 않는다.

## 2. 로컬 분석 결과

아래 수치는 현재 저장소 산출물 기준의 로컬 분석이다.

### 데이터 구성

- 총 페이지 수: `224`
- 주요 `page_type` 분포:
  - `knowledge`: `127`
  - `seminar`: `38`
  - `event`: `12`
  - `advertisement`: `12`
- 주요 `entry_type` 분포:
  - `knowledge`: `127`
  - `seminar`: `38`
  - `event`: `12`
- 총 chunk 수: `1520`
- 주요 `chunk_type` 분포:
  - `field_chunk`: `668`
  - `abbreviation_chunk`: `365`
  - `entry_overview_chunk`: `177`
  - `knowledge_table_chunk`: `127`
  - `index_lookup_chunk`: `95`
  - `calendar_chunk`: `88`

### 파싱 품질

- `high`: `183`
- `medium`: `30`
- `low`: `11`

`knowledge`, `seminar`, `event` 페이지는 대부분 `high`지만, 실제 텍스트 샘플을 보면 일부 `knowledge` 페이지는 표형 구조와 인코딩 노이즈가 섞여 있다. 즉, “평가상 고품질”과 “후속 검색/요약에 이상적인 구조화”는 동일하지 않다.

### chunk 크기 분포

- `entry_overview_chunk`:
  - median: `1877`
  - p90: `3626`
  - max: `8176`
- `field_chunk`:
  - median: `263.5`
  - p90: `1829`
  - max: `8176`

현재는 매우 큰 overview chunk와 짧은 field chunk가 혼재한다. 이 구조는 recall에는 유리할 수 있지만, hard multi-page 질의의 top-1 정렬과 grounded synthesis에는 불리할 수 있다.

### 현재 병목

최신 평가 산출물 기준으로 핵심 병목은 broad retrieval이 아니라 `multi_page_lookup` hard slice다.

- `multi_page_hard__retrieval_top1_hit_rate = 0.8333`
- `multi_page_lookup` 계열의 top-1 miss가 residual failure의 중심
- `grounding_details.csv` 기준 실패 2건 모두 `multi_page_lookup`
- 실패 예시는 `THOR`, `HIII`, `ATD`, `dummy landscape` 관련 페이지 묶음

즉, 현재 시스템은 이미 대부분의 일반 질의에서 매우 강하다. 다음 고도화는 “전체를 갈아엎는 수준의 대수술”보다, multi-page / hybrid-document / hard-ranking 문제를 정확히 겨냥해야 ROI가 높다.

## 3. 병목 해석

현재 프로젝트의 구조와 데이터 특성을 함께 보면 병목은 아래 5개로 정리된다.

### 3.1 표형/혼합형 `knowledge` 페이지의 구조 손실

`knowledge` 페이지 비중이 크고, 테이블/목록/색인형 구조가 많다. 현재도 이를 `page_summary`, `key_points`, `knowledge_table_chunk` 등으로 처리하지만, 원본의 읽기 순서와 셀 단위 관계가 완전히 보존되지는 않는다.

### 3.2 chunk granularity 불균형

큰 overview chunk와 작은 field chunk가 공존한다. 현재는 route 정책과 heuristic rerank가 이를 보정하지만, hard query에서는 작은 정확 단서와 큰 설명 맥락이 따로 놀 수 있다.

### 3.3 다중 페이지 질의의 정렬 문제

현재 실패는 “관련 문서를 못 찾는 문제”보다 “올바른 페이지 묶음을 top-1으로 안정적으로 세우는 문제”에 가깝다.

### 3.4 다국어 질의와 영문 본문 간 간극

사용자 질의는 한국어가 많고 본문은 영어 중심이다. 지금은 query normalization과 route heuristic으로 잘 버티고 있지만, dense retrieval이 다국어 의미 정렬을 충분히 담당한다고 보기는 어렵다.

### 3.5 GraphRAG의 낮은 즉시 ROI

현재 주요 실패는 “코퍼스 전체의 theme 요약”보다 “특정 토픽의 multi-page 묶음 정렬” 문제다. 따라서 full GraphRAG는 비용 대비 즉효성이 낮다.

## 4. 외부 전문가 의견 종합

아래는 연구 논문과 산업 구현 가이드에서 반복적으로 나타나는 공통 의견을 이 프로젝트 맥락에 맞게 정리한 것이다.

### 4.1 하이브리드 검색은 유지하되, 정적인 결합은 재검토할 가치가 있다

- Elastic는 hybrid search에서 lexical + semantic 결합에 RRF를 권장한다.
- 그러나 Bruch et al.은 lexical/semantic fusion에서 RRF가 파라미터에 민감하며, 작은 학습 샘플만 있어도 convex combination이 더 나을 수 있다고 보고했다.

이 프로젝트는 이미 `gold_questions`, `adversarial_questions`, `multi_page_hard_questions`를 갖고 있으므로, “학습 가능한 간단한 결합 가중치”를 도입하기 좋은 상태다.

근거:

- Elastic hybrid search docs: https://www.elastic.co/docs/solutions/search/hybrid-search
- Bruch et al., *An Analysis of Fusion Functions for Hybrid Retrieval*: https://arxiv.org/abs/2210.11934

### 4.2 chunk 자체에 문맥을 더하는 방식은 실제로 효과가 크다

- Anthropic의 Contextual Retrieval은 chunk별 설명 맥락을 추가하고 BM25까지 함께 contextualize하면 retrieval failure를 크게 줄였다고 보고했다.
- EMNLP 2024의 RAG best-practice 연구도 metadata addition, small-to-big chunking, sliding window가 retrieval 품질을 높인다고 정리했다.

이 프로젝트는 이미 `title`, `section_l1`, `entry_type`, `field_name`, `page_role` 같은 구조 정보를 갖고 있다. 따라서 별도의 대형 인프라 없이도 “contextual chunk text”를 만드는 것이 가능하다.

근거:

- Anthropic Contextual Retrieval: https://www.anthropic.com/engineering/contextual-retrieval
- Wang et al., *Searching for Best Practices in Retrieval-Augmented Generation*: https://aclanthology.org/2024.emnlp-main.981/

### 4.3 강한 reranker는 hard route에서 특히 효과적이다

- Sentence Transformers 문서는 retrieve-then-rerank 파이프라인을 복잡한 검색/QA에서 권장한다.
- 같은 문서는 cross-encoder가 retriever보다 훨씬 더 정확한 relevance scoring을 제공하지만, 모든 문서쌍에 쓰기에는 느리므로 top-K 후보에만 적용해야 한다고 설명한다.

현재 프로젝트는 top-10 recall이 이미 높고, residual error가 top-1 ordering에 집중되어 있다. 이런 경우 cross-encoder 또는 stronger reranker는 매우 전형적인 해법이다.

근거:

- Sentence Transformers Retrieve & Re-Rank: https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html

### 4.4 late interaction / multi-vector retrieval은 다국어·장문·세밀한 정렬에 유리하다

- ColBERTv2는 token-level late interaction을 통해 단일 벡터 dense retrieval보다 더 세밀한 relevance modeling을 제공한다.
- BGE-M3는 multilingual, dense/sparse/multi-vector를 동시에 지원하고, 긴 문서와 cross-lingual retrieval에서 강점을 갖는다.

현재 프로젝트는 한국어 질의와 영문 문서가 섞이고, hard multi-page 질의에서 세밀한 토픽 구분이 필요하다. 이런 환경은 late interaction 또는 multi-vector 계열의 적합도가 높다.

근거:

- ColBERTv2: https://aclanthology.org/2022.naacl-main.272/
- M3-Embedding / BGE-M3: https://arxiv.org/abs/2402.03216

### 4.5 혼합형 PDF에서는 파싱 품질이 retrieval 상한을 결정한다

- Docling은 PDF에서 layout, reading order, table structure, OCR를 포함한 고급 추출을 제공한다.
- 최근 hybrid-document RAG 연구들은 text-only flattening이 heterogeneous text-table 문서에서 성능을 크게 떨어뜨리며, 구조 보존형 표현이 top-1 retrieval을 유의미하게 끌어올린다고 보고한다.

현재 corpus에서 `knowledge` 페이지가 크고 표형/목록형이 많다는 점을 고려하면, parser 업그레이드는 retrieval 업그레이드만큼 중요하다.

근거:

- Docling documentation: https://docling-project.github.io/docling/
- MixRAG / heterogeneous text-table retrieval: https://arxiv.org/abs/2504.09554

### 4.6 GraphRAG는 “전역 요약형 질문”에 강하지만, 현재 주병목과는 결이 다르다

- Microsoft GraphRAG 문서는 local search가 특정 entity 중심 질문에, global search가 dataset 전체의 theme/insight 질문에 적합하다고 설명한다.
- Microsoft Research는 baseline RAG가 corpus-wide summarization 질문에 약하다고 강조한다.

현재 SafetyCompanion의 주병목은 specific entity/anchor 기반 multi-page retrieval이다. 따라서 GraphRAG는 장기 옵션일 수는 있어도, 지금 당장 1순위는 아니다.

근거:

- GraphRAG Query Overview: https://microsoft.github.io/graphrag/query/overview/
- GraphRAG Global Search: https://microsoft.github.io/graphrag/query/global_search/
- Microsoft Research GraphRAG paper page: https://www.microsoft.com/en-us/research/publication/from-local-to-global-a-graph-rag-approach-to-query-focused-summarization/

### 4.7 계층적/요약형 인덱스는 multi-page 응답 품질을 보완할 수 있다

- RAPTOR는 문서를 요약 트리로 조직해 긴 문서 질의에서 여러 수준의 추상도를 활용하도록 제안한다.

이 프로젝트에서 full RAPTOR를 바로 도입할 필요는 없지만, “page-summary index + detail-page retrieval” 같은 RAPTOR-lite 구조는 multi-page route에 잘 맞는다.

근거:

- RAPTOR: https://arxiv.org/abs/2401.18059

## 5. 프로젝트 맞춤 고도화 권고안

아래는 우선순위를 반영한 권고안이다.

## 5.1 1순위: parser + chunking + contextual metadata 강화

가장 먼저 할 일:

1. `knowledge` 페이지와 table-like 페이지에 대해 layout-aware parser 실험 경로 추가
2. oversized `entry_overview_chunk`를 더 작은 retrieval unit으로 분해
3. chunk text 앞에 구조 metadata를 안정적으로 prepend
4. small-to-big 방식으로 작은 chunk를 찾고, 답변에는 부모 문맥을 함께 제공

추천 구현:

- 기존 `pdfplumber/pdftotext` 경로는 유지
- 조건부 fallback 또는 A/B parser로 Docling 추가
- `chunk_id` 단위에 아래 문맥 추가:
  - `title`
  - `section_l1`
  - `entry_type`
  - `field_name`
  - `pdf_page`
  - `printed_page`
  - `page_role` 또는 `entry_bundle_id`

왜 1순위인가:

- 현재 corpus가 table/list-heavy knowledge 문서를 많이 포함한다.
- hard failure가 retrieval candidate 부재가 아니라 structure-aware ordering 실패에 가깝다.
- 이 단계는 외부 서비스 없이도 적용 가능하다.

## 5.2 2순위: dense retrieval 현대화 + route별 reranker 도입

추천 방향:

1. dense backend를 TF-IDF+SVD에서 stronger embedding 기반으로 실험
2. 1차 후보는 hybrid retrieval로 넓게 가져가고
3. `multi_page_lookup`, `compare`, `recommendation`에만 stronger reranker 적용

추천 후보:

- dense retriever 후보: `BGE-M3` 우선 검토
- reranker 후보: Sentence Transformers CrossEncoder 계열 또는 BGE reranker 계열

왜 `BGE-M3`가 맞는가:

- 다국어 질의 대응
- 장문/다중 granularity 대응
- dense / sparse / multi-vector 확장 가능성

왜 전 route가 아니라 hard route 우선인가:

- 현재 일반 질의는 이미 충분히 강하다.
- 전체 경로에 무거운 reranker를 붙이면 latency와 운영 복잡성만 늘 수 있다.

## 5.3 3순위: multi-page 전용 계층적 검색 경로

추천 방향:

- `multi_page_lookup`에서만 2단계 retrieval 수행
  1. page-summary / entity anchor 레벨에서 seed page 찾기
  2. bundle / relation / neighboring pages를 재수집

구체 예시:

- `knowledge page summary index`
- `entity cluster index` for `THOR`, `HIII`, `ATD`, `dummy landscape`
- `page role aware reranking`
- `follow-up retrieval` for secondary pages

이 단계의 목표:

- `multi_page_hard__retrieval_top1_hit_rate`
- `multi_page_lookup` 계열 grounding failure

를 줄이는 것이다.

## 5.4 4순위: learned fusion

현재는 RRF가 안정적인 기본값이지만, 이 프로젝트는 labeled question set이 있으므로 아래 실험이 가능하다.

- BM25 score
- dense score
- route prior
- anchor hit
- page-role bonus
- disambiguation score

를 feature로 두고, 간단한 weighted fusion 또는 learning-to-rank를 도입할 수 있다.

권장 방식:

- 먼저 route별 scalar weighted fusion
- 그 다음 필요 시 route별 lightweight LTR

이 단계는 1순위와 2순위가 끝난 뒤에야 의미가 크다.

## 5.5 보류 권고: full GraphRAG / full multimodal VDocRAG

지금 당장은 아래 둘을 기본 경로에 넣는 것을 권장하지 않는다.

### Full GraphRAG

보류 이유:

- 현재 병목이 corpus-wide theme 질문이 아님
- graph 구축/요약 비용이 큼
- 기본 경로의 복잡도 증가

### Full visual-document RAG

보류 이유:

- charts/images 자체가 현재 핵심 failure source로 보이지 않음
- 구현 난이도와 비용이 큼
- parser/layout 보강만으로도 상당 부분 개선 가능성이 높음

## 6. 추천 로드맵

### Phase A. 2주 내 실용 개선

- Docling 또는 layout-aware fallback PoC
- chunk contextualization
- overview chunk 재분할
- `multi_page_lookup` 전용 evaluation slice 강화

성공 기준:

- `multi_page_hard__retrieval_top1_hit_rate` 개선
- `grounding_details.csv`의 multi-page failure 감소

### Phase B. 2~4주 개선

- BGE-M3 dense 실험
- hard route 대상 cross-encoder reranker 실험
- route별 top-K / rerank-K 최적화

성공 기준:

- hard multi-page top-1 개선
- latency 증가를 허용 가능한 범위로 유지

### Phase C. 선택 고도화

- learned fusion
- RAPTOR-lite hierarchical page summaries
- entity-cluster retrieval

### Phase D. 장기 옵션

- GraphRAG
- multimodal visual retrieval

## 7. 바로 하지 말아야 할 것

아래는 현재 기준으로 비추천이다.

- 아무 병목 분석 없이 GraphRAG부터 도입
- dense 모델만 교체하고 parser는 그대로 두기
- 모든 route에 무거운 reranker 일괄 적용
- 기존 평가셋 없이 fusion 공식을 감으로 조정

## 8. 최종 결론

현재 SafetyCompanion RAG는 “전체적으로 약한 시스템”이 아니라, 이미 상당히 강한 baseline 위에서 residual hard case가 남아 있는 상태다. 따라서 가장 적합한 고도화 방식은 다음 순서다.

1. 문서 구조 보존 강화
2. chunk 문맥 강화와 granularity 재설계
3. hard route 대상 dense/reranker 현대화
4. multi-page 전용 계층적 retrieval
5. 필요 시 learned fusion
6. GraphRAG는 장기 옵션

한 줄로 요약하면, 이 프로젝트의 다음 단계는 “더 큰 RAG”가 아니라 “더 구조를 잘 보존하고, hard route를 더 정교하게 정렬하는 RAG”다.

## 9. 조사 출처

- Wang et al., *Searching for Best Practices in Retrieval-Augmented Generation*:
  https://aclanthology.org/2024.emnlp-main.981/
- Anthropic, *Contextual Retrieval*:
  https://www.anthropic.com/engineering/contextual-retrieval
- Elastic, *Hybrid search*:
  https://www.elastic.co/docs/solutions/search/hybrid-search
- Bruch et al., *An Analysis of Fusion Functions for Hybrid Retrieval*:
  https://arxiv.org/abs/2210.11934
- Santhanam et al., *ColBERTv2*:
  https://aclanthology.org/2022.naacl-main.272/
- Chen et al., *M3-Embedding / BGE-M3*:
  https://arxiv.org/abs/2402.03216
- Sentence Transformers, *Retrieve & Re-Rank*:
  https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html
- Docling documentation:
  https://docling-project.github.io/docling/
- MixRAG / heterogeneous text-table retrieval:
  https://arxiv.org/abs/2504.09554
- RAPTOR:
  https://arxiv.org/abs/2401.18059
- Microsoft GraphRAG Query Overview:
  https://microsoft.github.io/graphrag/query/overview/
- Microsoft GraphRAG Global Search:
  https://microsoft.github.io/graphrag/query/global_search/
