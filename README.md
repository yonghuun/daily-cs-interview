# Daily CS Interview

CS/기술면접과 Spring 백엔드 지식을 매일 하나씩 기록하는 개인 학습 저장소입니다.

매일 노트는 `daily_notes/`에 날짜별 Markdown 문서로 남깁니다. 하루에 **CS 주제 1개**와 **Spring 백엔드 주제 1개**를 함께 정리합니다.

이 저장소의 목적은 단순 개념 정리가 아니라, **백엔드 개발자 면접 대비와 실무 이해를 위한 학습 노트**를 꾸준히 축적하는 것입니다.

---

## 핵심 원칙

| 원칙 | 기준 |
|------|------|
| 면접 복습 우선 | 문서를 열었을 때 핵심 요약, 면접 포인트, 예상 질문, 답변 예시가 먼저 보여야 합니다. |
| 구조화 우선 | 긴 줄글보다 목록, 표, 단계별 흐름, 비교표를 우선 사용합니다. |
| 실무 연결 | Java/Spring 백엔드에서 실제로 어떻게 쓰이는지 함께 설명합니다. |
| 꼬리 질문 대비 | 단순 정의에서 끝내지 않고 연관 개념까지 확장합니다. |
| 코드 예시 | Java/Spring 중심으로 핵심을 보여주는 짧은 예제를 사용합니다. |

---

## 기록 방식

- CS 주제: 알고리즘, 자료구조, 네트워크, 운영체제, 데이터베이스, Java 등
- Spring 주제: Spring Core, MVC, JPA, Security, Validation, Transaction, REST API 등
- 각 노트에는 핵심 요약, 면접 포인트, 예상 질문, 답변 예시, 실무 관점, 코드 예시, 상세 설명을 포함합니다.
- 이미 공부한 주제는 `study_state/`에 기록하여 중복 생성을 방지합니다.
- 가능하면 주제 간 연관 개념도 함께 설명합니다.

---

## 일일 노트 구성

노트는 복습하기 쉬운 순서로 작성합니다. 긴 설명은 아래로 내리고, 면접에서 바로 말할 수 있는 내용은 위쪽에 둡니다.

| 순서 | 섹션 | 목적 |
|------|------|------|
| 1 | 주제 | 오늘 학습할 개념을 명확히 표시 |
| 2 | 핵심 요약 | 3-5줄로 빠르게 복습 |
| 3 | 면접 포인트 | 정의, 원리, 장단점, 실무 활용 키워드 정리 |
| 4 | 예상 질문 | 자주 나오는 질문과 답변 방향 정리 |
| 5 | 답변 예시 | 실제 면접에서 말할 수 있는 문장으로 작성 |
| 6 | 실무 관점 | 프로젝트에서의 사용 방식과 주의점 정리 |
| 7 | 코드 예시 | 핵심 개념을 보여주는 최소 코드 |
| 8 | 상세 설명 | 내부 동작, 비교표, 꼬리 개념 심화 |

---

## 작성 품질 기준

<details>
<summary><strong>1. 면접에서 말할 수 있는 답변으로 작성</strong></summary>

면접 답변은 키워드 나열이 아니라 실제 말로 설명할 수 있는 형태로 작성합니다.

좋은 예:

```text
HashMap은 해시 함수를 이용해 버킷 위치를 계산하기 때문에 평균적으로 O(1)의 조회 성능을 제공합니다.
다만 해시 충돌이 많아지면 성능이 저하될 수 있어 충돌 해결 방식과 해시 함수의 품질이 중요합니다.
```

나쁜 예:

```text
HashMap
- O(1)
- 버킷
- 충돌
```

</details>

<details>
<summary><strong>2. 표와 목록을 적극 활용</strong></summary>

비교가 필요한 내용은 표로 정리합니다.

```md
| 구분 | HashMap | TreeMap |
|------|---------|---------|
| 정렬 | 보장하지 않음 | key 기준 정렬 |
| 조회 | 평균 O(1) | O(logN) |
| 적합한 경우 | 빠른 단건 조회 | 정렬/범위 검색 |
```

흐름이 중요한 내용은 단계로 정리합니다.

```md
1. 요청이 `DispatcherServlet`에 도착합니다.
2. `HandlerMapping`이 처리할 Controller를 찾습니다.
3. `HandlerAdapter`가 Controller 메서드를 호출합니다.
4. 결과가 응답으로 변환됩니다.
```

</details>

<details>
<summary><strong>3. 단순 정의에서 끝내지 않기</strong></summary>

각 주제는 개념 설명 이후 자연스럽게 이어지는 하위 개념까지 함께 정리합니다.

**해시**

- 해시 함수
- 버킷
- 충돌
- 체이닝
- 개방 주소법
- 재해싱
- Load Factor
- `HashMap` 내부 구조
- `equals()` / `hashCode()`

**인덱스**

- Clustered Index
- Non-Clustered Index
- Covering Index
- 인덱스를 타지 못하는 경우
- `EXPLAIN` 분석
- B-Tree / Hash Index

**트랜잭션**

- ACID
- Isolation Level
- Dirty Read
- Non-repeatable Read
- Phantom Read
- Spring `@Transactional`
- Proxy

</details>

<details>
<summary><strong>4. 실무 관점까지 연결</strong></summary>

단순 이론보다 실제 Java/Spring 백엔드 개발에서 어떻게 활용되는지 연결합니다.

- `HashMap`과 `ConcurrentHashMap`
- 인덱스와 SQL 성능
- JVM 메모리 구조와 GC
- DI를 사용하는 이유
- `@Transactional` 사용 시 주의점
- JPA N+1 문제
- Redis 캐싱 전략
- Spring Security 인증/인가 구조

실무 관점에는 다음 내용을 포함합니다.

- 실제 프로젝트에서 어떻게 사용하는가
- 어떤 문제가 자주 발생하는가
- 어떤 대안이 있는가
- 성능, 안정성, 유지보수에 어떤 영향을 주는가

</details>

<details>
<summary><strong>5. 코드 예시는 짧고 정확하게</strong></summary>

개념 이해에 도움이 되는 경우 Java/Spring 코드를 적극 활용합니다.

- Java 문법
- 자료구조
- 객체지향
- Spring MVC
- Spring Transaction
- JPA
- 동시성
- 디자인 패턴

주의사항:

- 코드가 설명보다 길어지지 않도록 합니다.
- 핵심 개념을 보여주는 최소한의 코드만 사용합니다.
- SQL 관련 내용은 SQL 예제를 사용합니다.
- Spring 관련 내용은 Java/Spring 코드 예제를 사용합니다.

</details>

---

## CS 주제 작성 규칙

CS 주제는 “정의 → 원리 → 장단점 → 실무 활용 → 꼬리 개념” 흐름으로 작성합니다.

| 섹션 | 포함할 내용 |
|------|-------------|
| 핵심 요약 | 정의, 왜 쓰는지, 핵심 장단점 |
| 면접 포인트 | 시간 복잡도, 동작 원리, 비교 개념 |
| 질문/답변 | 실제 면접에서 말할 수 있는 답변 |
| 실무 관점 | Java/Spring 백엔드에서의 활용 |
| 코드 예시 | Java 중심의 짧은 예제 |
| 상세 설명 | 내부 구조, 비교표, 연관 개념 |

<details>
<summary><strong>CS 주제별 확장 예시</strong></summary>

| 주제 | 함께 정리할 개념 |
|------|------------------|
| 해시 | 해시 함수, 버킷, 충돌, 체이닝, 개방 주소법, 재해싱, Load Factor, `HashMap` |
| 정렬 | 안정 정렬, 불안정 정렬, 시간 복잡도, 공간 복잡도, Java 정렬 API |
| 그래프 | BFS, DFS, 최단 경로, 위상 정렬, Union-Find |
| 운영체제 프로세스 | PCB, Context Switching, Thread, Scheduler, Race Condition |
| DB 인덱스 | B-Tree, Cardinality, Covering Index, 인덱스 미사용 케이스, `EXPLAIN` |
| 네트워크 HTTP | TCP, TLS, 상태 코드, Keep-Alive, REST API |

</details>

---

## Spring 주제 작성 규칙

Spring 주제는 단순 사용법보다 **왜 그렇게 동작하는지**, **실무에서 어디에 쓰는지**, **어떤 실수를 피해야 하는지**까지 정리합니다.

| 섹션 | 포함할 내용 |
|------|-------------|
| 핵심 요약 | 개념 정의와 사용하는 이유 |
| 동작 원리 | Spring 내부 흐름 |
| 내부 구성 요소 | 관련 객체와 역할 |
| 실무 구현 포인트 | 실제 프로젝트 적용 방식 |
| 주의사항 | 자주 하는 실수, 성능 이슈, 설계상 주의점 |
| 코드 예시 | Spring 코드 중심의 짧은 예제 |
| 꼬리 질문 | 면접에서 이어질 질문 |
| 함께 알아야 하는 개념 | 연관 개념 확장 |

<details>
<summary><strong>Spring 주제별 확장 예시</strong></summary>

**IoC / DI**

- Bean
- BeanFactory
- ApplicationContext
- 생성자 주입
- 필드 주입
- 순환 참조
- `@RequiredArgsConstructor`

**Spring MVC**

- `DispatcherServlet`
- `HandlerMapping`
- `HandlerAdapter`
- `ViewResolver`
- Argument Resolver
- Message Converter

**Transaction**

- ACID
- Isolation Level
- Dirty Read
- Non-repeatable Read
- Phantom Read
- Spring Proxy
- `@Transactional` self-invocation

**JPA**

- Persistence Context
- Dirty Checking
- Flush
- Lazy Loading
- N+1
- Fetch Join
- EntityGraph

**Security**

- SecurityFilterChain
- Authentication
- Authorization
- UserDetailsService
- JWT
- Session
- CSRF / CORS

</details>

<details>
<summary><strong>Spring 꼬리 질문 예시</strong></summary>

**IoC / DI**

- IoC와 DI의 차이는 무엇인가요?
- 생성자 주입을 권장하는 이유는 무엇인가요?
- 필드 주입의 단점은 무엇인가요?
- Bean은 언제 생성되나요?

**Transaction**

- ACID란 무엇인가요?
- Isolation Level은 무엇인가요?
- `@Transactional`은 어떻게 동작하나요?
- 프록시는 무엇인가요?
- self-invocation에서 트랜잭션이 적용되지 않는 이유는 무엇인가요?

**Security**

- JWT와 Session의 차이는 무엇인가요?
- Authentication과 Authorization의 차이는 무엇인가요?
- Spring Security 필터는 어떤 순서로 동작하나요?
- CORS와 CSRF는 무엇이 다른가요?

</details>

---

## 일일 노트 템플릿

<details open>
<summary><strong>전체 템플릿 보기</strong></summary>

````md
# YYYY-MM-DD 1일 2CS/면접 지식

---

# 오늘의 CS 지식

## 주제

주제명

## 카테고리

`algorithm`

## 핵심 요약

- 핵심 개념 1
- 핵심 개념 2
- 핵심 개념 3

## 면접 포인트

| 질문 포인트 | 핵심 키워드 |
|------------|------------|
| 정의 | |
| 동작 원리 | |
| 장점 | |
| 단점 | |
| 실무 활용 | |

## 자주 나오는 면접 질문

| 질문 | 핵심 답변 방향 |
|------|----------------|
| 질문 1 | |
| 질문 2 | |
| 질문 3 | |

## 면접 답변 예시

### Q. 질문

답변 예시

## 실무 관점

- 실제 프로젝트에서 어떻게 사용되는가
- 주의할 점은 무엇인가
- 관련 기술과의 차이는 무엇인가

## 코드 예시

```java
예제 코드
```

## 상세 설명

개념을 자세히 설명합니다.

필요한 경우 비교 표를 적극 활용합니다.

---

# 오늘의 Spring 백엔드 지식

## 주제

주제명

## Spring 핵심 요약

- 핵심 개념 1
- 핵심 개념 2
- 핵심 개념 3

## 동작 원리

Spring 내부 동작 흐름을 설명합니다.

## 내부 구성 요소

| 구성 요소 | 역할 |
|-----------|------|
| | |
| | |

## 실무 구현 포인트

| 상황 | 권장 방식 | 이유 |
|------|-----------|------|
| | | |
| | | |

## 주의사항

- 자주 하는 실수
- 성능 이슈
- 설계상 주의점

## 코드 예시

```java
예제 코드
```

## 자주 나오는 꼬리 질문

- 질문 1
- 질문 2
- 질문 3

## Spring 면접 답변 예시

### Q. 질문

답변 예시

## 함께 알아야 하는 개념

- 관련 개념 1
- 관련 개념 2
- 관련 개념 3

## 상세 설명

Spring 동작 원리와 내부 구조를 자세히 설명합니다.
````

</details>

---

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

참고 자료를 갱신할 때:

```bash
python3 scripts/sync_references.py
```

`reference_repos/`는 로컬 동기화 캐시이고 Git에는 올리지 않습니다. 실제 노트 생성은 `my_materials/`, `references/curated/`, `references/sources/`를 기준으로 동작합니다.

---

## 자료 구조

```text
daily_notes/        날짜별 학습 노트
references/         학습 자료
  curated/          직접 정리한 자료
  sources/          공개 자료 스냅샷
  SOURCES.md        출처 및 라이선스

scripts/            노트 생성 및 동기화 스크립트
study_state/        학습 이력 및 생성 로그
```

---

## 생성 시 최종 규칙

노트 생성 시 다음 기준을 반드시 따릅니다.

- CS 주제 1개와 Spring 주제 1개를 작성합니다.
- 이미 학습한 주제는 가능한 한 제외합니다.
- 핵심 요약 → 면접 포인트 → 질문 → 답변 → 실무 → 코드 → 상세 설명 순서를 유지합니다.
- Spring 주제는 동작 원리, 내부 구성 요소, 주의사항, 꼬리 질문을 포함합니다.
- 긴 줄글보다 표와 구조화된 정리를 우선합니다.
- Java/Spring 백엔드 개발자 면접 관점에서 설명합니다.
- 코드 예시는 Java/Spring을 우선 사용합니다.
- 실무에서의 사용 사례와 주의점을 함께 설명합니다.
- 단순 암기형 설명보다 이해 중심으로 작성합니다.
- 문서를 읽고 바로 면접 답변이 가능하도록 작성합니다.
