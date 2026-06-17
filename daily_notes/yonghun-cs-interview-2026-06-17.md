# 2026-06-17 1일 2CS/면접 지식

## 오늘의 CS 지식

완전탐색(brute force search)

## 카테고리

`algorithm`

## 핵심 요약

- 완전탐색은 문제 해결법 중 하나로, 가능한 모든 경우의 수를 다 검사하는것으로 다른 방법들보다 느리지만 항상 정확한 결과를 도출한
- 예를들어, 순열을 구하는 문제에서 완전탐색은 가능한 모든 조합을 다 찾아본
- 이러한 완전탐색은 문제 해결에 있어 유용하지만, 문제의 크기가 커질수록 시간 복잡도가 증가하기 때문에 주의하여야 한다.

## 조금 더 자세히

완전탐색은 문제 해결법 중 하나로, 가능한 모든 경우의 수를 다 검사하는것으로 다른 방법들보다 느리지만 항상 정확한 결과를 도출한다.

예를들어, 순열을 구하는 문제에서 완전탐색은 가능한 모든 조합을 다 찾아본다.

이러한 완전탐색은 문제 해결에 있어 유용하지만, 문제의 크기가 커질수록 시간 복잡도가 증가하기 때문에 주의하여야 한다.

## 면접 포인트

- 완전탐색(brute force search): 무엇인지 한 문장으로 설명할 수 있어야 합니다.
- 핵심 키워드: 문제, 완전탐색, 가능한, 모든, brute
- 비슷한 개념과 비교했을 때 어떤 차이가 있는지 정리해두면 좋습니다.
- 실무에서 성능, 안정성, 확장성 중 무엇에 영향을 주는지 연결해서 생각해봅니다.

## 연관되어 자주 나오는 면접 질문

- 완전탐색(brute force search)를 한 문장으로 설명해주세요.
- 완전탐색(brute force search)가 필요한 이유는 무엇인가요?
- 완전탐색(brute force search)의 장점과 단점은 무엇인가요?
- 완전탐색(brute force search)와 비슷한 개념을 비교해서 설명해주세요.
- 실무에서 완전탐색(brute force search)를 사용할 때 주의할 점은 무엇인가요?

## 면접 답변 예시

### 완전탐색(brute force search)를 한 문장으로 설명해주세요.

완전탐색(brute force search)는 가능한 모든 경우의 수를 빠짐없이 확인해서 조건에 맞는 정답을 찾는 탐색 방법입니다.

### 완전탐색(brute force search)가 필요한 이유는 무엇인가요?

입력 크기가 작거나 경우의 수가 제한적인 문제에서는 복잡한 최적화 기법보다 완전탐색이 가장 단순하고 확실한 해결책이 될 수 있습니다. 또한 더 효율적인 알고리즘을 설계하기 전에 정답 검증용 기준 풀이로도 자주 사용됩니다.

### 완전탐색(brute force search)의 장점과 단점은 무엇인가요?

장점은 구현이 비교적 직관적이고, 가능한 경우를 모두 확인하기 때문에 조건만 올바르면 정답을 놓치지 않는다는 점입니다.

단점은 경우의 수가 커질수록 시간 복잡도가 급격히 증가한다는 점입니다. 예를 들어 순열, 조합, 부분집합처럼 경우의 수가 지수적으로 늘어나는 문제에서는 입력 크기가 조금만 커져도 실행 시간이 현실적으로 감당되지 않을 수 있습니다.

### 완전탐색(brute force search)와 비슷한 개념을 비교해서 설명해주세요.

완전탐색은 모든 후보를 검사하는 방식이고, 그리디나 동적 계획법은 문제의 특성을 이용해 검사해야 할 후보를 줄이는 방식입니다. 그리디는 매 순간 최선의 선택이 전체 최적해로 이어진다는 조건이 필요하고, 동적 계획법은 중복 부분 문제와 최적 부분 구조가 있을 때 효과적입니다.

### 실무에서 완전탐색(brute force search)를 사용할 때 주의할 점은 무엇인가요?

먼저 입력 크기와 가능한 경우의 수를 계산해서 제한 시간 안에 실행 가능한지 확인해야 합니다. 완전탐색이 너무 느리다면 가지치기, 정렬, 해시, 백트래킹, 동적 계획법 같은 방법으로 탐색 범위를 줄일 수 있는지 검토하는 것이 좋습니다.

---

## 오늘의 Spring 백엔드 지식

REST API 설계 기본

## Spring 핵심 요약

- REST API는 HTTP 자원을 URI로 표현하고, HTTP 메서드로 행위를 표현하는 API 설계 방식입니다.
- 백엔드 구현에서는 URI, 메서드, 상태 코드, 요청/응답 DTO, 에러 응답 형식을 일관되게 잡는 것이 핵심입니다.
- 좋은 REST API는 Controller 코드보다 먼저 리소스 모델과 클라이언트 사용 흐름이 분명해야 합니다.

## Spring 조금 더 자세히

- `GET /owners/{ownerId}`처럼 URI는 행위가 아니라 자원을 나타내고, 조회/생성/수정/삭제는 `GET`, `POST`, `PUT/PATCH`, `DELETE`로 표현합니다.
- 응답은 성공과 실패 모두 예측 가능해야 합니다. 성공 시에는 적절한 HTTP 상태 코드와 DTO를 반환하고, 실패 시에는 에러 코드, 메시지, 상세 정보를 일정한 포맷으로 내려주는 것이 좋습니다.
- Entity를 그대로 응답으로 내보내면 도메인 구조가 API 계약이 되어버릴 수 있으므로, 보통 요청 DTO와 응답 DTO를 분리합니다.

## Spring 구현 체크리스트

- Controller는 HTTP 요청 매핑, 입력 검증, 응답 변환에 집중합니다.
- Service는 유스케이스와 비즈니스 규칙을 담당하고, Repository는 데이터 접근만 담당하게 분리합니다.
- `@Valid`로 요청 DTO를 검증하고, 예외는 `@RestControllerAdvice`에서 공통 응답으로 변환합니다.
- 목록 조회 API는 처음부터 페이징, 정렬, 검색 조건을 고려합니다.

## Spring 코드 예시

### 요청/응답 DTO와 Controller 예시

```java
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/owners")
class OwnerController {

    private final OwnerService ownerService;

    OwnerController(OwnerService ownerService) {
        this.ownerService = ownerService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    OwnerResponse create(@Valid @RequestBody CreateOwnerRequest request) {
        return ownerService.create(request);
    }

    @GetMapping("/{ownerId}")
    OwnerResponse findById(@PathVariable Long ownerId) {
        return ownerService.findById(ownerId);
    }
}

record CreateOwnerRequest(
        @NotBlank @Size(max = 40) String name,
        @NotBlank @Size(max = 20) String phone
) {
}

record OwnerResponse(
        Long id,
        String name,
        String phone
) {
}
```

### Service와 예외 응답 예시

```java
import java.time.Instant;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.*;

class OwnerService {

    private final OwnerRepository ownerRepository;

    OwnerService(OwnerRepository ownerRepository) {
        this.ownerRepository = ownerRepository;
    }

    OwnerResponse findById(Long ownerId) {
        Owner owner = ownerRepository.findById(ownerId)
                .orElseThrow(() -> new OwnerNotFoundException(ownerId));
        return new OwnerResponse(owner.getId(), owner.getName(), owner.getPhone());
    }

    OwnerResponse create(CreateOwnerRequest request) {
        Owner owner = ownerRepository.save(new Owner(request.name(), request.phone()));
        return new OwnerResponse(owner.getId(), owner.getName(), owner.getPhone());
    }
}

@RestControllerAdvice
class ApiExceptionHandler {

    @ExceptionHandler(OwnerNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    ErrorResponse handleNotFound(OwnerNotFoundException exception) {
        return new ErrorResponse("OWNER_NOT_FOUND", exception.getMessage(), Instant.now());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    ErrorResponse handleValidation(MethodArgumentNotValidException exception) {
        String message = exception.getBindingResult().getFieldErrors().stream()
                .findFirst()
                .map(error -> error.getField() + ": " + error.getDefaultMessage())
                .orElse("Invalid request");
        return new ErrorResponse("INVALID_REQUEST", message, Instant.now());
    }
}

record ErrorResponse(String code, String message, Instant timestamp) {
}
```


### PetClinic 참고 포인트

- PetClinic은 Owner, Pet, Visit 같은 도메인을 기준으로 화면과 요청 흐름을 나누고 있어 리소스 중심 설계를 읽어보기 좋습니다.

## Spring 면접 질문

- REST API에서 URI와 HTTP 메서드는 각각 어떤 책임을 가지나요?
- `PUT`과 `PATCH`의 차이는 무엇인가요?
- Entity를 그대로 API 응답으로 반환하면 어떤 문제가 생길 수 있나요?
- Spring에서 API 에러 응답을 일관되게 처리하려면 어떻게 구성하나요?

## Spring 면접 답변 예시

REST API는 자원을 URI로 표현하고 HTTP 메서드로 행위를 표현하는 방식입니다. Spring에서는 Controller가 요청을 받고 DTO로 입력을 검증한 뒤, Service에 유스케이스 처리를 위임하는 구조로 구현합니다. Entity를 직접 노출하면 내부 도메인 구조가 외부 API 계약이 될 수 있으므로 요청/응답 DTO를 분리하는 것이 좋습니다. 또한 성공 응답뿐 아니라 실패 응답도 `@RestControllerAdvice`로 일관된 포맷과 상태 코드를 제공해야 운영과 클라이언트 연동이 쉬워집니다.

