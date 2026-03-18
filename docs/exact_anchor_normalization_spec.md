# Exact Anchor Normalization Spec

## 목표
사용자 입력의 code / acronym / title fragment를 canonical anchor로 복원한다.

## 예시
- `fmvss305a` -> `FMVSS 305a`
- `gtr14` -> `GTR 14`
- `adas experience` -> `ADAS Experience`
- `a e b` -> `AEB`

## 적용 위치
- query normalization
- exact anchor lookup
- disambiguation scorer
