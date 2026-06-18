# Daily CS Interview

요청할 때마다 오늘 날짜의 CS/기술면접 지식 카드와 Spring 백엔드 지식 카드를 함께 생성하는 개인 학습 시스템입니다.

GitHub에 공개된 CS/면접 자료와 직접 모은 Markdown/Text 파일을 읽어 CS 주제 하나를 고르고, 별도의 Spring 백엔드 필수 커리큘럼에서 주제 하나를 골라 `daily_notes/`에 함께 정리합니다. 답변을 직접 쓰는 워크시트가 아니라, 매일 가볍게 읽고 면접 질문까지 함께 확인하는 방식입니다.

## Features

- 오늘 날짜 기준 CS/면접 지식 1개 생성
- Spring 백엔드 필수 지식 1개를 별도 트랙으로 생성
- OS, Network, DB, Java, Spring, JPA, Algorithm 등 카테고리 필터 지원
- 핵심 요약, 자세한 설명, 면접 포인트, 연관 면접 질문, 면접 답변 예시 자동 구성
- Spring REST API, 계층 분리, IoC/DI, MVC, 검증/예외, 트랜잭션, JPA, JWT 인증 등 필수 주제 누적
- 참고 자료 이미지 경로를 GitHub에서 보이는 추적 대상 경로로 보정
- 주간 리뷰 노트 생성
- 필요할 때 직접 생성하는 수동 실행 흐름 지원

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

## Topic Order

CS 주제는 랜덤이 아니라 정해진 순서로 선택됩니다.

1. `my_materials/`를 먼저 읽고, 그 다음 `references/external/`를 읽습니다.
2. 각 폴더 안의 Markdown/Text 파일은 파일 경로 이름순으로 정렬해서 훑습니다.
3. 파일 안에서는 Markdown 제목과 질문 라인을 학습 항목으로 뽑습니다.
4. `study_state/studied_items.json`에 이미 기록된 항목은 건너뜁니다.
5. 아직 학습하지 않은 항목 중 가장 먼저 발견된 항목이 오늘의 주제가 됩니다.

즉, 기본 순서는 `자료 위치 -> 파일명 정렬 -> 문서 안 제목 순서 -> 미학습 여부`로 결정됩니다.

Spring 백엔드 주제는 CS와 별도 순서로 진행됩니다.

1. `scripts/make_today_note.py` 안의 Spring 필수 커리큘럼 순서대로 진행합니다.
2. 진행한 Spring 주제는 `study_state/spring_studied_items.json`에 기록합니다.
3. 이미 만든 날짜를 `--force`로 다시 생성하면 그 날짜에 기록된 Spring 주제를 그대로 다시 렌더링합니다.

## Note Format

생성되는 노트는 아래 형식입니다.

```md
# 2026-06-16 1일 2CS/면접 지식

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

## 면접 답변 예시

- 자주 나오는 질문에 대한 답변 초안을 함께 생성합니다.

---

## 오늘의 Spring 백엔드 지식

REST API 설계 기본

## Spring 핵심 요약

- Spring 백엔드 필수 주제를 CS와 별도로 정리합니다.

## Spring 조금 더 자세히

- 개념, 구현 흐름, 실무 주의점을 차근차근 정리합니다.

## Spring 구현 체크리스트

- Controller, Service, Repository, DTO, 트랜잭션, 예외 처리 관점의 체크리스트를 정리합니다.

## Spring 코드 예시

- 코드가 있는 편이 이해에 도움이 되는 주제는 Java/Spring 예시 코드를 함께 생성합니다.

## Spring 면접 질문

- Spring 백엔드 직무 면접 질문을 함께 생성합니다.

## Spring 면접 답변 예시

- Spring 질문에 대한 답변 초안을 함께 생성합니다.

```

## Weekly Review

이번 주 생성된 CS 질문과 Spring 백엔드 주제를 모아 리뷰 노트를 만들 수 있습니다.

```bash
python3 scripts/make_weekly_review.py
```

결과는 `daily_notes/yonghun-cs-weekly-review-YYYY-MM-DD.md` 형식으로 저장됩니다.

## Manual Run

기본 사용 방식은 직접 실행입니다.

```bash
python3 scripts/make_today_note.py
```

이미 오늘 파일이 있는데 다시 만들려면:

```bash
python3 scripts/make_today_note.py --force
```

## Auto Run on macOS

자동 생성이 필요할 때만 macOS 로그인/시작 시 실행을 켤 수 있습니다.

```bash
./scripts/enable_daily_study.sh
```

자동 생성을 끄려면:

```bash
./scripts/disable_daily_study.sh
```

자동 실행은 `launchd`의 `RunAtLoad`를 사용합니다. 오늘 날짜의 노트가 이미 있으면 새로 만들지 않고 건너뜁니다. 직접 요청해서 생성하는 흐름으로 쓸 때는 켜지 않아도 됩니다.

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

`scripts/sync_references.py`는 참고 레포를 `reference_repos/`에 로컬 Git 캐시로 동기화한 뒤, `.git` 폴더를 제외한 파일 스냅샷을 `references/external/`에 복사합니다. 실제 노트 생성은 Git에 함께 올릴 수 있는 `references/external/`을 기준으로 동작합니다.

각 저장소의 원문 저작권과 라이선스를 존중해 개인 학습 용도로 사용하세요. 특히 `ksundong/backend-interview-question`은 비영리 조건이 포함된 CC BY-NC-SA 계열로 안내되어 있습니다.

Spring 백엔드 트랙은 필수 커리큘럼을 스크립트 안에 별도로 두고 진행합니다. 추가로 직접 모은 Spring 참고 자료는 `references/spring/`에 둘 수 있습니다. 구현 구조 참고 자료로는 Spring 공식 샘플인 `spring-projects/spring-petclinic`을 참고합니다.

## Project Structure

```text
.
├── daily_notes/          # 날짜별 지식 카드
├── my_materials/         # 직접 추가한 학습 자료
├── references/           # Git에 함께 올리는 참고 자료 스냅샷
│   ├── external/         # 외부 참고 레포 파일 스냅샷
│   └── spring/           # 직접 모은 Spring 참고 자료
├── reference_repos/      # 로컬 Git 동기화 캐시, Git에는 올리지 않음
├── scripts/              # 생성/동기화/자동실행 스크립트
├── study_state/          # CS/Spring 학습 로그, launchd 로그
├── reference_repos.json  # 참고 레포 목록
└── README.md
```

## Commands

```bash
# 참고 레포 동기화
python3 scripts/sync_references.py

# 오늘 카드 생성
python3 scripts/make_today_note.py

# 오늘 카드 다시 생성
python3 scripts/make_today_note.py --force

# 특정 카테고리 카드 생성
python3 scripts/make_today_note.py --category network

# 주간 리뷰 생성
python3 scripts/make_weekly_review.py

# macOS 자동 생성 켜기/끄기, 필요할 때만 사용
./scripts/enable_daily_study.sh
./scripts/disable_daily_study.sh
```
