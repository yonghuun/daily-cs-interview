# 2026-07-01 1일 2CS/면접 지식

---

# 오늘의 CS 지식

## 주제

Red-Black Tree: 어떻게 `O(log n)`을 보장하는가

## 카테고리

`algorithm` · `data-structure`

## 오늘의 핵심 질문

> Red-Black Tree는 완전 균형 트리가 아닌데도 어떻게 최악의 탐색 시간을 `O(log n)`으로 보장할까?

## 핵심 요약

- Red-Black Tree는 각 노드에 색을 추가하고 몇 가지 불변식을 유지하는 **자가 균형 이진 탐색 트리**입니다.
- 루트에서 모든 `NIL`까지의 검은 노드 수를 같게 하고 빨간 노드가 연속되지 못하게 하므로, 가장 긴 경로는 가장 짧은 경로의 2배를 넘지 않습니다.
- 따라서 높이는 `h <= 2log₂(n + 1)`이고 탐색·삽입·삭제의 최악 시간 복잡도는 `O(log n)`입니다.
- 삽입과 삭제는 먼저 BST 방식으로 수행한 뒤, 깨진 불변식을 **재색칠(recoloring)**과 **회전(rotation)**으로 복구합니다.
- Java의 `TreeMap`·`TreeSet`이 대표적인 Red-Black Tree 활용 사례입니다. 정렬, 범위 검색, 최솟값·최댓값 탐색이 필요할 때 유용합니다.

## 먼저 바로잡을 표현

Red-Black Tree를 흔히 “균형 트리”라고 하지만, 모든 리프의 깊이가 같은 **완전한 높이 균형**을 유지하는 것은 아닙니다. 대신 높이가 로그 범위를 벗어나지 않는 정도의 느슨한 균형을 유지합니다. 이 느슨함 덕분에 AVL Tree보다 탐색 경로는 조금 길 수 있지만, 삽입·삭제 시 균형 조정 부담은 대체로 작습니다.

## Red-Black Tree의 5가지 불변식

| 번호 | 불변식 | 이 규칙이 하는 일 |
| --- | --- | --- |
| 1 | 모든 노드는 Red 또는 Black입니다. | 균형 상태를 표현할 1비트 정보를 둡니다. |
| 2 | 루트는 Black입니다. | 정의와 증명을 단순화합니다. 루트 재색칠은 경로 간 Black 수 차이를 만들지 않습니다. |
| 3 | 모든 `NIL` 리프는 Black입니다. | 자식이 없는 경우도 동일한 기준으로 Black Height를 계산합니다. |
| 4 | Red 노드의 자식은 모두 Black입니다. | Red가 연속되는 것을 막아 한 경로만 과도하게 길어지지 못하게 합니다. |
| 5 | 한 노드에서 자손 `NIL`로 가는 모든 경로의 Black 노드 수가 같습니다. | 어느 한쪽에만 노드가 계속 쌓이는 것을 제한합니다. |

여기서 `NIL`은 실제 데이터를 가진 노드가 아니라 “자식 없음”을 표현하는 가상의 Black 노드입니다. 구현에서는 하나의 sentinel 객체를 공유하거나 `null`을 Black으로 간주할 수 있습니다.

### Black Height

노드 `x`의 Black Height `bh(x)`는 일반적으로 `x`를 제외하고, `x`에서 임의의 자손 `NIL`까지 내려가는 경로에 포함된 Black 노드 수입니다. 5번 불변식 때문에 어떤 경로를 선택해도 값이 같습니다.

## 핵심: 높이가 왜 `O(log n)`인가

노드 수가 `n`이고 루트에서 `NIL`까지의 가장 긴 경로 길이를 `h`라고 하겠습니다.

1. Red 노드는 연속할 수 없습니다.
2. 따라서 가장 긴 경로에서도 Red 노드 수는 Black 노드 수보다 많을 수 없습니다.
3. 그러므로 Black Height를 `bh`라고 하면 `h <= 2bh`입니다.
4. Black Height가 `bh`인 서브트리는 내부 노드를 최소 `2^bh - 1`개 가집니다.
5. 따라서 `n >= 2^bh - 1`, 즉 `bh <= log₂(n + 1)`입니다.
6. 두 부등식을 합치면 다음과 같습니다.

```text
h <= 2bh <= 2log₂(n + 1)
```

즉, 트리의 높이가 `O(log n)`을 벗어나지 않습니다. 탐색은 루트에서 리프 방향으로 높이만큼 이동하므로 최악에도 `O(log n)`입니다. “자가 균형이라서 빠르다”보다 이 논리를 설명해야 면접 답변이 단단해집니다.

## 회전은 무엇을 보존하는가

회전은 부모·자식 관계를 국소적으로 바꾸지만 **BST의 중위 순서**는 보존합니다.

### 왼쪽 회전

```text
    x                       y
   / \                     / \
  A   y      left(x)      x   C
     / \       ───▶      / \
    B   C               A   B
```

회전 전후 모두 중위 순회 결과는 `A < x < B < y < C`입니다. 포인터 몇 개만 바꾸므로 회전 자체는 `O(1)`입니다. 다만 전체 삽입·삭제는 위치 탐색과 위반 전파 때문에 `O(log n)`입니다.

## 삽입: 왜 새 노드는 Red인가

새 노드를 Black으로 삽입하면 새 노드를 포함한 경로의 Black Height가 즉시 1 증가해 5번 불변식이 깨집니다. Red로 삽입하면 Black Height는 그대로이고, 위반 가능성은 주로 “부모도 Red인 경우”로 한정됩니다. 국소적인 Red-Red 충돌이 전체 경로의 Black Height 불일치보다 복구하기 쉽습니다.

### 삽입의 큰 흐름

1. 일반 BST 규칙으로 삽입 위치를 찾습니다.
2. 새 노드를 Red로 삽입합니다.
3. 부모가 Black이면 종료합니다.
4. 부모가 Red라면 삼촌의 색과 노드 배치를 보고 재색칠 또는 회전합니다.
5. 위반이 위로 전파될 수 있으므로 루트까지 반복하고, 마지막에 루트를 Black으로 만듭니다.

### 삽입 복구 케이스

`z`는 삽입 노드, `P`는 부모, `G`는 조부모, `U`는 삼촌이라고 하겠습니다. `P`가 Red일 때 `G`는 반드시 Black이어야 합니다. 삽입 전에는 Red가 연속될 수 없었기 때문입니다.

| 상황 | 처리 | 이유 |
| --- | --- | --- |
| `P`가 Black | 아무 작업도 하지 않습니다. | 모든 불변식을 만족합니다. |
| `P`와 `U`가 모두 Red | `P`, `U`를 Black으로, `G`를 Red로 바꾸고 `G`부터 다시 검사합니다. | 현재 서브트리의 Black Height를 유지하면서 Red-Red 충돌을 위로 올립니다. |
| `P`는 Red, `U`는 Black, 안쪽 꺾임(LR/RL) | `P`를 기준으로 한 번 회전해 바깥쪽 직선(LL/RR)으로 바꿉니다. | 다음 회전을 적용할 수 있는 형태로 정규화합니다. |
| `P`는 Red, `U`는 Black, 바깥쪽 직선(LL/RR) | `G`를 기준으로 회전하고 `P`와 `G`를 재색칠합니다. | BST 순서와 Black Height를 보존하며 Red-Red 충돌을 제거합니다. |

### 삽입 예시: `10 → 20 → 30`

`30`을 Red로 삽입하면 `20-30`이 Red-Red가 됩니다. 삼촌은 Black `NIL`이고 오른쪽-오른쪽(RR) 직선 형태이므로, `10`을 기준으로 왼쪽 회전한 뒤 `20`을 Black, `10`을 Red로 바꿉니다.

```text
10(B)                  20(B)
   \                   /   \
   20(R)      ───▶   10(R) 30(R)
      \
      30(R)
```

## 삭제가 삽입보다 어려운 이유

Red 노드를 제거하면 어떤 경로의 Black 노드 수도 바뀌지 않습니다. 반면 Black 노드를 제거하면 해당 경로의 Black Height가 1 줄어듭니다. 이를 설명하기 위해 삭제 과정에서는 부족한 Black 하나를 가진 상태를 흔히 **Double Black**이라고 부릅니다. Double Black은 실제 색이 아니라 복구 알고리즘을 이해하기 위한 개념입니다.

### 삭제의 큰 흐름

1. 자식이 둘이면 BST 삭제와 마찬가지로 후계자 또는 전임자와 위치를 조정해, 실제 제거 대상을 자식이 최대 하나인 노드로 만듭니다.
2. 제거되는 노드의 원래 색이 Red라면 종료합니다.
3. Black을 제거했지만 대체 자식이 Red라면 그 자식을 Black으로 바꾸고 종료합니다.
4. Black을 제거했고 대체 자식도 Black이면 Double Black을 형제의 색과 자식 색에 따라 위로 이동시키거나, 회전과 재색칠로 해소합니다.

### 삭제 복구를 보는 기준

| 형제 `S`의 상태 | 핵심 처리 방향 |
| --- | --- |
| `S`가 Red | 부모를 기준으로 회전하고 부모와 형제를 재색칠해, 형제가 Black인 문제로 변환합니다. |
| `S`가 Black이고 두 자식도 Black | 형제를 Red로 바꾸고 부족한 Black을 부모 쪽으로 올립니다. |
| `S`가 Black이고 가까운 자식만 Red | 형제를 먼저 회전해 먼 자식이 Red인 형태로 바꿉니다. |
| `S`가 Black이고 먼 자식이 Red | 부모를 기준으로 회전·재색칠해 Double Black을 제거합니다. |

면접에서 삭제의 모든 대칭 케이스를 암기해 늘어놓기보다, **Black 노드 삭제가 Black Height를 깨뜨리고, 형제 서브트리의 Black을 회전·재색칠로 재분배한다**는 원리를 먼저 말하는 편이 좋습니다.

## 시간·공간 복잡도

| 연산 | 최악 시간 | 설명 |
| --- | --- | --- |
| 검색 | `O(log n)` | 높이가 `O(log n)`입니다. |
| 삽입 | `O(log n)` | 위치 탐색 `O(log n)` + 복구 `O(log n)`입니다. 회전 횟수는 상수로 제한됩니다. |
| 삭제 | `O(log n)` | 위치 탐색과 Double Black 복구가 루트 방향으로 진행될 수 있습니다. |
| 최솟값·최댓값 | `O(log n)` | 가장 왼쪽·오른쪽 노드까지 이동합니다. |
| 전체 순회 | `O(n)` | 모든 노드를 한 번 방문합니다. |
| 공간 | `O(n)` | 노드, 자식·부모 참조와 색 정보가 필요합니다. |

## AVL Tree, Hash Table, B+Tree와 비교

| 구조 | 강점 | 약점 | 적합한 상황 |
| --- | --- | --- | --- |
| Red-Black Tree | 느슨한 균형으로 조회·삽입·삭제 모두 최악 `O(log n)` | 해시보다 동등 키 평균 조회가 느릴 수 있음 | 정렬된 Map/Set, 범위 검색, 잦은 변경 |
| AVL Tree | 더 엄격한 높이 균형으로 조회 경로가 짧음 | 삽입·삭제 시 균형 조정이 더 잦을 수 있음 | 조회 비중이 매우 높은 인메모리 구조 |
| Hash Table | 동등 키 조회가 평균 `O(1)` | 정렬·범위 검색이 약하고 충돌 시 성능 저하 | 순서가 필요 없는 빠른 키 조회 |
| B/B+Tree | 높은 fan-out으로 디스크 I/O 횟수를 줄임 | 인메모리 구현은 복잡하고 노드가 큼 | DB·파일 시스템 인덱스 |

Red-Black Tree와 B+Tree가 모두 균형 검색 트리라고 해서 용도가 같은 것은 아닙니다. DB 인덱스는 비교 한 번의 CPU 비용보다 디스크 페이지 접근 횟수가 훨씬 중요하므로, 한 노드에 많은 키를 담아 높이를 낮추는 B+Tree 계열이 유리합니다.

## Java 실무 연결

### `TreeMap`과 `TreeSet`

`TreeMap`은 키를 Red-Black Tree로 관리하며 `get`, `put`, `remove`, `containsKey`를 `O(log n)`에 제공합니다. `TreeSet`은 내부적으로 `TreeMap`을 이용합니다.

```java
NavigableMap<Integer, String> schedules = new TreeMap<>();
schedules.put(900, "daily meeting");
schedules.put(1330, "code review");
schedules.put(1100, "interview study");

Map.Entry<Integer, String> next = schedules.ceilingEntry(1000);
SortedMap<Integer, String> afternoon = schedules.tailMap(1200);
```

정렬뿐 아니라 `floorEntry`, `ceilingEntry`, `subMap`처럼 **근접 키와 범위 조회**가 필요할 때 `HashMap`보다 적합합니다.

### 실무 주의점

- 정렬 기준인 `Comparator`가 동등하다고 판단하는 두 키는 Map 관점에서도 같은 키로 취급될 수 있습니다. 일반적으로 비교 결과와 `equals`의 의미를 일치시키는 것이 안전합니다.
- 키로 사용한 객체의 정렬 기준 필드를 삽입 후 변경하면 트리 순서가 깨진 것처럼 조회가 실패할 수 있으므로 키는 불변 객체로 두는 편이 좋습니다.
- `TreeMap`은 스레드 안전하지 않습니다. 정렬된 동시성 Map이 필요하면 `ConcurrentSkipListMap` 등을 검토합니다.
- Java `HashMap`도 충돌이 심한 버킷을 특정 조건에서 Red-Black Tree로 바꿉니다. 이는 충돌 공격과 최악의 선형 탐색을 완화하기 위한 구현 전략이며, `HashMap` 전체가 정렬된다는 뜻은 아닙니다.
- 현재 JDK 구현에서 한 버킷의 엔트리가 일정 임계값에 도달하고 테이블 용량도 충분할 때 트리화하지만, 구체적인 임계값은 API 계약이 아닌 구현 세부사항입니다.

## 자주 나오는 면접 질문

### Q1. Red-Black Tree를 한 문장으로 설명해주세요.

Red-Black Tree는 노드 색과 Black Height 불변식을 이용해 가장 긴 루트-리프 경로를 가장 짧은 경로의 2배 이내로 제한함으로써, 검색·삽입·삭제의 최악 시간 복잡도를 `O(log n)`으로 보장하는 자가 균형 BST입니다.

### Q2. 왜 새 노드를 Red로 삽입하나요?

Black으로 삽입하면 그 노드가 포함된 모든 경로의 Black Height가 1 증가해 전역적인 불균형이 생깁니다. Red로 넣으면 Black Height는 유지되고 부모가 Red일 때의 국소적인 Red-Red 위반만 복구하면 되기 때문입니다.

### Q3. 회전하면 BST 정렬 규칙이 깨지지 않나요?

깨지지 않습니다. 회전은 부분 트리의 부모·자식 관계만 바꾸고 중위 순서, 즉 `왼쪽 < 루트 < 오른쪽`의 키 순서는 그대로 보존합니다.

### Q4. Red-Black Tree는 항상 완전 균형인가요?

아닙니다. 좌우 서브트리 높이가 항상 같지는 않습니다. 다만 Red 연속 금지와 동일한 Black Height 규칙으로 최장 경로가 최단 경로의 2배를 넘지 않게 제한해 점근적인 균형을 보장합니다.

### Q5. Red-Black Tree와 AVL Tree의 차이는 무엇인가요?

AVL Tree는 각 노드의 좌우 높이 차를 엄격히 제한해 검색에 유리하고, Red-Black Tree는 균형 조건이 더 느슨해 삽입·삭제의 구조 변경 부담이 상대적으로 작습니다. 그래서 읽기와 쓰기가 섞인 범용 정렬 Map/Set에는 Red-Black Tree가 자주 쓰입니다.

### Q6. `TreeMap`과 `HashMap` 중 무엇을 선택하나요?

동등 키 기반 조회만 필요하면 평균 `O(1)`인 `HashMap`을 우선 고려합니다. 키 정렬, 범위 검색, 바로 이전·다음 키 탐색이 필요하거나 최악 `O(log n)` 보장이 중요하면 `TreeMap`이 적합합니다.

## 30초 면접 답변

> Red-Black Tree는 자가 균형 BST입니다. 모든 루트-리프 경로의 Black 노드 수를 같게 하고 Red 노드의 연속을 금지합니다. 그래서 가장 긴 경로가 가장 짧은 경로의 2배를 넘지 않고, 높이가 최대 `2log₂(n+1)`로 제한됩니다. 삽입·삭제 후 규칙이 깨지면 재색칠과 회전으로 복구하므로 탐색·삽입·삭제 모두 최악 `O(log n)`입니다. Java에서는 `TreeMap`과 `TreeSet`이 대표적인 활용 사례입니다.

## 스스로 점검하기

1. Red 노드가 연속될 수 있다면 높이 증명이 왜 깨질까?
2. 새 노드를 Black이 아니라 Red로 삽입하는 이유를 Black Height로 설명할 수 있는가?
3. `TreeMap`이 `HashMap`보다 나은 구체적인 API 요구사항을 세 가지 말할 수 있는가?
4. DB 인덱스가 Red-Black Tree보다 B+Tree를 주로 사용하는 이유를 메모리와 디스크 접근 단위로 설명할 수 있는가?

---

# 오늘의 Spring 백엔드 지식

## 주제

Spring 트랜잭션 심화: 전파, 롤백 경계, `UnexpectedRollbackException`

## 오늘의 핵심 질문

> 내부 `@Transactional` 메서드의 예외를 `try-catch`로 처리했는데, 왜 바깥 메서드가 끝날 때 전체 트랜잭션이 롤백될까?

## Spring 핵심 요약

- `@Transactional`은 AOP 프록시의 `TransactionInterceptor`가 메서드 호출 전후에 트랜잭션 시작·참여·커밋·롤백을 결정하는 선언적 트랜잭션 기능입니다.
- 기본 전파인 `REQUIRED`는 이미 트랜잭션이 있으면 같은 **물리 트랜잭션**에 참여합니다. 각 메서드의 논리적 범위가 달라도 실제 DB 커넥션과 커밋 단위는 하나입니다.
- 내부 참여 범위가 `rollback-only`를 표시하면 바깥 코드가 예외를 잡아도 물리 트랜잭션은 커밋할 수 없습니다. 바깥 커밋 시점에 이를 알리기 위해 `UnexpectedRollbackException`이 발생할 수 있습니다.
- `REQUIRES_NEW`는 독립적인 물리 트랜잭션을 만들지만 커넥션을 추가 점유하고 바깥 트랜잭션과 원자성을 공유하지 않습니다.
- DB 트랜잭션은 외부 API, 메시지 브로커, 파일 시스템을 자동으로 롤백하지 못합니다. 이런 경계에서는 Outbox, 멱등성, 재시도, 보상 트랜잭션을 함께 설계해야 합니다.

## 프록시에서 DB까지의 동작 흐름

```text
클라이언트
   │
   ▼
Spring AOP Proxy
   │  TransactionInterceptor
   │  1. 트랜잭션 속성 조회
   │  2. 시작 또는 기존 트랜잭션 참여
   ▼
Target Service Method
   │
   ▼
Repository / EntityManager / JDBC Connection
   │
   ▼
정상 반환: commit 시도
예외 반환: rollback 규칙 평가
```

Spring은 `PlatformTransactionManager` 추상화를 통해 실제 자원을 제어합니다. JDBC라면 보통 현재 스레드에 커넥션을, JPA라면 `EntityManager`와 트랜잭션 자원을 연결합니다. 따라서 같은 스레드의 하위 Repository 호출이 같은 트랜잭션 자원에 참여할 수 있습니다.

### 중요한 결과

- 프록시를 거치지 않는 self-invocation은 새 `@Transactional` 경계를 만들지 못할 수 있습니다.
- 새 스레드에서 실행되는 `@Async` 작업에 호출 스레드의 트랜잭션이 자동 전파되지 않습니다.
- 트랜잭션은 보통 Service의 **외부에서 호출 가능한 유스케이스 메서드**에 경계를 두는 것이 이해하기 쉽습니다.

## 논리 트랜잭션과 물리 트랜잭션

다음 호출을 생각해 봅시다.

```text
OrderService.createOrder()       @Transactional(REQUIRED)
 └─ StockService.decrease()      @Transactional(REQUIRED)
```

두 메서드는 각각 `@Transactional` 경계를 선언했으므로 논리적인 트랜잭션 범위는 두 개입니다. 하지만 `decrease()`는 기존 트랜잭션에 참여하므로 DB 커넥션 관점의 물리 트랜잭션은 하나입니다.

```text
논리 범위: [ createOrder -------------------------------- ]
                    [ decrease -------- ]
물리 범위: [ connection / DB transaction ---------------- ]
```

커밋은 가장 바깥 물리 트랜잭션이 끝날 때 한 번 수행됩니다. 안쪽 메서드가 정상 종료됐다고 독립적으로 커밋되는 것이 아닙니다.

## `UnexpectedRollbackException` 발생 과정

### 문제 코드

```java
@Service
@RequiredArgsConstructor
public class OrderService {

    private final StockService stockService;
    private final OrderRepository orderRepository;

    @Transactional
    public Long createOrder(CreateOrderCommand command) {
        try {
            stockService.decrease(command.productId(), command.quantity());
        } catch (OutOfStockException e) {
            // 예외를 처리했으니 바깥 트랜잭션은 커밋될 것이라고 착각하기 쉽다.
            log.warn("재고 차감 실패", e);
        }

        return orderRepository.save(Order.pending(command)).getId();
    }
}

@Service
@RequiredArgsConstructor
public class StockService {

    private final StockRepository stockRepository;

    @Transactional // propagation = REQUIRED가 기본값
    public void decrease(Long productId, int quantity) {
        Stock stock = stockRepository.findByProductId(productId)
                .orElseThrow();
        stock.decrease(quantity); // OutOfStockException 발생 가능
    }
}
```

### 실제 순서

1. `createOrder()` 프록시가 물리 트랜잭션을 시작합니다.
2. 다른 Bean인 `stockService`의 프록시가 기존 트랜잭션에 참여합니다.
3. `decrease()`에서 런타임 예외가 발생합니다.
4. `StockService`의 트랜잭션 인터셉터가 예외를 보고 **공유 물리 트랜잭션을 rollback-only로 표시**합니다.
5. 바깥 `createOrder()`가 예외를 잡아 실행을 계속합니다.
6. 바깥 인터셉터가 커밋하려 하지만 이미 rollback-only이므로 실제로 롤백합니다.
7. 호출자에게 “정상 커밋된 것으로 오해하지 말라”는 의미로 `UnexpectedRollbackException`을 던집니다.

핵심은 `catch`가 Java의 제어 흐름을 바꿀 뿐, 이미 기록된 트랜잭션의 rollback-only 상태를 되돌리지 않는다는 점입니다.

## 의도에 따른 해결 방향

| 비즈니스 의도 | 권장 방향 |
| --- | --- |
| 재고 차감 실패 시 주문도 실패해야 함 | 예외를 삼키지 말고 바깥까지 전파해 전체 롤백합니다. |
| 실패 기록만 본 트랜잭션과 독립적으로 남겨야 함 | 별도 Bean의 `REQUIRES_NEW`를 제한적으로 사용하거나 트랜잭션 종료 후 이벤트를 처리합니다. |
| 내부 작업만 되돌리고 바깥 작업은 계속해야 함 | Savepoint가 적합한지 검토하고 지원되는 트랜잭션 매니저에서 `NESTED`를 고려합니다. |
| 외부 결제는 실패했지만 주문 상태를 보존해야 함 | 짧은 DB 트랜잭션으로 상태를 전이하고, 외부 호출은 멱등성·재시도·보상 흐름으로 분리합니다. |
| 반드시 하나의 원자적 작업이어야 함 | 같은 `REQUIRED` 경계에서 실패를 전파하고 한 번에 롤백합니다. |

“예외가 났으니 `REQUIRES_NEW`를 붙인다”는 해결법은 위험합니다. 먼저 두 작업이 정말 서로 다른 커밋 운명을 가져야 하는지 비즈니스 원자성을 정해야 합니다.

## 전파 옵션 비교

| 전파 옵션 | 기존 트랜잭션이 있을 때 | 없을 때 | 대표 용도·주의점 |
| --- | --- | --- | --- |
| `REQUIRED` | 참여 | 새로 시작 | 기본값. 하나의 유스케이스를 원자적으로 묶습니다. |
| `REQUIRES_NEW` | 기존 것을 중단하고 새 물리 트랜잭션 시작 | 새로 시작 | 독립 감사 로그 등에 사용. 별도 커넥션과 독립 커밋에 주의합니다. |
| `NESTED` | Savepoint를 만든 중첩 범위 | 새로 시작 | 일부만 롤백. 매니저·드라이버의 Savepoint 지원을 확인합니다. |
| `SUPPORTS` | 참여 | 트랜잭션 없이 실행 | 트랜잭션 유무에 따라 동작이 달라질 수 있어 쓰기 로직에는 신중해야 합니다. |
| `MANDATORY` | 참여 | 예외 발생 | 반드시 상위 트랜잭션 안에서만 실행되어야 하는 내부 작업입니다. |
| `NOT_SUPPORTED` | 기존 것을 중단 | 트랜잭션 없이 실행 | 트랜잭션을 피해야 하는 긴 비DB 작업 등에 검토합니다. |
| `NEVER` | 예외 발생 | 트랜잭션 없이 실행 | 트랜잭션 안에서 호출되면 안 되는 작업을 강제합니다. |

### `REQUIRES_NEW`의 숨은 비용

바깥 트랜잭션이 커넥션 하나를 잡은 채 안쪽 트랜잭션용 커넥션을 하나 더 기다립니다. 동시 요청 수와 커넥션 풀 크기가 빠듯하면 모든 요청이 바깥 커넥션을 점유한 채 새 커넥션을 기다리는 **풀 고갈**이 생길 수 있습니다.

```text
Thread 1: outer connection 보유 ── inner connection 대기
Thread 2: outer connection 보유 ── inner connection 대기
Thread 3: outer connection 보유 ── inner connection 대기
Pool:     남은 connection 0
```

따라서 `REQUIRES_NEW`는 독립 커밋이 정말 필요한 짧은 작업에만 사용하고, 호출 깊이·최대 동시성·풀 크기를 함께 검토해야 합니다.

### `NESTED`와 `REQUIRES_NEW`의 차이

```text
REQUIRES_NEW
outer TX ── suspend ───────────── resume ── commit/rollback
              └─ new TX ───────┘

NESTED
outer TX ───── savepoint ─ rollback to savepoint ─ commit/rollback
```

- `REQUIRES_NEW`는 커밋 운명이 독립적입니다. 안쪽이 커밋된 뒤 바깥이 롤백돼도 안쪽 결과는 남습니다.
- `NESTED`는 같은 물리 트랜잭션의 Savepoint를 사용합니다. 안쪽만 되돌릴 수 있지만 최종적으로 바깥이 롤백되면 안쪽 결과도 함께 사라집니다.
- `NESTED`는 모든 환경에서 동일하게 지원되지 않습니다. 특히 JPA 사용 시 단순히 애노테이션만 붙이면 원하는 Savepoint 동작이 된다고 가정하면 안 됩니다.

## 롤백 규칙

Spring의 기본 규칙은 다음과 같습니다.

- `RuntimeException`과 `Error`: 롤백
- checked exception: 기본적으로 커밋
- 필요하면 `rollbackFor`, `noRollbackFor`로 명시

```java
@Transactional(rollbackFor = PaymentException.class)
public void completePayment() throws PaymentException {
    // checked exception인 PaymentException에도 롤백
}
```

하지만 무조건 `rollbackFor = Exception.class`를 복사해 붙이기 전에, 그 예외가 비즈니스 실패인지 재시도 가능한 기술 실패인지부터 분류해야 합니다. 예외 정책은 트랜잭션의 커밋 정책이기도 합니다.

### 예외를 잡으면 항상 커밋될까?

아닙니다. 어디에서 잡았는지가 중요합니다.

- 대상 `@Transactional` 메서드 **안에서 직접 발생한 예외를 내부에서 잡아 정상 반환**하면 프록시는 예외를 보지 못하므로 기본적으로 커밋을 시도합니다.
- 별도 `REQUIRED` 프록시 메서드가 예외를 보고 rollback-only로 표시한 후 바깥에서 잡으면, 바깥의 물리 트랜잭션은 커밋할 수 없습니다.
- DB 오류에 따라 트랜잭션 자체가 이미 실패 상태가 될 수 있으므로, 예외를 잡고 계속 SQL을 실행하는 것도 안전하다고 가정하면 안 됩니다.

## self-invocation 함정

```java
@Service
public class ReportService {

    public void createAll() {
        createOne(); // this.createOne(): 프록시를 거치지 않음
    }

    @Transactional
    public void createOne() {
        // 기대한 새 트랜잭션 경계가 적용되지 않을 수 있다.
    }
}
```

Spring의 기본 프록시 방식에서는 외부 객체가 프록시를 호출해야 인터셉터가 동작합니다. 해결을 위해 자기 자신 프록시를 억지로 주입하기보다, 트랜잭션 경계가 필요한 책임을 별도 Bean으로 분리하거나 외부 유스케이스 메서드에 경계를 다시 설계하는 편이 명확합니다.

## JPA의 `flush`와 `commit`은 다르다

```text
엔티티 변경
  └─ 영속성 컨텍스트가 변경 감지
       └─ flush: SQL을 DB에 전송
            └─ commit: DB 트랜잭션 확정
```

- `flush()`는 영속성 컨텍스트의 변경 내용을 DB와 동기화하지만 트랜잭션을 확정하지 않습니다.
- flush 후에도 바깥 트랜잭션이 롤백되면 변경은 사라집니다.
- 제약 조건 위반은 `save()` 호출 순간이 아니라 flush 또는 commit 시점에 드러날 수 있습니다.
- 실패를 특정 코드 구간에서 확인해야 한다면 명시적 flush가 필요할 수 있지만, 이는 조기 커밋이 아닙니다.

```java
@Transactional
public Long register(User user) {
    User saved = userRepository.save(user);
    entityManager.flush(); // SQL 실행과 제약 조건 검증을 앞당길 뿐 commit은 아니다.
    return saved.getId();
}
```

## `readOnly = true`를 과신하지 말 것

`@Transactional(readOnly = true)`는 트랜잭션 매니저와 영속성 기술에 전달되는 **읽기 전용 힌트**입니다. JPA 구현체가 flush 전략을 최적화하거나 JDBC 커넥션에 읽기 전용 속성을 전달할 수 있지만, 모든 DB·드라이버 조합에서 쓰기를 물리적으로 차단한다고 보장하지는 않습니다.

읽기 전용의 주된 가치는 의도 표현과 가능한 최적화입니다. 정말 쓰기를 차단해야 한다면 읽기 전용 DB 계정, Replica 라우팅, 권한 정책 같은 데이터베이스 수준의 장치도 필요합니다.

## 외부 API를 트랜잭션 안에 오래 두면 안 되는 이유

```java
@Transactional
public void placeOrder() {
    orderRepository.save(...);
    paymentClient.pay(...); // 느린 네트워크 I/O
    order.markPaid();
}
```

이 구조는 외부 응답을 기다리는 동안 DB 커넥션과 락을 오래 점유합니다. 또한 결제가 성공한 직후 DB 커밋이 실패하면 외부 결제만 남습니다. 로컬 DB 트랜잭션은 결제 서버를 롤백할 수 없습니다.

실무에서는 보통 다음을 조합합니다.

1. 짧은 DB 트랜잭션으로 주문을 `PENDING` 상태로 저장합니다.
2. 커밋된 이벤트를 Outbox 등에 기록합니다.
3. 별도 처리기가 멱등성 키를 사용해 결제를 요청합니다.
4. 결과에 따라 새 트랜잭션에서 `PAID` 또는 `PAYMENT_FAILED`로 전이합니다.
5. 중간 실패에는 재시도하고, 되돌릴 수 없는 성공에는 취소 같은 보상 작업을 둡니다.

원자성의 범위가 DB 하나를 넘어서는 순간부터는 애노테이션보다 **상태 머신과 실패 복구 설계**가 핵심입니다.

## 격리 수준과 전파를 함께 볼 때

```java
@Transactional(
        propagation = Propagation.REQUIRED,
        isolation = Isolation.REPEATABLE_READ
)
public void update() {
}
```

격리 수준은 일반적으로 새 물리 트랜잭션을 시작할 때 의미가 있습니다. 이미 시작된 트랜잭션에 `REQUIRED`로 참여하는 내부 메서드가 다른 격리 수준을 선언해도 새 DB 트랜잭션이 생기지 않으므로 기대대로 바뀐다고 가정하면 안 됩니다. 트랜잭션의 시작 지점에서 격리 수준을 결정하고, 사용하는 DBMS의 실제 구현과 기본값을 확인해야 합니다.

## 실무 설계 체크리스트

- 트랜잭션 경계가 하나의 비즈니스 유스케이스와 일치하는가?
- 내부 호출이 실제로 프록시를 통과하는가?
- 예외를 잡았을 때 이미 rollback-only가 된 참여 트랜잭션은 없는가?
- checked exception의 롤백 정책이 의도와 일치하는가?
- `REQUIRES_NEW`가 정말 독립 커밋이어야 하며 커넥션 풀 여유가 있는가?
- 외부 API 호출 동안 DB 커넥션과 락을 붙들고 있지 않은가?
- flush 시점과 commit 시점을 구분하고 있는가?
- 비동기·새 스레드·메시지 소비 경계에서 트랜잭션이 자동 전파된다고 착각하지 않았는가?
- 통합 테스트에서 최종 DB 상태와 발생 예외를 함께 검증했는가?

## 테스트로 확인할 시나리오

```java
@SpringBootTest
class OrderTransactionTest {

    @Autowired OrderService orderService;
    @Autowired OrderRepository orderRepository;

    @Test
    void 내부_REQUIRED가_rollbackOnly로_표시하면_바깥_커밋은_실패한다() {
        assertThatThrownBy(() -> orderService.createOrder(outOfStockCommand()))
                .isInstanceOf(UnexpectedRollbackException.class);

        assertThat(orderRepository.count()).isZero();
    }
}
```

트랜잭션 테스트 자체에 `@Transactional`을 붙이면 테스트 프레임워크의 롤백과 서비스 트랜잭션이 섞여 결과를 오해할 수 있습니다. 전파와 최종 커밋 여부를 검증하는 테스트에서는 테스트 메서드의 트랜잭션 유무를 의도적으로 결정해야 합니다.

## 자주 나오는 꼬리 질문

### Q1. `REQUIRED`와 `REQUIRES_NEW`의 차이는 무엇인가요?

`REQUIRED`는 기존 트랜잭션이 있으면 참여해 하나의 물리 트랜잭션과 커밋 운명을 공유합니다. `REQUIRES_NEW`는 기존 트랜잭션을 중단하고 독립적인 물리 트랜잭션과 커넥션을 사용합니다. 독립 커밋이 가능하지만 원자성이 분리되고 커넥션 풀 부담이 커집니다.

### Q2. 예외를 잡았는데 왜 `UnexpectedRollbackException`이 발생하나요?

안쪽 `REQUIRED` 프록시가 런타임 예외를 보고 공유 트랜잭션을 rollback-only로 표시했기 때문입니다. 바깥 코드의 `catch`는 그 표시를 취소하지 못하고, 최종 커밋 시도가 실제 롤백으로 바뀌면서 호출자에게 예외가 전달됩니다.

### Q3. `NESTED`와 `REQUIRES_NEW`는 어떻게 다른가요?

`NESTED`는 같은 물리 트랜잭션에서 Savepoint를 사용해 부분 롤백하고, 바깥이 롤백되면 함께 롤백됩니다. `REQUIRES_NEW`는 별도 물리 트랜잭션이므로 안쪽 커밋 후 바깥이 롤백되어도 안쪽 결과가 남습니다.

### Q4. `@Transactional`을 private 메서드에 붙이면 왜 문제가 되나요?

핵심은 접근 제한자 자체보다 해당 호출이 Spring 프록시를 통과하느냐입니다. 같은 객체 내부의 직접 호출은 프록시를 우회하므로 트랜잭션 인터셉터가 실행되지 않습니다. 프록시 방식과 메서드 가시성의 제약도 함께 확인해야 합니다.

### Q5. `save()`가 성공하면 DB 반영도 성공한 것인가요?

항상 그렇지는 않습니다. JPA는 쓰기 지연과 변경 감지를 사용하므로 SQL 실행이나 제약 조건 검증이 flush·commit 시점까지 미뤄질 수 있습니다. `save()` 반환은 트랜잭션의 최종 커밋 성공을 뜻하지 않습니다.

### Q6. 트랜잭션에서 외부 API를 호출하면 함께 롤백되나요?

아닙니다. 일반적인 DB 트랜잭션은 외부 HTTP 요청의 결과를 롤백할 수 없습니다. 멱등성 키, Outbox, 재시도, 상태 전이, 보상 요청을 통해 분산 실패를 설계해야 합니다.

## 30초 면접 답변

> Spring의 `@Transactional`은 프록시가 메서드 호출을 가로채 트랜잭션을 시작하거나 기존 트랜잭션에 참여시키는 방식입니다. 기본 전파인 `REQUIRED`에서는 내부와 외부 메서드가 같은 물리 트랜잭션을 공유합니다. 그래서 내부 프록시가 런타임 예외를 보고 rollback-only로 표시하면 바깥에서 예외를 잡아도 커밋할 수 없고, 최종 시점에 `UnexpectedRollbackException`이 발생할 수 있습니다. 독립 커밋이 필요하면 `REQUIRES_NEW`를 검토하지만 원자성 분리와 추가 커넥션 비용이 있으므로 비즈니스 경계를 먼저 판단해야 합니다.

## 스스로 점검하기

1. 논리 트랜잭션 두 개가 물리 트랜잭션 하나를 공유한다는 말을 그림 없이 설명할 수 있는가?
2. `catch`가 rollback-only를 취소하지 못하는 이유를 프록시 실행 순서로 설명할 수 있는가?
3. 감사 로그에 `REQUIRES_NEW`를 사용할 때 생기는 원자성·커넥션 풀 문제를 말할 수 있는가?
4. 외부 결제 API가 포함된 주문 흐름을 짧은 트랜잭션과 상태 전이로 다시 설계할 수 있는가?
5. `flush()`와 `commit()`의 차이를 제약 조건 예외 발생 시점과 연결해 설명할 수 있는가?

---

## 오늘의 연결 고리

두 주제는 겉으로 전혀 달라 보이지만 공통점이 있습니다.

- Red-Black Tree는 **불변식**을 정하고, 삽입·삭제가 불변식을 깨면 회전과 재색칠로 복구합니다.
- 트랜잭션은 **원자성과 일관성의 경계**를 정하고, 실패하면 커밋 대신 롤백이나 보상으로 상태를 복구합니다.

면접에서도 구현 세부사항을 무작정 외우기보다 “어떤 불변식을 지키는가 → 무엇이 그 불변식을 깨는가 → 어떤 비용으로 복구하는가”의 순서로 설명하면 낯선 꼬리 질문에도 대응하기 쉽습니다.
