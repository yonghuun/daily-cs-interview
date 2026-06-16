# Daily CS Interview

매일 하나씩 CS/기술면접 지식 카드를 생성하는 개인 학습 시스템입니다.

GitHub에 공개된 CS/면접 자료와 직접 모은 Markdown/Text 파일을 읽어, 하루에 하나의 주제를 골라 `daily_notes/`에 학습 카드로 정리합니다. 답변을 직접 쓰는 워크시트가 아니라, 매일 가볍게 읽고 면접 질문까지 함께 확인하는 방식입니다.

## Features

- 하루에 하나의 CS/면접 지식 카드 생성
- OS, Network, DB, Java, Spring, JPA, Algorithm 등 카테고리 필터 지원
- 핵심 요약, 자세한 설명, 면접 포인트, 연관 면접 질문 자동 구성
- Markdown 이미지 경로 자동 보정
- D+1, D+3, D+7 복습 항목 자동 표시
- 주간 리뷰 노트 생성
- macOS 로그인/시작 시 자동 생성 지원

## Quick Start

참고 레포를 내려받습니다.

```bash
python3 scripts/sync_references.py
```

오늘의 지식 카드를 생성합니다.

```bash
python3 scripts/make_today_note.py
```

생성 결과는 아래 경로에 저장됩니다.

```text
daily_notes/yonghun-cs-interview-YYYY-MM-DD.md
```

## Category

특정 카테고리만 골라 생성할 수 있습니다.

```bash
python3 scripts/make_today_note.py --category network
python3 scripts/make_today_note.py --category db
python3 scripts/make_today_note.py --category os
```

지원 카테고리를 확인하려면:

```bash
python3 scripts/make_today_note.py --list-categories
```

현재 지원 카테고리:

```text
algorithm
db
design
java
jpa
network
os
spring
web
```

## Note Format

생성되는 노트는 아래 형식입니다.

```md
# 2026-06-16 1일 1CS/면접 지식

## 오늘의 CS 지식

비대칭키 방식(공개키 방식)

## 카테고리

network

## 핵심 요약

- 핵심 내용을 짧게 정리합니다.

## 조금 더 자세히

원문 기반 설명, 표, 이미지 등을 정리해서 보여줍니다.

## 면접 포인트

- 면접에서 어떤 관점으로 설명해야 하는지 정리합니다.

## 연관되어 자주 나오는 면접 질문

- 이 개념을 한 문장으로 설명해주세요.
- 장점과 단점은 무엇인가요?
- 비슷한 개념과 비교해주세요.

## 오늘의 복습

- D+1, D+3, D+7 복습 항목이 자동으로 들어갑니다.
```

## Weekly Review

이번 주 생성된 학습 카드를 모아 리뷰 노트를 만들 수 있습니다.

```bash
python3 scripts/make_weekly_review.py
```

결과는 `daily_notes/yonghun-cs-weekly-review-YYYY-MM-DD.md` 형식으로 저장됩니다.

## Auto Run on macOS

macOS 로그인/시작 시 오늘의 지식 카드를 자동 생성하려면:

```bash
./scripts/enable_daily_study.sh
```

자동 생성을 끄려면:

```bash
./scripts/disable_daily_study.sh
```

자동 실행은 `launchd`의 `RunAtLoad`를 사용합니다. 오늘 날짜의 노트가 이미 있으면 새로 만들지 않고 건너뜁니다.

## Add My Materials

직접 모은 자료는 `my_materials/`에 넣으면 됩니다.

```text
my_materials/my_backend_questions.md
```

권장 형식:

```md
## 트랜잭션 ACID란?

ACID는 원자성, 일관성, 격리성, 지속성을 의미합니다.

## 인덱스를 많이 만들면 왜 안 좋나요?

쓰기 성능 저하와 저장 공간 증가가 발생할 수 있습니다.
```

## Reference Repositories

`reference_repos.json`에 아래 레포들이 등록되어 있습니다.

- `gyoogle/tech-interview-for-developer`
- `devSquad-study/2023-CS-Study`
- `ksundong/backend-interview-question`

각 저장소의 원문 저작권과 라이선스를 존중해 개인 학습 용도로 사용하세요. 특히 `ksundong/backend-interview-question`은 비영리 조건이 포함된 CC BY-NC-SA 계열로 안내되어 있습니다.

## Project Structure

```text
.
├── daily_notes/          # 날짜별 지식 카드
├── my_materials/         # 직접 추가한 학습 자료
├── reference_repos/      # 동기화된 참고 GitHub 레포
├── scripts/              # 생성/동기화/자동실행 스크립트
├── study_state/          # 출제 기록, 복습 로그, launchd 로그
├── reference_repos.json  # 참고 레포 목록
└── README.md
```

## Commands

```bash
# 참고 레포 동기화
python3 scripts/sync_references.py

# 오늘 카드 생성
python3 scripts/make_today_note.py

# 특정 카테고리 카드 생성
python3 scripts/make_today_note.py --category network

# 주간 리뷰 생성
python3 scripts/make_weekly_review.py

# macOS 자동 생성 켜기/끄기
./scripts/enable_daily_study.sh
./scripts/disable_daily_study.sh
```
