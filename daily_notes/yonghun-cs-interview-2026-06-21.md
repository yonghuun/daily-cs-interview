# 2026-06-21 일일 CS/면접 지식

---

# 오늘의 CS 지식

## 주제

이진 트리(Binary Tree)

## 카테고리

`algorithm`

## 핵심 요약

- 이진 트리는 각 노드가 **최대 두 개의 자식**을 갖는 트리입니다. 왼쪽·오른쪽 자식의 위치는 구분됩니다.
- 이진 트리 자체는 정렬 규칙이 아닙니다. 탐색 성능은 트리의 모양과 추가 규칙(BST 등)에 따라 달라집니다.
- 완전 이진 트리는 마지막 레벨을 제외한 모든 레벨이 채워지고, 마지막 레벨도 왼쪽부터 채워지는 형태입니다. 배열로 효율적으로 표현할 수 있어 힙에 쓰입니다.
- 이진 탐색 트리(BST)는 `left < node < right` 규칙을 추가한 이진 트리이며, 균형이 맞을 때 탐색·삽입·삭제가 `O(log n)`입니다.

## 면접 포인트

| 질문 포인트 | 핵심 키워드 |
| --- | --- |
| 정의 | 한 노드의 자식 수가 최대 2개인 계층 자료구조 |
| 핵심 구분 | 이진 트리 ≠ 이진 탐색 트리(BST) ≠ 완전 이진 트리 |
| 시간 복잡도 | 순회는 `O(n)`; BST 연산은 균형 시 `O(log n)`, 편향 시 `O(n)` |
| 배열 표현 | 0번 인덱스 기준 부모 `(i - 1) / 2`, 왼쪽 `2i + 1`, 오른쪽 `2i + 2` |
| 실무 활용 | 힙 기반 우선순위 큐, 정렬된 맵/셋, 파일·DB 인덱스의 트리 구조 이해 |

## 자주 나오는 면접 질문

| 질문 | 핵심 답변 방향 |
| --- | --- |
| 이진 트리와 BST의 차이는 무엇인가요? | BST는 키의 대소 관계 규칙을 가진 이진 트리입니다. |
| 완전 이진 트리가 왜 배열 표현에 유리한가요? | 노드 위치에 빈칸이 거의 없어 인덱스 계산만으로 부모·자식을 찾습니다. |
| BST가 항상 `O(log n)`인가요? | 아닙니다. 한쪽으로 치우치면 연결 리스트처럼 `O(n)`이 됩니다. |
| Java의 `PriorityQueue`는 어떤 트리 구조인가요? | 완전 이진 트리 형태의 이진 힙을 배열에 저장합니다. |
| `TreeMap`은 왜 정렬을 보장하나요? | Red-Black Tree로 키를 정렬해 관리합니다. |

## 면접 답변 예시

### 이진 트리(Binary Tree)를 한 문장으로 설명해주세요.

이진 트리는 한 노드가 최대 두 자식을 갖는 트리입니다. 다만 이 말만으로는 값의 정렬이나 탐색 성능을 보장하지 않습니다. 예를 들어 BST는 왼쪽 서브트리의 키가 현재 노드보다 작고 오른쪽은 큰 규칙을 추가합니다. 반면 완전 이진 트리는 모양을 제한해 배열 저장에 유리하며, 이진 힙의 기반이 됩니다.

### 이진 트리(Binary Tree)가 필요한 이유는 무엇인가요?

데이터를 계층적으로 관리하면서 탐색, 우선순위 처리, 정렬된 범위 조회를 수행하기 위해 사용합니다. 필요한 성질에 따라 구조를 고릅니다. 우선순위가 필요하면 힙, 키 정렬·범위 조회가 필요하면 균형 BST, 빠른 동등성 조회가 필요하면 보통 해시 테이블이 더 적합합니다.

### 이진 트리(Binary Tree)의 장점과 단점은 무엇인가요?

균형 잡힌 트리는 탐색·삽입·삭제를 `O(log n)`에 수행할 수 있고, 중위 순회로 정렬된 결과를 얻기 쉽습니다. 반면 포인터 기반 노드는 배열보다 메모리 지역성이 떨어질 수 있고, 균형을 유지하지 않는 BST는 편향되어 `O(n)`까지 느려집니다. 삽입 순서가 예측되지 않는 서비스에서는 직접 BST를 구현하기보다 검증된 균형 트리 구현을 쓰는 편이 안전합니다.

### 이진 트리(Binary Tree)와 비슷한 개념을 비교해서 설명해주세요.

이진 트리는 자식 수만 제한합니다. BST는 키 정렬 규칙을, 완전 이진 트리는 노드 배치 규칙을, 이진 힙은 부모-자식 간 우선순위 규칙을 추가합니다. 따라서 힙은 최솟값/최댓값 확인에는 좋지만 임의 원소 검색에는 적합하지 않고, BST는 정렬과 범위 조회에 강합니다.

### 실무에서 이진 트리(Binary Tree)를 사용할 때 주의할 점은 무엇인가요?

Java에서는 `PriorityQueue`로 작업 스케줄링·상위 N개 처리를 구현할 수 있고, `TreeMap`·`TreeSet`으로 키 정렬과 범위 조회를 할 수 있습니다. 동시 접근이 필요하면 `PriorityQueue` 자체는 스레드 안전하지 않음을 주의하고, 용도에 따라 `PriorityBlockingQueue` 또는 외부 동기화를 검토합니다.

## 실무 관점

- `algorithm` 영역에서 이진 트리(Binary Tree)가 실제 시스템의 성능, 안정성, 유지보수성에 어떤 영향을 주는지 연결해 봅니다.
- 비슷한 개념과 비교하면서 언제 이 개념을 선택하고 언제 다른 대안을 선택할지 정리합니다.
- 운영 환경에서는 데이터 크기, 장애 상황, 보안 요구사항, 성능 병목을 함께 고려합니다.

## 코드 예시

```java
// Java PriorityQueue는 배열 기반의 완전 이진 힙이다.
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
minHeap.offer(30);
minHeap.offer(10);
minHeap.offer(20);

System.out.println(minHeap.peek()); // 10: 최솟값 확인 O(1)
System.out.println(minHeap.poll()); // 10: 삭제 후 힙 재구성 O(log n)
```

## 상세 설명

### 관련 구조 비교

| 구조 | 추가 규칙 | 대표 용도 |
| --- | --- | --- |
| 이진 트리 | 자식이 최대 2개 | 계층 구조의 기본 모델 |
| 완전 이진 트리 | 마지막 레벨만 왼쪽부터 채움 | 배열 기반 이진 힙 |
| BST | 왼쪽 키 < 노드 키 < 오른쪽 키 | 정렬, 범위 조회 |
| 균형 BST | 높이를 `O(log n)`으로 유지 | `TreeMap`, `TreeSet` |

### 배열 기반 완전 이진 트리

루트가 인덱스 `0`일 때 인덱스 `i`의 부모는 `(i - 1) / 2`, 왼쪽 자식은 `2i + 1`, 오른쪽 자식은 `2i + 2`입니다. 완전 이진 트리는 중간 빈칸이 없어 이 계산으로 노드를 바로 찾을 수 있습니다. 일반 이진 트리는 빈칸이 많을 수 있어 보통 노드 참조 방식으로 표현합니다.

---

# 오늘의 Spring 백엔드 지식

## 주제

Spring MVC와 DispatcherServlet

## Spring 핵심 요약

- DispatcherServlet은 Spring MVC의 프론트 컨트롤러로 모든 웹 요청을 받아 적절한 핸들러로 위임합니다.
- 요청은 HandlerMapping, HandlerAdapter, Controller, ViewResolver 또는 MessageConverter 흐름을 거칩니다.
- REST API에서는 보통 ViewResolver보다 `HttpMessageConverter`를 통해 JSON 응답을 만듭니다.

## 동작 원리

1. 요청이 Servlet Container를 거쳐 DispatcherServlet에 도착합니다.
2. HandlerMapping이 요청을 처리할 Controller 메서드를 찾습니다.
3. HandlerAdapter가 Controller 메서드를 호출합니다.
4. 반환값은 ViewResolver 또는 HttpMessageConverter를 통해 응답으로 변환됩니다.
5. 예외가 발생하면 HandlerExceptionResolver나 ControllerAdvice가 응답을 구성합니다.

## 내부 구성 요소

| 구성 요소 | 역할 |
| --- | --- |
| DispatcherServlet | 모든 웹 요청의 중앙 진입점입니다. |
| HandlerMapping | 요청을 처리할 핸들러를 찾습니다. |
| HandlerAdapter | 찾은 핸들러를 실제로 호출합니다. |
| ViewResolver | 뷰 이름을 실제 뷰로 해석합니다. |
| HttpMessageConverter | 객체와 JSON 같은 HTTP body를 변환합니다. |

## 실무 구현 포인트

| 상황 | 권장 방식 | 이유 |
| --- | --- | --- |
| 실무 적용 | 화면 반환 Controller와 REST Controller의 차이를 구분합니다 | 일관된 구조와 유지보수성을 높이기 위해서입니다. |
| 공통 예외 처리 | `@ControllerAdvice` 또는 `@RestControllerAdvice`로 분리합니다 | 책임과 변경 범위를 명확히 하기 위해서입니다. |
| 공통 인증/로깅 | Filter 또는 Interceptor의 실행 위치를 검토합니다 | 책임과 변경 범위를 명확히 하기 위해서입니다. |
| 실무 적용 | 요청/응답 로깅을 넣을 때 민감 정보가 남지 않게 주의합니다 | 일관된 구조와 유지보수성을 높이기 위해서입니다. |

## 주의사항

- Filter와 Interceptor의 실행 위치를 구분해서 공통 로직을 배치합니다.
- REST API에서는 ViewResolver가 아니라 HttpMessageConverter 흐름을 이해합니다.
- 요청/응답 로깅 시 개인정보와 인증 토큰이 남지 않게 주의합니다.
- Controller가 화면/응답 변환 이상의 비즈니스 판단을 직접 하지 않게 합니다.

## 코드 예시

```java
@RestController
@RequestMapping("/api/orders")
class OrderController {

    @GetMapping("/{orderId}")
    OrderResponse findOrder(@PathVariable Long orderId) {
        return new OrderResponse(orderId);
    }
}
```

## 자주 나오는 꼬리 질문

| 질문 | 핵심 답변 방향 |
| --- | --- |
| DispatcherServlet의 역할은 무엇인가요? | 정의, 동작 원리, 실무 주의점을 연결해 답변합니다. |
| Filter와 Interceptor는 어떤 차이가 있나요? | 책임, 동작 위치, 사용 시점을 기준으로 비교합니다. |
| `@Controller`와 `@RestController`의 차이는 무엇인가요? | 책임, 동작 위치, 사용 시점을 기준으로 비교합니다. |
| Spring MVC에서 JSON 응답은 어떻게 만들어지나요? | 처리 순서와 관련 컴포넌트를 단계적으로 설명합니다. |

## Spring 면접 답변 예시

### Q. DispatcherServlet의 역할은 무엇인가요?

DispatcherServlet은 Spring MVC의 프론트 컨트롤러로, 들어온 요청을 받아 어떤 Controller 메서드가 처리할지 찾고 호출하는 중심 역할을 합니다. REST API에서는 Controller가 반환한 객체를 `HttpMessageConverter`가 JSON으로 변환해 응답합니다. Filter는 Servlet 영역에서 동작하고 Interceptor는 Spring MVC 핸들러 호출 전후에 동작하므로, 인증이나 로깅 같은 공통 처리를 넣을 때 위치를 구분해야 합니다.

### Q. 실무에서 Spring MVC와 DispatcherServlet을 적용할 때 무엇을 주의해야 하나요?

Filter와 Interceptor의 실행 위치를 구분해서 공통 로직을 배치합니다. REST API에서는 ViewResolver가 아니라 HttpMessageConverter 흐름을 이해합니다.

## 함께 알아야 하는 개념

| 개념 | 함께 알아야 하는 이유 |
| --- | --- |
| Filter | Servlet 레벨의 공통 처리를 담당합니다. |
| Interceptor | Spring MVC 핸들러 호출 전후 처리를 담당합니다. |
| ArgumentResolver | Controller 파라미터 바인딩을 확장합니다. |
| MessageConverter | JSON 요청/응답 변환을 담당합니다. |

- PetClinic은 Spring Boot 기반 MVC 샘플이라 Controller 요청 흐름과 화면 렌더링 구조를 확인하는 참고 자료로 좋습니다.

## 상세 설명

- 프론트 컨트롤러 패턴은 공통 웹 처리 진입점을 하나로 모아 인증, 로깅, 라우팅, 예외 처리 구성을 단순화합니다.

- `@Controller`나 `@RestController`의 메서드는 HandlerMapping에 의해 매핑되고 HandlerAdapter를 통해 호출됩니다.

- `@ResponseBody` 또는 `@RestController`를 사용하면 반환 객체가 JSON 같은 HTTP body로 변환됩니다.
