# Hard Negative Spec

## 목적
top-10 내 정답을 top-1/top-3로 끌어올리기 위해 혼동이 잦은 유사 개념 쌍을 명시적으로 관리한다.

## 우선 혼동군
- `FMVSS 208` / `FMVSS 214` / `FMVSS 305a`
- `Euro NCAP` / `C-NCAP` / `U.S. NCAP`
- `active safety` / `passive safety`
- `dummy` / `ATD` / `THOR` / `HIII`
- 유사 seminar / event 제목군
- 한국어 paraphrase 표현군

## 활용 원칙
- query에서 특정 anchor가 검출되면 sibling anchor가 있는 후보는 penalty를 받을 수 있다.
- exact anchor hit는 strong boost를 받는다.
- hard-negative는 reranker와 disambiguation scorer 둘 다에서 활용한다.
