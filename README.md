# Daily CS Interview

CS/기술면접과 Spring 백엔드 지식을 매일 하나씩 기록하는 개인 학습 저장소입니다.

매일 노트는 `daily_notes/`에 날짜별 Markdown으로 남깁니다. 한 번 생성할 때 CS 주제 1개와 Spring 백엔드 주제 1개를 함께 정리합니다.

## 기록 방식

- CS 주제: 알고리즘, 네트워크, 운영체제, 데이터베이스, Java, JPA, Spring 등
- Spring 주제: REST API, 계층 분리, IoC/DI, MVC, 검증/예외, 트랜잭션, JPA, Security 등
- 각 노트에는 핵심 요약, 자세한 설명, 면접 포인트, 예상 질문, 답변 예시를 담습니다.
- 이미 공부한 주제는 `study_state/`에 기록해서 다음 생성 때 건너뜁니다.

## 사용

```bash
# 오늘 노트 생성
python3 scripts/make_today_note.py

# 오늘 노트 다시 생성
python3 scripts/make_today_note.py --force

# 특정 카테고리만 생성
python3 scripts/make_today_note.py --category network

# 주간 리뷰 생성
python3 scripts/make_weekly_review.py
```

생성 결과:

```text
daily_notes/yonghun-cs-interview-YYYY-MM-DD.md
```

## 자료 구조

```text
daily_notes/        날짜별 학습 노트
references/         학습에 참고하는 자료
  curated/          직접 정리한 자료
  sources/          공개 자료 스냅샷
  SOURCES.md        원본 출처와 라이선스
scripts/            노트 생성/자료 동기화 스크립트
study_state/        공부한 주제와 생성 로그
```

참고 자료를 갱신할 때:

```bash
python3 scripts/sync_references.py
```

`reference_repos/`는 로컬 동기화 캐시이고 Git에는 올리지 않습니다. 실제 노트 생성은 `my_materials/`, `references/curated/`, `references/sources/`를 기준으로 동작합니다.

