#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MY_MATERIALS_DIR = ROOT / "my_materials"
REFERENCES_DIR = ROOT / "references"
CURATED_REFERENCES_DIR = REFERENCES_DIR / "curated"
REFERENCE_SOURCES_DIR = REFERENCES_DIR / "sources"
DAILY_NOTES_DIR = ROOT / "daily_notes"
STUDY_STATE_DIR = ROOT / "study_state"
STUDIED_ITEMS_FILE = STUDY_STATE_DIR / "studied_items.json"
SPRING_STUDIED_ITEMS_FILE = STUDY_STATE_DIR / "spring_studied_items.json"
STUDY_LOG_FILE = STUDY_STATE_DIR / "study_log.json"
REFERENCE_REPOS_FILE = ROOT / "reference_repos.json"
IGNORED_DIRS = {".git", ".github", "assets", "asset", "image", "images", "img", "resources"}
IGNORED_FILES = {"pull_request_template.md", "issue_template.md"}
CATEGORY_ALIASES = {
    "algorithm": {"algorithm", "algo", "자료구조", "알고리즘"},
    "db": {"db", "database", "데이터베이스"},
    "design": {"design", "design-pattern", "디자인", "디자인패턴"},
    "java": {"java", "자바"},
    "jpa": {"jpa"},
    "network": {"network", "net", "네트워크"},
    "os": {"os", "operating-system", "운영체제"},
    "spring": {"spring", "스프링"},
    "web": {"web", "웹"},
}
NOISE_TITLES = {
    "backend-interview-question",
    "check",
    "contents",
    "contributors",
    "information",
    "readme",
    "sample cs questions",
    "special thanks to",
    "table of contents",
    "단점",
    "삭제",
    "삽입",
    "장점",
    "정리",
    "특징",
    "개념도",
    "예시",
    "목차",
}


STOPWORDS = {
    "and",
    "the",
    "with",
    "that",
    "this",
    "있다",
    "있는",
    "한다",
    "대한",
    "대해",
    "설명",
    "설명해보세요",
    "설명해주세요",
    "차이",
    "차이점",
    "무엇",
    "무엇인가",
    "사용",
    "경우",
    "것",
    "가지",
    "많이",
    "무엇인가요",
    "무엇이고",
    "대해서",
    "때문",
    "이유",
    "정의",
    "좋은데",
}

@dataclass(frozen=True)
class StudyItem:
    title: str
    body: str
    source: Path
    category: str
    github_url: str | None = None

    @property
    def key(self) -> str:
        raw = f"{source_identity(self.source)}\n{self.title}\n{self.body}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class SpringTopic:
    key: str
    title: str
    summary: tuple[str, ...]
    details: tuple[str, ...]
    implementation: tuple[str, ...]
    questions: tuple[str, ...]
    answer: str
    code_examples: tuple[str, ...] = ()
    petclinic_hint: str = ""


SPRING_CURRICULUM: tuple[SpringTopic, ...] = (
    SpringTopic(
        key="spring-rest-api-basics",
        title="REST API 설계 기본",
        summary=(
            "REST API는 HTTP 자원을 URI로 표현하고, HTTP 메서드로 행위를 표현하는 API 설계 방식입니다.",
            "백엔드 구현에서는 URI, 메서드, 상태 코드, 요청/응답 DTO, 에러 응답 형식을 일관되게 잡는 것이 핵심입니다.",
            "좋은 REST API는 Controller 코드보다 먼저 리소스 모델과 클라이언트 사용 흐름이 분명해야 합니다.",
        ),
        details=(
            "`GET /owners/{ownerId}`처럼 URI는 행위가 아니라 자원을 나타내고, 조회/생성/수정/삭제는 `GET`, `POST`, `PUT/PATCH`, `DELETE`로 표현합니다.",
            "응답은 성공과 실패 모두 예측 가능해야 합니다. 성공 시에는 적절한 HTTP 상태 코드와 DTO를 반환하고, 실패 시에는 에러 코드, 메시지, 상세 정보를 일정한 포맷으로 내려주는 것이 좋습니다.",
            "Entity를 그대로 응답으로 내보내면 도메인 구조가 API 계약이 되어버릴 수 있으므로, 보통 요청 DTO와 응답 DTO를 분리합니다.",
        ),
        implementation=(
            "Controller는 HTTP 요청 매핑, 입력 검증, 응답 변환에 집중합니다.",
            "Service는 유스케이스와 비즈니스 규칙을 담당하고, Repository는 데이터 접근만 담당하게 분리합니다.",
            "`@Valid`로 요청 DTO를 검증하고, 예외는 `@RestControllerAdvice`에서 공통 응답으로 변환합니다.",
            "목록 조회 API는 처음부터 페이징, 정렬, 검색 조건을 고려합니다.",
        ),
        questions=(
            "REST API에서 URI와 HTTP 메서드는 각각 어떤 책임을 가지나요?",
            "`PUT`과 `PATCH`의 차이는 무엇인가요?",
            "Entity를 그대로 API 응답으로 반환하면 어떤 문제가 생길 수 있나요?",
            "Spring에서 API 에러 응답을 일관되게 처리하려면 어떻게 구성하나요?",
        ),
        answer=(
            "REST API는 자원을 URI로 표현하고 HTTP 메서드로 행위를 표현하는 방식입니다. "
            "Spring에서는 Controller가 요청을 받고 DTO로 입력을 검증한 뒤, Service에 유스케이스 처리를 위임하는 구조로 구현합니다. "
            "Entity를 직접 노출하면 내부 도메인 구조가 외부 API 계약이 될 수 있으므로 요청/응답 DTO를 분리하는 것이 좋습니다. "
            "또한 성공 응답뿐 아니라 실패 응답도 `@RestControllerAdvice`로 일관된 포맷과 상태 코드를 제공해야 운영과 클라이언트 연동이 쉬워집니다."
        ),
        code_examples=(
            """### 요청/응답 DTO와 Controller 예시

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
""",
            """### Service와 예외 응답 예시

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
""",
        ),
        petclinic_hint="PetClinic은 Owner, Pet, Visit 같은 도메인을 기준으로 화면과 요청 흐름을 나누고 있어 리소스 중심 설계를 읽어보기 좋습니다.",
    ),
    SpringTopic(
        key="spring-layered-architecture",
        title="Controller-Service-Repository 계층 분리",
        summary=(
            "Spring 백엔드의 기본 구조는 Controller, Service, Repository 계층으로 책임을 나누는 것입니다.",
            "계층 분리는 코드 위치를 나누는 일이 아니라 변경 이유와 테스트 범위를 나누는 일입니다.",
            "면접에서는 각 계층의 책임뿐 아니라 Controller가 비대해지는 문제, 트랜잭션 경계, 테스트 전략까지 함께 설명하는 것이 좋습니다.",
        ),
        details=(
            "Controller는 HTTP 요청/응답, 라우팅, 파라미터 바인딩, 입력 검증, 상태 코드 변환을 담당합니다. 요청을 받은 뒤에는 비즈니스 판단을 직접 하지 않고 Service에 유스케이스 실행을 위임합니다.",
            "Service는 하나의 유스케이스를 처리하는 계층입니다. 여러 Repository 호출을 조합하고, 도메인 규칙을 적용하며, 보통 이곳에 `@Transactional`을 두어 작업 단위를 명확히 합니다.",
            "Repository는 DB 접근을 추상화하고 쿼리나 영속성 기술의 세부 사항을 감춥니다. Service는 Repository 인터페이스를 통해 필요한 데이터를 요청하고, SQL/JPA 구현 세부 사항에 덜 의존하게 됩니다.",
            "계층 분리는 변경의 전파를 줄입니다. API 표현 방식이 바뀌면 Controller와 DTO 중심으로, 비즈니스 규칙이 바뀌면 Service 중심으로, 쿼리 방식이 바뀌면 Repository 중심으로 수정 범위를 좁힐 수 있습니다.",
        ),
        implementation=(
            "Controller에서는 요청 DTO 검증, PathVariable/RequestParam 처리, 응답 DTO 반환에 집중합니다.",
            "Service 메서드는 `createOwner`, `registerVisit`, `changePassword`처럼 유스케이스 단위로 이름을 짓습니다.",
            "변경 작업 Service에는 보통 `@Transactional`을 두고, 단순 조회는 `@Transactional(readOnly = true)`를 검토합니다.",
            "Repository는 조회 조건과 저장/삭제 같은 데이터 접근 책임에 집중하고, 화면/API 전용 조합 로직은 무리하게 넣지 않습니다.",
            "테스트는 Controller 슬라이스 테스트, Service 단위 테스트, Repository 통합 테스트처럼 검증 목적에 맞게 나눕니다.",
        ),
        questions=(
            "Controller, Service, Repository를 나누는 이유는 무엇인가요?",
            "Service 계층에 트랜잭션을 두는 이유는 무엇인가요?",
            "Controller에 비즈니스 로직이 많아지면 어떤 문제가 생기나요?",
            "계층 분리가 테스트에 주는 장점은 무엇인가요?",
            "Service와 Repository 중 어디에 비즈니스 규칙을 두는 것이 좋나요?",
        ),
        answer=(
            "Controller, Service, Repository를 나누는 이유는 각 코드의 변경 이유와 테스트 범위를 분리하기 위해서입니다. "
            "Controller는 HTTP 요청/응답과 입력 검증, Service는 비즈니스 유스케이스와 트랜잭션 경계, Repository는 데이터 접근을 담당합니다. "
            "예를 들어 API 응답 형식이 바뀌면 Controller와 DTO 위주로 수정하고, 주문 생성 규칙이 바뀌면 Service를 수정하며, 쿼리 최적화가 필요하면 Repository를 수정하는 식으로 변경 범위를 줄일 수 있습니다. "
            "Service에 트랜잭션을 두는 이유는 하나의 유스케이스 안에서 여러 데이터 변경이 함께 성공하거나 함께 실패해야 하기 때문입니다. "
            "Controller에 비즈니스 로직이 쌓이면 HTTP 계층과 핵심 로직이 강하게 결합되어 재사용과 테스트가 어려워지므로, Controller는 얇게 유지하고 Service에서 정책을 표현하는 것이 좋습니다."
        ),
        code_examples=(
            """### 계층별 책임 예시

```java
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
        return ownerService.createOwner(request);
    }
}

@Service
class OwnerService {

    private final OwnerRepository ownerRepository;

    OwnerService(OwnerRepository ownerRepository) {
        this.ownerRepository = ownerRepository;
    }

    @Transactional
    OwnerResponse createOwner(CreateOwnerRequest request) {
        if (ownerRepository.existsByPhone(request.phone())) {
            throw new DuplicateOwnerPhoneException(request.phone());
        }

        Owner owner = new Owner(request.name(), request.phone());
        Owner savedOwner = ownerRepository.save(owner);
        return OwnerResponse.from(savedOwner);
    }
}

interface OwnerRepository extends JpaRepository<Owner, Long> {
    boolean existsByPhone(String phone);
}
```
""",
            """### 테스트 관점 예시

```java
@ExtendWith(MockitoExtension.class)
class OwnerServiceTest {

    @Mock
    OwnerRepository ownerRepository;

    @InjectMocks
    OwnerService ownerService;

    @Test
    void duplicatedPhoneCannotBeRegistered() {
        CreateOwnerRequest request = new CreateOwnerRequest("Kim", "010-1111-2222");
        given(ownerRepository.existsByPhone(request.phone())).willReturn(true);

        assertThatThrownBy(() -> ownerService.createOwner(request))
                .isInstanceOf(DuplicateOwnerPhoneException.class);
    }
}
```
""",
        ),
        petclinic_hint="PetClinic의 owner, vet, visit 관련 패키지를 보면 웹 계층과 데이터 접근 계층이 어떻게 나뉘는지 확인할 수 있습니다.",
    ),
    SpringTopic(
        key="spring-ioc-di",
        title="IoC와 DI, 생성자 주입",
        summary=(
            "IoC는 객체 생성과 의존성 연결의 제어권을 프레임워크가 가져가는 구조입니다.",
            "DI는 필요한 의존 객체를 외부에서 주입받는 방식이며, Spring에서는 Bean을 통해 이를 관리합니다.",
            "실무에서는 필수 의존성을 명확히 드러내고 테스트하기 쉬운 생성자 주입을 기본으로 봅니다.",
        ),
        details=(
            "객체가 직접 `new`로 의존 객체를 만들면 구현체 교체와 테스트가 어려워집니다.",
            "Spring 컨테이너는 Bean을 생성하고, 생성자나 설정 정보를 통해 필요한 의존성을 연결합니다.",
            "생성자 주입은 필수 의존성을 `final`로 둘 수 있고, 순환 참조를 비교적 빨리 발견하게 해줍니다.",
        ),
        implementation=(
            "필수 의존성은 생성자 주입을 사용합니다.",
            "인터페이스와 구현체를 분리할 때는 변경 가능성이 실제로 있는지 확인합니다.",
            "테스트에서는 Mock 객체를 생성자에 직접 넣어 Service 로직을 검증할 수 있게 합니다.",
            "필드 주입은 테스트와 불변성 측면에서 되도록 피합니다.",
        ),
        questions=(
            "IoC와 DI의 차이를 설명해주세요.",
            "Spring에서 생성자 주입을 권장하는 이유는 무엇인가요?",
            "필드 주입의 단점은 무엇인가요?",
            "Bean으로 등록된 객체와 일반 객체는 무엇이 다른가요?",
        ),
        answer=(
            "IoC는 객체 생성과 흐름 제어를 개발자가 직접 하지 않고 Spring 컨테이너가 관리하는 구조이고, DI는 그 과정에서 필요한 의존 객체를 외부에서 주입받는 방식입니다. "
            "생성자 주입을 사용하면 필수 의존성이 명확하게 드러나고 `final`로 불변성을 지킬 수 있으며, 테스트할 때도 Spring 컨테이너 없이 필요한 의존성을 직접 넣어 검증할 수 있습니다."
        ),
    ),
    SpringTopic(
        key="spring-mvc-dispatcher-servlet",
        title="Spring MVC와 DispatcherServlet",
        summary=(
            "DispatcherServlet은 Spring MVC의 프론트 컨트롤러로 모든 웹 요청을 받아 적절한 핸들러로 위임합니다.",
            "요청은 HandlerMapping, HandlerAdapter, Controller, ViewResolver 또는 MessageConverter 흐름을 거칩니다.",
            "REST API에서는 보통 ViewResolver보다 `HttpMessageConverter`를 통해 JSON 응답을 만듭니다.",
        ),
        details=(
            "프론트 컨트롤러 패턴은 공통 웹 처리 진입점을 하나로 모아 인증, 로깅, 라우팅, 예외 처리 구성을 단순화합니다.",
            "`@Controller`나 `@RestController`의 메서드는 HandlerMapping에 의해 매핑되고 HandlerAdapter를 통해 호출됩니다.",
            "`@ResponseBody` 또는 `@RestController`를 사용하면 반환 객체가 JSON 같은 HTTP body로 변환됩니다.",
        ),
        implementation=(
            "화면 반환 Controller와 REST Controller의 차이를 구분합니다.",
            "공통 예외 처리는 `@ControllerAdvice` 또는 `@RestControllerAdvice`로 분리합니다.",
            "공통 인증/로깅은 Filter 또는 Interceptor 위치를 검토합니다.",
            "요청/응답 로깅을 넣을 때 민감 정보가 남지 않게 주의합니다.",
        ),
        questions=(
            "DispatcherServlet의 역할은 무엇인가요?",
            "Filter와 Interceptor는 어떤 차이가 있나요?",
            "`@Controller`와 `@RestController`의 차이는 무엇인가요?",
            "Spring MVC에서 JSON 응답은 어떻게 만들어지나요?",
        ),
        answer=(
            "DispatcherServlet은 Spring MVC의 프론트 컨트롤러로, 들어온 요청을 받아 어떤 Controller 메서드가 처리할지 찾고 호출하는 중심 역할을 합니다. "
            "REST API에서는 Controller가 반환한 객체를 `HttpMessageConverter`가 JSON으로 변환해 응답합니다. "
            "Filter는 Servlet 영역에서 동작하고 Interceptor는 Spring MVC 핸들러 호출 전후에 동작하므로, 인증이나 로깅 같은 공통 처리를 넣을 때 위치를 구분해야 합니다."
        ),
        petclinic_hint="PetClinic은 Spring Boot 기반 MVC 샘플이라 Controller 요청 흐름과 화면 렌더링 구조를 확인하는 참고 자료로 좋습니다.",
    ),
    SpringTopic(
        key="spring-validation-exception",
        title="요청 검증과 예외 응답 설계",
        summary=(
            "백엔드 API는 정상 흐름보다 실패 흐름을 일관되게 설계하는 것이 더 중요할 때가 많습니다.",
            "Spring에서는 Bean Validation과 `@Valid`, `@RestControllerAdvice`를 조합해 검증과 예외 응답을 구성합니다.",
            "검증 실패, 권한 실패, 리소스 없음, 비즈니스 규칙 위반을 구분해야 클라이언트와 운영자가 문제를 빠르게 이해할 수 있습니다.",
        ),
        details=(
            "DTO 필드에는 `@NotBlank`, `@NotNull`, `@Size`, `@Email` 같은 제약 조건을 둘 수 있습니다.",
            "검증 실패는 보통 400 Bad Request로 처리하고, 없는 리소스는 404, 권한 문제는 401 또는 403으로 구분합니다.",
            "비즈니스 예외는 도메인 의미가 드러나는 커스텀 예외와 에러 코드를 두면 관리하기 쉽습니다.",
        ),
        implementation=(
            "요청 DTO와 응답 DTO를 분리합니다.",
            "Controller 파라미터에 `@Valid`를 붙여 입력을 검증합니다.",
            "`@RestControllerAdvice`에서 예외 타입별 응답을 통일합니다.",
            "에러 응답에는 내부 스택트레이스나 민감 정보를 담지 않습니다.",
        ),
        questions=(
            "Spring에서 요청 DTO 검증은 어떻게 하나요?",
            "`@ControllerAdvice`와 `@RestControllerAdvice`는 어떤 역할을 하나요?",
            "400, 401, 403, 404 상태 코드는 어떻게 구분하나요?",
            "비즈니스 예외를 설계할 때 무엇을 고려해야 하나요?",
        ),
        answer=(
            "Spring에서는 요청 DTO에 Bean Validation 애노테이션을 붙이고 Controller에서 `@Valid`로 검증을 수행합니다. "
            "검증 실패나 비즈니스 예외는 `@RestControllerAdvice`에서 공통 에러 응답으로 변환해 API 응답 형식을 일관되게 유지합니다. "
            "상태 코드는 원인을 기준으로 구분해야 하며, 클라이언트 입력 오류는 400, 인증 실패는 401, 권한 부족은 403, 리소스 없음은 404로 표현하는 식으로 설계합니다."
        ),
    ),
    SpringTopic(
        key="spring-transaction",
        title="Spring 트랜잭션과 @Transactional",
        summary=(
            "`@Transactional`은 하나의 유스케이스를 원자적으로 처리하기 위한 Spring의 트랜잭션 선언 방식입니다.",
            "일반적으로 Service 계층에 트랜잭션 경계를 두고, Repository 호출들을 하나의 작업 단위로 묶습니다.",
            "읽기 전용, 롤백 규칙, 프록시 기반 동작, 영속성 컨텍스트와의 관계까지 함께 이해해야 합니다.",
        ),
        details=(
            "Spring의 선언적 트랜잭션은 기본적으로 프록시를 통해 동작하므로 같은 클래스 내부 메서드 호출에는 적용되지 않을 수 있습니다.",
            "기본 롤백 대상은 unchecked exception 계열이며, checked exception 롤백은 별도 설정이 필요합니다.",
            "JPA에서는 트랜잭션 안에서 영속성 컨텍스트가 변경 감지, 지연 로딩, 쓰기 지연과 함께 동작합니다.",
        ),
        implementation=(
            "변경 작업 유스케이스는 Service 메서드에 `@Transactional`을 둡니다.",
            "조회 전용 유스케이스는 `@Transactional(readOnly = true)`를 검토합니다.",
            "트랜잭션 안에서 외부 API 호출을 오래 잡고 있지 않도록 주의합니다.",
            "내부 호출, private 메서드, self-invocation 상황에서 트랜잭션 적용 여부를 확인합니다.",
        ),
        questions=(
            "`@Transactional`은 어느 계층에 두는 것이 일반적인가요?",
            "Spring 트랜잭션의 기본 롤백 조건은 무엇인가요?",
            "프록시 기반 트랜잭션에서 self-invocation 문제가 무엇인가요?",
            "`readOnly = true`는 언제 사용하나요?",
        ),
        answer=(
            "`@Transactional`은 보통 하나의 비즈니스 유스케이스를 담당하는 Service 계층에 둡니다. "
            "여러 Repository 작업을 하나의 원자적 작업으로 묶고, 중간에 예외가 발생하면 일관성이 깨지지 않도록 롤백하기 위해서입니다. "
            "Spring의 트랜잭션은 프록시 기반으로 동작하므로 같은 클래스 내부 호출에는 적용되지 않을 수 있고, 기본적으로 unchecked exception이 롤백 대상이라는 점을 주의해야 합니다."
        ),
    ),
    SpringTopic(
        key="spring-jpa-basic",
        title="Spring Data JPA와 Repository",
        summary=(
            "Spring Data JPA는 반복적인 Repository 구현을 줄이고 JPA 기반 데이터 접근을 쉽게 구성하게 해줍니다.",
            "하지만 메서드 이름 쿼리, JPQL, Querydsl, EntityGraph 등 조회 방법의 장단점을 구분해야 합니다.",
            "Repository는 데이터 접근 계층이지 모든 비즈니스 규칙을 넣는 장소가 아닙니다.",
        ),
        details=(
            "`JpaRepository`를 상속하면 기본 CRUD, 페이징, 정렬 기능을 사용할 수 있습니다.",
            "간단한 조회는 메서드 이름 쿼리로 충분하지만 복잡한 동적 조건은 Querydsl 같은 도구가 더 적합할 수 있습니다.",
            "Entity 설계에서는 연관관계 방향, cascade, orphanRemoval, fetch 전략을 신중히 정해야 합니다.",
        ),
        implementation=(
            "Entity와 API DTO를 분리합니다.",
            "목록 조회는 `Pageable`과 정렬 조건을 고려합니다.",
            "복잡한 조회는 서비스 로직으로 억지 조합하지 말고 쿼리 계층에서 명확히 표현합니다.",
            "테스트는 `@DataJpaTest`로 Repository 쿼리와 매핑을 검증합니다.",
        ),
        questions=(
            "Spring Data JPA를 사용하는 이유는 무엇인가요?",
            "Entity와 DTO를 분리하는 이유는 무엇인가요?",
            "JPA Repository에 비즈니스 로직을 넣으면 어떤 문제가 생기나요?",
            "`Pageable`은 어떤 상황에서 사용하나요?",
        ),
        answer=(
            "Spring Data JPA는 기본 CRUD와 페이징, 정렬 같은 반복적인 데이터 접근 코드를 줄여줍니다. "
            "다만 Repository는 데이터 접근 책임에 집중해야 하고, 비즈니스 규칙은 Service 계층에 두는 것이 좋습니다. "
            "Entity를 API 응답으로 직접 노출하면 내부 영속성 모델이 외부 계약이 되므로 DTO를 분리하고, 조회 성능이 필요한 경우 fetch 전략과 쿼리 방식을 함께 검토해야 합니다."
        ),
        petclinic_hint="PetClinic은 H2 기본 설정과 MySQL/PostgreSQL 프로필을 제공해 Spring Data와 DB 설정 흐름을 보기 좋습니다.",
    ),
    SpringTopic(
        key="spring-security-jwt",
        title="JWT 인증 구현 기본",
        summary=(
            "JWT 인증은 로그인 성공 후 서버가 서명된 토큰을 발급하고, 이후 요청에서 토큰을 검증해 사용자를 식별하는 방식입니다.",
            "Spring Security에서는 보통 인증 Filter에서 Authorization 헤더의 Bearer 토큰을 읽고 SecurityContext에 인증 객체를 저장합니다.",
            "JWT는 stateless 인증에 유리하지만 토큰 탈취, 만료, 재발급, 로그아웃 처리를 반드시 설계해야 합니다.",
        ),
        details=(
            "JWT는 header, payload, signature로 구성되며 payload는 암호화가 아니라 인코딩이므로 민감 정보를 넣으면 안 됩니다.",
            "Access Token은 짧게, Refresh Token은 더 길게 두되 저장소와 회전 전략을 함께 설계하는 것이 일반적입니다.",
            "서버는 매 요청마다 서명, 만료 시간, issuer, subject, 권한 클레임 등을 검증해야 합니다.",
        ),
        implementation=(
            "로그인 API에서 사용자 인증 후 Access Token과 Refresh Token을 발급합니다.",
            "Spring Security Filter에서 `Authorization: Bearer ...` 헤더를 파싱합니다.",
            "토큰 검증 성공 시 `Authentication`을 만들어 `SecurityContextHolder`에 저장합니다.",
            "토큰 만료, 위조, 권한 부족은 각각 일관된 에러 응답으로 처리합니다.",
            "Refresh Token은 DB나 Redis에 저장하고 재발급/폐기 정책을 둡니다.",
        ),
        questions=(
            "JWT 인증 흐름을 설명해주세요.",
            "JWT payload에 민감 정보를 넣으면 안 되는 이유는 무엇인가요?",
            "Access Token과 Refresh Token을 나누는 이유는 무엇인가요?",
            "Spring Security에서 JWT 검증 Filter는 어떤 역할을 하나요?",
        ),
        answer=(
            "JWT 인증은 로그인 성공 시 서버가 서명된 토큰을 발급하고, 클라이언트가 이후 요청마다 Bearer 토큰을 보내면 서버가 이를 검증해 사용자를 식별하는 방식입니다. "
            "Spring Security에서는 커스텀 Filter가 Authorization 헤더에서 토큰을 읽고 서명과 만료 시간을 검증한 뒤, 인증 정보를 `SecurityContext`에 저장합니다. "
            "JWT payload는 누구나 디코딩할 수 있으므로 민감 정보를 넣으면 안 되고, 토큰 탈취에 대비해 짧은 Access Token과 Refresh Token 재발급/폐기 전략을 함께 설계해야 합니다."
        ),
    ),
)


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp949"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def clean_heading(line: str) -> str:
    line = re.sub(r"^\s{0,3}#{1,6}\s+", "", line.strip())
    line = re.sub(r"^\s*[-*+]\s+", "", line)
    line = re.sub(r"^\s*\d+[.)]\s+", "", line)
    return line.strip()


def is_noise_title(title: str) -> bool:
    normalized = title.strip().lower()
    return (
        normalized in NOISE_TITLES
        or normalized.endswith("expected question")
        or normalized.endswith("개념도")
        or normalized.endswith("예시")
    )


def normalize_category(value: str | None) -> str | None:
    if not value:
        return None
    normalized = value.strip().lower().replace("_", "-")
    for category, aliases in CATEGORY_ALIASES.items():
        if normalized == category or normalized in aliases:
            return category
    return normalized


def infer_category(path: Path) -> str:
    parts = [part.lower() for part in path.relative_to(ROOT).parts]
    text = " ".join(parts)
    for category, aliases in CATEGORY_ALIASES.items():
        if category in text or any(alias.lower() in text for alias in aliases):
            return category
    return "general"


def source_identity(path: Path) -> str:
    try:
        relative = path.relative_to(REFERENCE_SOURCES_DIR)
    except ValueError:
        return path.as_posix()
    return (ROOT / "reference_repos" / relative).as_posix()


def load_reference_repos() -> dict[str, dict[str, str]]:
    if not REFERENCE_REPOS_FILE.exists():
        return {}
    data = json.loads(REFERENCE_REPOS_FILE.read_text(encoding="utf-8"))
    return {repo["name"]: repo for repo in data}


def build_github_url(path: Path, repos: dict[str, dict[str, str]]) -> str | None:
    try:
        relative = path.relative_to(REFERENCE_SOURCES_DIR)
    except ValueError:
        return None
    if not relative.parts:
        return None
    repo_name = relative.parts[0]
    repo = repos.get(repo_name)
    if not repo:
        return None
    branch = repo.get("branch", "main")
    inner_path = "/".join(relative.parts[1:])
    return f"{repo['homepage']}/blob/{branch}/{inner_path}"


def meaningful_body_text(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<img\s+[^>]*?>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_markdown_sections(path: Path, text: str) -> list[StudyItem]:
    items: list[StudyItem] = []
    matches = list(re.finditer(r"(?m)^\s{0,3}#{1,3}\s+(.+?)\s*$", text))
    if not matches:
        return items

    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        title = clean_heading(match.group(1))
        body = text[start:end].strip()
        if title and body and not is_noise_title(title) and len(meaningful_body_text(body)) >= 40:
            items.append(StudyItem(title=title, body=body, source=path, category=infer_category(path)))
    return items


def parse_question_lines(path: Path, text: str) -> list[StudyItem]:
    items: list[StudyItem] = []
    for line in text.splitlines():
        title = clean_heading(line)
        if not title or len(title) < 5:
            continue
        if is_noise_title(title):
            continue
        if title.endswith("?") or title.endswith("요") or "차이" in title or "설명" in title:
            items.append(StudyItem(title=title, body="", source=path, category=infer_category(path)))
    return items


def collect_items(category: str | None = None) -> list[StudyItem]:
    items: list[StudyItem] = []
    reference_repos = load_reference_repos()
    search_roots = [MY_MATERIALS_DIR]
    if CURATED_REFERENCES_DIR.exists():
        search_roots.append(CURATED_REFERENCES_DIR)
    if REFERENCE_SOURCES_DIR.exists():
        search_roots.append(REFERENCE_SOURCES_DIR)

    for root in search_roots:
        for path in sorted(root.rglob("*")):
            if any(part in IGNORED_DIRS for part in path.parts):
                continue
            if path.name.lower() in IGNORED_FILES:
                continue
            if path.suffix.lower() not in {".md", ".txt"} or not path.is_file():
                continue
            text = read_text(path)
            if path.name.lower() == "readme.md":
                if "ksundong-backend-interview" not in path.parts:
                    continue
                parsed = parse_question_lines(path, text)
            else:
                parsed = parse_markdown_sections(path, text)
                parsed.extend(parse_question_lines(path, text))
            for item in parsed:
                items.append(
                    StudyItem(
                        title=item.title,
                        body=item.body,
                        source=item.source,
                        category=item.category,
                        github_url=build_github_url(item.source, reference_repos),
                    )
                )

    deduped: dict[str, StudyItem] = {}
    for item in items:
        if category and item.category != category:
            continue
        deduped[item.key] = item
    return list(deduped.values())


def load_used() -> list[str]:
    if not STUDIED_ITEMS_FILE.exists():
        return []
    try:
        data = json.loads(STUDIED_ITEMS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_used(keys: list[str]) -> None:
    STUDY_STATE_DIR.mkdir(parents=True, exist_ok=True)
    STUDIED_ITEMS_FILE.write_text(json.dumps(keys, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_spring_used() -> list[str]:
    if not SPRING_STUDIED_ITEMS_FILE.exists():
        return []
    try:
        data = json.loads(SPRING_STUDIED_ITEMS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_spring_used(keys: list[str]) -> None:
    STUDY_STATE_DIR.mkdir(parents=True, exist_ok=True)
    SPRING_STUDIED_ITEMS_FILE.write_text(json.dumps(keys, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_study_log() -> list[dict[str, str]]:
    if not STUDY_LOG_FILE.exists():
        return []
    try:
        data = json.loads(STUDY_LOG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_study_log(entries: list[dict[str, str]]) -> None:
    STUDY_STATE_DIR.mkdir(parents=True, exist_ok=True)
    STUDY_LOG_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def recent_study_sources(limit: int = 7) -> set[str]:
    entries = load_study_log()
    return {
        source_identity((ROOT / source).resolve())
        for source in (entry.get("source", "") for entry in entries[-limit:])
        if source
    }


def choose_item(items: list[StudyItem], used: list[str]) -> StudyItem:
    unused = [item for item in items if item.key not in used]
    recent_sources = recent_study_sources()
    fresh_source_items = [
        item
        for item in unused
        if source_identity(item.source) not in recent_sources
    ]
    if fresh_source_items:
        return fresh_source_items[0]
    if unused:
        return unused[0]
    return items[0]


def choose_item_for_date(items: list[StudyItem], used: list[str], target_date: date, force: bool) -> StudyItem:
    if force:
        for entry in load_study_log():
            if entry.get("date") != target_date.isoformat():
                continue
            for item in items:
                if item.key == entry.get("key"):
                    return item
    return choose_item(items, used)


def choose_spring_topic(used: list[str]) -> SpringTopic:
    for topic in SPRING_CURRICULUM:
        if topic.key not in used:
            return topic
    return SPRING_CURRICULUM[0]


def choose_spring_topic_for_date(used: list[str], target_date: date, force: bool) -> SpringTopic:
    if force:
        for entry in load_study_log():
            if entry.get("date") != target_date.isoformat():
                continue
            spring_key = entry.get("spring_key")
            for topic in SPRING_CURRICULUM:
                if topic.key == spring_key:
                    return topic
    return choose_spring_topic(used)


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[[^\]]+\]\([^)]+\)", " ", text)
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[`*_>#|]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list[str]:
    clean = strip_markdown(text)
    if not clean:
        return []
    chunks = re.split(r"[.!?。]\s+|다\.\s+|요\.\s+", clean)
    return [sentence.strip() for sentence in chunks if len(sentence.strip()) >= 12]


def normalize_keyword(word: str) -> str:
    normalized = word.strip("-").lower()
    for particle in ("으로부터", "으로서", "으로써", "에서", "에게", "부터", "까지", "으로", "라고", "이며", "이고", "와", "과", "은", "는", "이", "가", "을", "를", "의", "에", "로", "도", "만"):
        if normalized.endswith(particle) and len(normalized) > len(particle) + 1:
            normalized = normalized[: -len(particle)]
            break
    return normalized


def extract_keywords(title: str, body: str, limit: int = 8) -> list[str]:
    text = strip_markdown(f"{title} {body}").lower()
    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+.#-]{2,}|[가-힣]{2,}", text)
    counts: dict[str, int] = {}
    for word in words:
        normalized = normalize_keyword(word)
        if normalized in STOPWORDS or len(normalized) < 2:
            continue
        counts[normalized] = counts.get(normalized, 0) + 1
    return [word for word, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def looks_like_question_list(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    question_lines = [line for line in lines if "?" in line or "설명" in line or line.endswith("요.") or line.endswith("세요.")]
    return len(question_lines) >= max(2, len(lines) // 2)


def build_answer_draft(item: StudyItem) -> str:
    sentences = split_sentences(item.body)
    if sentences and not looks_like_question_list(item.body):
        first = sentences[0]
        support = sentences[1:3]
        lines = [f"{item.title}에 대한 핵심은 {first}"]
        if support:
            lines.append("근거로는 " + " ".join(support))
        lines.append("면접에서는 먼저 한 문장으로 정의하고, 왜 필요한지와 어떤 트레이드오프가 있는지를 예시와 함께 설명하면 좋습니다.")
        return "\n\n".join(lines)

    keywords = extract_keywords(item.title, item.body, limit=5)
    keyword_text = ", ".join(keywords) if keywords else "정의, 동작 방식, 장단점, 실무 예시"
    return (
        f"{item.title}: `{item.category}` 영역에서 자주 확인하는 면접 주제입니다. "
        f"답변은 먼저 이 개념의 정의를 한 문장으로 말하고, 이어서 {keyword_text}를 중심으로 설명하면 좋습니다.\n\n"
        "그 다음 비슷한 개념과의 차이, 실제 요청이나 장애 상황에서 어떤 영향을 주는지, 사용 시 주의할 트레이드오프를 덧붙이면 면접 답변으로 더 자연스럽습니다."
    )


def build_keyword_section(item: StudyItem) -> str:
    keywords = extract_keywords(item.title, item.body)
    if not keywords:
        return "- 정의\n- 동작 방식\n- 장점\n- 단점\n- 실무 예시"
    return "\n".join(f"- {keyword}" for keyword in keywords)




def body_without_code(text: str) -> str:
    return re.sub(r"```.*?```", " ", text, flags=re.DOTALL)


def first_sentences(text: str, limit: int = 3) -> list[str]:
    sentences = split_sentences(body_without_code(text))
    return sentences[:limit]


def markdown_table_summary(text: str) -> list[str]:
    rows = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    summaries: list[str] = []
    for row in rows:
        if re.fullmatch(r"[|:\- ]+", row):
            continue
        cells = [re.sub(r"[*`_]", "", cell.strip()) for cell in row.strip("|").split("|")]
        if len(cells) >= 2 and cells[0] not in {"특성", "기능", "적용기술"}:
            summaries.append(f"{cells[0]}: {cells[1]}")
    return summaries[:4]



def definition_terms(text: str, limit: int = 5) -> list[str]:
    terms: list[str] = []
    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned.startswith("-"):
            continue
        cleaned = re.sub(r"^[-*+]\s+", "", cleaned)
        term = re.split(r"\s*[:：]\s*", cleaned, maxsplit=1)[0]
        term = re.sub(r"[`*_]", "", term).strip()
        if 1 < len(term) <= 40:
            terms.append(term)
    deduped: list[str] = []
    for term in terms:
        if term not in deduped:
            deduped.append(term)
    return deduped[:limit]


def build_summary_section(item: StudyItem) -> str:
    lowered = f"{item.title} {strip_markdown(item.body)}".lower()
    if is_hash_topic(item):
        return "\n".join(
            [
                "- 해시는 임의 길이의 입력을 고정 길이의 해시값으로 매핑하는 방식입니다.",
                "- 해시 테이블은 해시 함수를 이용해 key가 저장될 버킷 위치를 계산하므로 평균적으로 검색, 삽입, 삭제가 `O(1)`에 가깝습니다.",
                "- 서로 다른 key가 같은 버킷에 매핑되는 해시 충돌은 피할 수 없으므로, 체이닝이나 개방 주소법 같은 충돌 해결 전략이 필요합니다.",
                "- 데이터가 많아져 Load Factor가 높아지면 충돌 가능성이 커지므로, 해시 테이블은 보통 재해싱을 통해 버킷 크기를 늘립니다.",
            ]
        )
    if "greedy" in lowered or "그리디" in lowered or "탐욕" in lowered:
        return "\n".join(
            [
                "- 그리디 알고리즘은 매 단계에서 현재 가장 좋아 보이는 선택을 하며 해답을 만들어가는 알고리즘 기법입니다.",
                "- 빠르고 구현이 단순한 경우가 많지만, 항상 최적해를 보장하지는 않습니다.",
                "- 탐욕 선택 속성과 최적 부분 구조가 성립하는지 확인해야 그리디 풀이를 정당화할 수 있습니다.",
            ]
        )

    table = markdown_table_summary(item.body)
    if table:
        return "\n".join(f"- {line}" for line in table)

    terms = definition_terms(item.body)
    if terms:
        return "\n".join(
            [
                f"- {item.title}는 {', '.join(terms[:3])} 같은 구성 요소를 구분해서 이해하는 주제입니다.",
                "- 각 요소가 어떤 입력과 출력을 가지는지, 그리고 실제 시스템에서 어떤 역할을 하는지 연결해서 보면 좋습니다.",
                "- 면접에서는 용어 정의만 외우기보다 서로의 관계와 차이를 함께 설명하는 것이 중요합니다.",
            ]
        )

    sentences = first_sentences(item.body, limit=3)
    if sentences:
        compact: list[str] = []
        for sentence in sentences:
            if len(sentence) > 140:
                sentence = sentence[:137].rstrip() + "..."
            compact.append(sentence)
        return "\n".join(f"- {sentence}" for sentence in compact)

    keywords = extract_keywords(item.title, item.body, limit=5)
    if keywords:
        return "\n".join(
            [
                f"- {item.title}는 {', '.join(keywords[:3])}를 중심으로 이해하면 좋습니다.",
                "- 정의, 동작 방식, 장단점, 실무 주의점을 함께 정리합니다.",
            ]
        )
    return f"- {item.title}의 정의와 쓰임을 중심으로 이해합니다."


def build_interview_points(item: StudyItem) -> str:
    lowered = f"{item.title} {strip_markdown(item.body)}".lower()
    if is_hash_topic(item):
        rows = [
            ("정의", "임의 길이 입력을 고정 길이 해시값으로 매핑"),
            ("동작 원리", "key, hashCode, 버킷, 인덱스 계산"),
            ("장점", "평균 `O(1)` 조회, 빠른 중복 확인, key 기반 접근"),
            ("단점", "해시 충돌, 순서 미보장, 최악 성능 저하"),
            ("충돌 해결", "체이닝, 개방 주소법, 선형 탐사, 이중 해싱"),
            ("확장 과정", "Load Factor, threshold, resize, rehashing"),
            ("실무 활용", "`HashMap`, `HashSet`, 캐시, 중복 제거, 보안 해시"),
        ]
        return markdown_table(("질문 포인트", "핵심 키워드"), rows)
    if "greedy" in lowered or "그리디" in lowered or "탐욕" in lowered:
        rows = [
            ("정의", "매 순간의 최선 선택으로 전체 해답을 구성하는 방식"),
            ("동작 원리", "현재 선택 기준, 적절성 검사, 해답 검사"),
            ("장점", "조건이 맞으면 빠르고 구현이 단순함"),
            ("단점", "탐욕 선택이 전체 최적해를 보장하지 않을 수 있음"),
            ("비교 개념", "완전탐색, 동적 계획법, 반례 검증"),
        ]
        return markdown_table(("질문 포인트", "핵심 키워드"), rows)

    keywords = extract_keywords(item.title, item.body, limit=5)
    if not keywords:
        keywords = ["정의", "동작 방식", "장단점", "실무 적용", "주의점"]
    rows = [
        ("정의", f"{item.title}를 한 문장으로 설명"),
        ("동작 원리", ", ".join(keywords[:4])),
        ("장점", "무엇을 더 빠르게, 단순하게, 안정적으로 만드는지 설명"),
        ("단점", "성능, 복잡도, 운영 부담, 예외 상황 설명"),
        ("비교 개념", "비슷한 개념과 책임, 사용 시점, 비용 비교"),
        ("실무 활용", "Java/Spring 백엔드에서의 사용 사례와 주의점 연결"),
    ]
    return markdown_table(("질문 포인트", "핵심 키워드"), rows)


def is_likely_interview_question(text: str) -> bool:
    if len(text) < 8 or len(text) > 120:
        return False
    if re.search(r"[🙎🙋💁🤷🤦🙍🙆💰]", text):
        return False
    if ":" in text and not re.search(r"(차이|설명|무엇|왜|어떻게|이유|장단점|특징)", text):
        return False
    return bool(re.search(r"(\?|설명|차이|무엇|왜|어떻게|이유|장단점)", text))


def build_related_questions(item: StudyItem) -> str:
    if is_hash_topic(item):
        rows = [
            ("해시를 한 문장으로 설명해주세요.", "입력 데이터를 해시 함수로 고정 길이 값에 매핑하는 방식"),
            ("해시 테이블의 조회가 빠른 이유는 무엇인가요?", "key를 비교 탐색하지 않고 버킷 위치를 바로 계산하기 때문"),
            ("해시 충돌은 왜 발생하나요?", "입력 공간은 크고 버킷 수는 제한되어 있기 때문"),
            ("체이닝과 개방 주소법의 차이는 무엇인가요?", "같은 버킷에 모아두는 방식과 다른 빈 버킷을 찾는 방식의 차이"),
            ("Load Factor와 재해싱은 무엇인가요?", "테이블이 얼마나 찼는지 나타내는 비율과 버킷을 늘려 다시 배치하는 과정"),
            ("Java `HashMap`은 충돌을 어떻게 처리하나요?", "체이닝 기반으로 처리하고, 충돌이 심한 버킷은 트리화할 수 있음"),
        ]
        return markdown_table(("질문", "핵심 답변 방향"), rows)

    explicit: list[str] = []
    text = body_without_code(item.body)
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            continue
        cleaned = clean_heading(line)
        cleaned = re.sub(r"[*`_]", "", cleaned).strip().rstrip(".")
        if is_likely_interview_question(cleaned):
            explicit.append(cleaned)
    questions = explicit[:6]
    questions.extend(
        [
            f"{item.title}를 한 문장으로 설명해주세요.",
            f"{item.title}가 필요한 이유는 무엇인가요?",
            f"{item.title}의 장점과 단점은 무엇인가요?",
            f"{item.title}와 비슷한 개념을 비교해서 설명해주세요.",
            f"실무에서 {item.title}를 사용할 때 주의할 점은 무엇인가요?",
        ]
    )
    deduped: list[str] = []
    for question in questions:
        if question not in deduped:
            deduped.append(question)
    rows = [(question, infer_question_direction(question)) for question in deduped[:6]]
    return markdown_table(("질문", "핵심 답변 방향"), rows)


def concept_name(title: str) -> str:
    name = re.sub(r"^\s*\[|\]\s*$", "", title).strip()
    return name


def is_hash_topic(item: StudyItem) -> bool:
    text = f"{item.title} {strip_markdown(item.body)}".lower()
    return "hash" in text or "해시" in text


def display_title(item: StudyItem) -> str:
    if is_hash_topic(item) and re.search(r"hash\s*란|해시", item.title, flags=re.IGNORECASE):
        return "해시(Hash)"
    return item.title


def build_interview_answer_examples(item: StudyItem) -> str:
    title = concept_name(item.title)
    lowered = f"{title} {strip_markdown(item.body)}".lower()

    if is_hash_topic(item):
        return """### Q. 해시를 한 문장으로 설명해주세요.

해시는 임의 길이의 입력 데이터를 해시 함수를 통해 고정 길이의 해시값으로 매핑하는 방식입니다. 자료구조에서는 key를 버킷 위치로 바꿔 빠르게 데이터를 찾기 위해 사용하고, 보안에서는 원문을 직접 저장하지 않거나 무결성을 검증하기 위해 사용합니다.

### Q. 해시 테이블의 조회가 평균적으로 빠른 이유는 무엇인가요?

해시 테이블은 key를 처음부터 순차 비교하지 않고, 해시 함수를 통해 key가 저장될 버킷 위치를 계산합니다. 해시값이 고르게 분포하고 충돌이 적다면 원하는 위치에 거의 바로 접근할 수 있기 때문에 검색, 삽입, 삭제가 평균적으로 `O(1)`에 가깝게 동작합니다.

### Q. 해시 충돌은 왜 발생하고 어떻게 해결하나요?

해시 충돌은 서로 다른 key가 같은 해시값이나 같은 버킷 위치로 매핑될 때 발생합니다. 가능한 key의 수는 매우 크지만 실제 버킷 수는 제한되어 있기 때문에 충돌은 피할 수 없습니다. 대표적인 해결 방법은 같은 버킷에 여러 값을 연결하는 체이닝과, 충돌 시 다른 빈 버킷을 찾는 개방 주소법입니다.

### Q. Load Factor와 재해싱은 무엇인가요?

Load Factor는 해시 테이블의 버킷이 얼마나 채워졌는지를 나타내는 비율입니다. 데이터가 계속 추가되어 Load Factor가 높아지면 충돌 가능성이 커지고 성능이 떨어질 수 있습니다. 그래서 일정 기준을 넘으면 버킷 배열을 늘리고 기존 key들을 새 위치에 다시 배치하는데, 이를 재해싱이라고 합니다.

### Q. Java `HashMap`은 충돌을 어떻게 처리하나요?

Java `HashMap`은 기본적으로 같은 버킷에 들어온 엔트리를 연결해서 관리하는 체이닝 방식을 사용합니다. Java 8 이후에는 특정 조건에서 버킷 내부 구조를 연결 리스트에서 트리로 바꿔 최악의 탐색 성능을 완화합니다."""

    if "greedy" in lowered or "그리디" in lowered or "탐욕" in lowered:
        return f"""### {title}를 한 문장으로 설명해주세요.

{title}는 매 단계에서 현재 가장 좋아 보이는 선택을 하며 전체 해답을 만들어가는 알고리즘 기법입니다.

### {title}가 필요한 이유는 무엇인가요?

문제의 조건이 맞다면 모든 경우를 탐색하지 않고도 빠르게 해답을 구할 수 있기 때문입니다. 특히 정렬 후 일정한 기준으로 선택을 반복하는 문제에서 구현이 단순하고 시간 복잡도를 크게 줄일 수 있습니다.

### {title}의 장점과 단점은 무엇인가요?

장점은 구현이 비교적 간단하고, 조건이 맞으면 매우 효율적으로 최적해를 구할 수 있다는 점입니다.

단점은 현재의 최선 선택이 전체 최적해로 이어진다는 보장이 없으면 오답이 될 수 있다는 점입니다. 그래서 그리디를 사용할 때는 탐욕 선택 속성과 최적 부분 구조가 성립하는지, 반례가 없는지 확인해야 합니다.

### {title}와 완전탐색, 동적 계획법을 비교해서 설명해주세요.

완전탐색은 가능한 모든 후보를 확인하고, 동적 계획법은 중복 부분 문제의 결과를 저장해 탐색량을 줄입니다. 반면 그리디는 매 순간 하나의 선택 기준으로 후보를 줄이며 진행합니다. 그래서 그리디는 빠르지만, 선택 기준이 항상 최적해를 보장한다는 정당성 설명이 필요합니다.

### {title}를 사용할 때 주의할 점은 무엇인가요?

선택 기준을 먼저 정하고, 그 기준이 항상 전체 최적해로 이어지는지 검증해야 합니다. 예를 들어 일부 동전 체계에서는 큰 동전부터 고르는 방식이 맞지만, 모든 동전 체계에서 맞는 것은 아니므로 반례를 확인하는 습관이 중요합니다."""

    if "완전탐색" in title or "brute force" in lowered:
        return f"""### {title}를 한 문장으로 설명해주세요.

{title}는 가능한 모든 경우의 수를 빠짐없이 확인해서 조건에 맞는 정답을 찾는 탐색 방법입니다.

### {title}가 필요한 이유는 무엇인가요?

입력 크기가 작거나 경우의 수가 제한적인 문제에서는 복잡한 최적화 기법보다 완전탐색이 가장 단순하고 확실한 해결책이 될 수 있습니다. 또한 더 효율적인 알고리즘을 설계하기 전에 정답 검증용 기준 풀이로도 자주 사용됩니다.

### {title}의 장점과 단점은 무엇인가요?

장점은 구현이 비교적 직관적이고, 가능한 경우를 모두 확인하기 때문에 조건만 올바르면 정답을 놓치지 않는다는 점입니다.

단점은 경우의 수가 커질수록 시간 복잡도가 급격히 증가한다는 점입니다. 예를 들어 순열, 조합, 부분집합처럼 경우의 수가 지수적으로 늘어나는 문제에서는 입력 크기가 조금만 커져도 실행 시간이 현실적으로 감당되지 않을 수 있습니다.

### {title}와 비슷한 개념을 비교해서 설명해주세요.

완전탐색은 모든 후보를 검사하는 방식이고, 그리디나 동적 계획법은 문제의 특성을 이용해 검사해야 할 후보를 줄이는 방식입니다. 그리디는 매 순간 최선의 선택이 전체 최적해로 이어진다는 조건이 필요하고, 동적 계획법은 중복 부분 문제와 최적 부분 구조가 있을 때 효과적입니다.

### 실무에서 {title}를 사용할 때 주의할 점은 무엇인가요?

먼저 입력 크기와 가능한 경우의 수를 계산해서 제한 시간 안에 실행 가능한지 확인해야 합니다. 완전탐색이 너무 느리다면 가지치기, 정렬, 해시, 백트래킹, 동적 계획법 같은 방법으로 탐색 범위를 줄일 수 있는지 검토하는 것이 좋습니다."""

    sentences = first_sentences(item.body, limit=2)
    definition = sentences[0] if sentences else build_answer_draft(item).split("\n\n", maxsplit=1)[0]
    keywords = extract_keywords(item.title, item.body, limit=5)
    keyword_text = ", ".join(keywords) if keywords else "정의, 동작 방식, 장단점"

    return f"""### {title}를 한 문장으로 설명해주세요.

{definition}

### {title}가 필요한 이유는 무엇인가요?

{title}는 `{item.category}` 영역에서 문제를 정확히 이해하고 시스템의 동작 방식이나 트레이드오프를 설명하기 위해 필요한 개념입니다. 면접에서는 단순 정의보다 어떤 상황에서 이 개념이 등장하고, 어떤 문제를 해결하는지까지 연결해서 말하는 것이 좋습니다.

### {title}의 장점과 단점은 무엇인가요?

장점은 {keyword_text}를 기준으로 동작 원리와 사용 목적을 명확하게 설명할 수 있다는 점입니다.

단점이나 주의점은 실제 적용 시 성능, 복잡도, 안정성, 운영 부담 중 어떤 비용이 생기는지 함께 검토해야 한다는 점입니다. 원문에 나온 조건과 예외 상황을 함께 정리하면 답변이 더 탄탄해집니다.

### {title}와 비슷한 개념을 비교해서 설명해주세요.

먼저 {title}의 핵심 기준을 잡고, 비슷한 개념과 입력, 출력, 책임, 사용 시점이 어떻게 다른지 비교하면 됩니다. 차이를 설명할 때는 "무엇을 해결하려는가"와 "어떤 비용을 감수하는가"를 같이 말하면 면접 답변이 자연스럽습니다.

### 실무에서 {title}를 사용할 때 주의할 점은 무엇인가요?

실무에서는 이 개념이 적용되는 범위와 한계를 먼저 확인해야 합니다. 특히 데이터 크기, 장애 상황, 보안 요구사항, 성능 병목처럼 운영 환경에서 문제가 될 수 있는 조건을 함께 고려하는 것이 중요합니다."""


def bullet_lines(lines: tuple[str, ...]) -> str:
    return "\n".join(f"- {line}" for line in lines)


def table_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", "<br>")


def markdown_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(table_cell(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


SPRING_OPERATION_STEPS: dict[str, tuple[str, ...]] = {
    "spring-rest-api-basics": (
        "클라이언트가 HTTP 요청을 보냅니다.",
        "DispatcherServlet이 요청을 받고 HandlerMapping을 통해 Controller를 찾습니다.",
        "Controller는 요청 DTO를 바인딩하고 검증한 뒤 Service에 유스케이스 처리를 위임합니다.",
        "Service는 비즈니스 규칙을 처리하고 Repository나 외부 시스템과 협력합니다.",
        "응답 DTO와 HTTP 상태 코드가 클라이언트로 반환됩니다.",
    ),
    "spring-layered-architecture": (
        "Controller가 HTTP 요청과 응답 변환을 담당합니다.",
        "Service가 하나의 비즈니스 유스케이스와 트랜잭션 경계를 담당합니다.",
        "Repository가 데이터 접근 세부 사항을 캡슐화합니다.",
        "각 계층은 바로 아래 계층에만 의존하도록 구성해 변경 전파를 줄입니다.",
    ),
    "spring-ioc-di": (
        "Spring이 설정 정보와 컴포넌트 스캔 결과를 바탕으로 Bean 후보를 찾습니다.",
        "BeanDefinition을 만들고 어떤 클래스가 어떤 의존성을 필요로 하는지 파악합니다.",
        "Spring 컨테이너가 Bean 객체를 생성합니다.",
        "생성자, setter, 필드 등의 주입 지점을 통해 필요한 의존 Bean을 연결합니다.",
        "초기화 콜백을 수행한 뒤 애플리케이션에서 사용할 수 있는 Bean으로 관리합니다.",
    ),
    "spring-mvc-dispatcher-servlet": (
        "요청이 Servlet Container를 거쳐 DispatcherServlet에 도착합니다.",
        "HandlerMapping이 요청을 처리할 Controller 메서드를 찾습니다.",
        "HandlerAdapter가 Controller 메서드를 호출합니다.",
        "반환값은 ViewResolver 또는 HttpMessageConverter를 통해 응답으로 변환됩니다.",
        "예외가 발생하면 HandlerExceptionResolver나 ControllerAdvice가 응답을 구성합니다.",
    ),
    "spring-validation-exception": (
        "Controller가 요청 DTO를 바인딩합니다.",
        "`@Valid` 또는 `@Validated`가 Bean Validation 제약 조건을 검사합니다.",
        "검증 실패나 비즈니스 예외가 발생하면 예외가 상위로 전파됩니다.",
        "`@RestControllerAdvice`가 예외 타입별로 HTTP 상태 코드와 에러 응답을 만듭니다.",
    ),
    "spring-transaction": (
        "클라이언트 코드가 `@Transactional`이 붙은 Service 메서드를 호출합니다.",
        "Spring AOP 프록시가 호출을 가로채 트랜잭션을 시작합니다.",
        "Service 로직과 Repository 호출이 같은 트랜잭션 안에서 실행됩니다.",
        "정상 종료되면 commit하고, 롤백 대상 예외가 발생하면 rollback합니다.",
    ),
    "spring-jpa-basic": (
        "Service가 Repository 메서드를 호출합니다.",
        "Spring Data JPA가 메서드 이름, JPQL, Querydsl 등의 방식으로 쿼리를 실행합니다.",
        "EntityManager가 영속성 컨텍스트를 통해 Entity를 관리합니다.",
        "트랜잭션 종료 시점에 flush와 dirty checking이 수행될 수 있습니다.",
    ),
    "spring-security-jwt": (
        "로그인 성공 시 서버가 Access Token과 Refresh Token을 발급합니다.",
        "클라이언트는 이후 요청마다 Authorization 헤더에 Bearer 토큰을 담아 보냅니다.",
        "Spring Security Filter가 토큰 서명, 만료 시간, 권한 클레임을 검증합니다.",
        "검증 성공 시 Authentication을 만들어 SecurityContext에 저장합니다.",
        "Controller와 Service는 인증된 사용자와 권한 정보를 바탕으로 요청을 처리합니다.",
    ),
}


SPRING_COMPONENTS: dict[str, tuple[tuple[str, str], ...]] = {
    "spring-rest-api-basics": (
        ("Controller", "HTTP 요청/응답과 라우팅을 담당합니다."),
        ("DTO", "외부 API 계약과 내부 도메인 모델을 분리합니다."),
        ("Service", "비즈니스 유스케이스를 처리합니다."),
        ("Repository", "데이터 접근을 캡슐화합니다."),
        ("ControllerAdvice", "예외 응답을 일관되게 변환합니다."),
    ),
    "spring-layered-architecture": (
        ("Controller", "입력 검증, 요청 매핑, 응답 변환을 담당합니다."),
        ("Service", "비즈니스 규칙과 트랜잭션 경계를 담당합니다."),
        ("Repository", "데이터 저장소 접근을 담당합니다."),
        ("DTO", "계층 간 전달 데이터와 API 표현을 분리합니다."),
    ),
    "spring-ioc-di": (
        ("Bean", "Spring 컨테이너가 생성하고 관리하는 객체입니다."),
        ("BeanDefinition", "Bean 생성과 주입에 필요한 메타데이터입니다."),
        ("BeanFactory", "Bean 생성과 조회를 담당하는 기본 컨테이너입니다."),
        ("ApplicationContext", "BeanFactory에 환경, 이벤트, 메시지 기능을 더한 컨테이너입니다."),
        ("Component Scan", "컴포넌트 애노테이션이 붙은 클래스를 Bean 후보로 찾는 과정입니다."),
    ),
    "spring-mvc-dispatcher-servlet": (
        ("DispatcherServlet", "모든 웹 요청의 중앙 진입점입니다."),
        ("HandlerMapping", "요청을 처리할 핸들러를 찾습니다."),
        ("HandlerAdapter", "찾은 핸들러를 실제로 호출합니다."),
        ("ViewResolver", "뷰 이름을 실제 뷰로 해석합니다."),
        ("HttpMessageConverter", "객체와 JSON 같은 HTTP body를 변환합니다."),
    ),
    "spring-validation-exception": (
        ("Bean Validation", "DTO 제약 조건을 선언적으로 검증합니다."),
        ("BindingResult", "검증 오류 정보를 담습니다."),
        ("RestControllerAdvice", "예외를 공통 API 응답으로 변환합니다."),
        ("ErrorResponse", "클라이언트가 이해할 수 있는 에러 계약입니다."),
    ),
    "spring-transaction": (
        ("TransactionManager", "트랜잭션 시작, commit, rollback을 담당합니다."),
        ("AOP Proxy", "`@Transactional` 메서드 호출을 감싸 트랜잭션을 적용합니다."),
        ("Persistence Context", "JPA Entity 변경을 추적합니다."),
        ("Rollback Rule", "어떤 예외에서 rollback할지 결정합니다."),
    ),
    "spring-jpa-basic": (
        ("JpaRepository", "기본 CRUD, 페이징, 정렬 기능을 제공합니다."),
        ("EntityManager", "Entity 생명주기와 영속성 컨텍스트를 관리합니다."),
        ("Persistence Context", "1차 캐시와 변경 감지를 제공합니다."),
        ("JPQL", "Entity 중심의 객체 지향 쿼리입니다."),
    ),
    "spring-security-jwt": (
        ("SecurityFilterChain", "보안 Filter들의 실행 순서를 정의합니다."),
        ("Authentication", "인증된 사용자와 권한 정보를 표현합니다."),
        ("SecurityContext", "현재 요청의 인증 정보를 보관합니다."),
        ("JwtAuthenticationFilter", "JWT를 검증하고 인증 객체를 만듭니다."),
        ("UserDetailsService", "사용자 정보를 조회하는 표준 확장 지점입니다."),
    ),
}


SPRING_CAUTIONS: dict[str, tuple[str, ...]] = {
    "spring-rest-api-basics": (
        "URI에 행위를 과하게 넣지 말고 리소스 중심으로 설계합니다.",
        "Entity를 그대로 응답하지 말고 요청/응답 DTO를 분리합니다.",
        "성공 응답뿐 아니라 실패 응답 형식도 일관되게 설계합니다.",
        "목록 API는 처음부터 페이징, 정렬, 검색 조건을 고려합니다.",
    ),
    "spring-layered-architecture": (
        "Controller에 비즈니스 로직이 쌓이지 않도록 합니다.",
        "Repository에 화면/API 전용 조합 로직을 과하게 넣지 않습니다.",
        "Service가 너무 많은 유스케이스를 담당하면 책임 분리를 검토합니다.",
        "계층 분리는 파일 위치가 아니라 변경 이유와 테스트 범위를 나누는 일입니다.",
    ),
    "spring-ioc-di": (
        "필드 주입은 테스트와 불변성 측면에서 되도록 피합니다.",
        "생성자 파라미터가 많다면 클래스 책임이 과도한지 점검합니다.",
        "순환 참조는 지연 주입보다 책임 분리로 해결하는 것이 좋습니다.",
        "인터페이스는 실제 교체 가능성과 테스트 필요성을 기준으로 도입합니다.",
    ),
    "spring-mvc-dispatcher-servlet": (
        "Filter와 Interceptor의 실행 위치를 구분해서 공통 로직을 배치합니다.",
        "REST API에서는 ViewResolver가 아니라 HttpMessageConverter 흐름을 이해합니다.",
        "요청/응답 로깅 시 개인정보와 인증 토큰이 남지 않게 주의합니다.",
        "Controller가 화면/응답 변환 이상의 비즈니스 판단을 직접 하지 않게 합니다.",
    ),
    "spring-validation-exception": (
        "검증 실패와 비즈니스 예외를 같은 의미로 처리하지 않습니다.",
        "에러 응답에 스택트레이스나 민감 정보를 노출하지 않습니다.",
        "HTTP 상태 코드와 비즈니스 에러 코드를 일관되게 분리합니다.",
        "클라이언트가 후속 조치를 할 수 있는 메시지와 코드를 제공합니다.",
    ),
    "spring-transaction": (
        "self-invocation에서는 프록시 기반 트랜잭션이 적용되지 않을 수 있습니다.",
        "트랜잭션 안에서 외부 API 호출을 오래 잡고 있지 않도록 합니다.",
        "checked exception은 기본 rollback 대상이 아니므로 정책을 확인합니다.",
        "읽기 전용 조회는 `readOnly = true`를 검토합니다.",
    ),
    "spring-jpa-basic": (
        "Entity를 API 응답으로 직접 노출하지 않습니다.",
        "N+1 문제가 생기지 않도록 fetch 전략과 조회 쿼리를 확인합니다.",
        "영속성 컨텍스트 범위 밖에서 지연 로딩을 접근하면 예외가 발생할 수 있습니다.",
        "복잡한 동적 조회는 메서드 이름 쿼리보다 명시적 쿼리 도구를 검토합니다.",
    ),
    "spring-security-jwt": (
        "JWT payload는 암호화가 아니므로 민감 정보를 넣지 않습니다.",
        "Access Token 만료와 Refresh Token 폐기 전략을 함께 설계합니다.",
        "토큰 탈취 상황에서 로그아웃과 재발급 정책을 고려합니다.",
        "인증 실패와 권한 부족을 401/403으로 구분합니다.",
    ),
}


SPRING_RELATED: dict[str, tuple[tuple[str, str], ...]] = {
    "spring-rest-api-basics": (
        ("HTTP Method", "자원에 대한 행위를 표현합니다."),
        ("HTTP Status Code", "요청 처리 결과를 표준 방식으로 전달합니다."),
        ("DTO", "외부 API 계약을 안정적으로 유지합니다."),
        ("Validation", "잘못된 입력을 Controller 경계에서 차단합니다."),
        ("ControllerAdvice", "공통 예외 응답을 구성합니다."),
    ),
    "spring-layered-architecture": (
        ("DTO", "계층 간 데이터 표현을 분리합니다."),
        ("Transaction Boundary", "Service 유스케이스의 작업 단위를 정합니다."),
        ("Slice Test", "계층별 책임을 독립적으로 검증합니다."),
        ("Domain Model", "비즈니스 규칙이 위치할 대상을 판단합니다."),
    ),
    "spring-ioc-di": (
        ("Bean Scope", "Bean이 언제 생성되고 얼마나 유지되는지 이해하기 위해 필요합니다."),
        ("Component Scan", "Spring이 어떤 클래스를 Bean으로 등록하는지 이해하기 위해 필요합니다."),
        ("`@Autowired`", "Spring의 의존성 주입 지점을 이해하기 위해 필요합니다."),
        ("`@RequiredArgsConstructor`", "생성자 주입을 간결하게 작성할 때 자주 사용합니다."),
        ("AOP Proxy", "Bean으로 등록되어야 트랜잭션 같은 부가 기능 적용이 가능하다는 점과 연결됩니다."),
    ),
    "spring-mvc-dispatcher-servlet": (
        ("Filter", "Servlet 레벨의 공통 처리를 담당합니다."),
        ("Interceptor", "Spring MVC 핸들러 호출 전후 처리를 담당합니다."),
        ("ArgumentResolver", "Controller 파라미터 바인딩을 확장합니다."),
        ("MessageConverter", "JSON 요청/응답 변환을 담당합니다."),
    ),
    "spring-validation-exception": (
        ("Bean Validation", "DTO 필드 검증을 선언적으로 표현합니다."),
        ("Error Code", "클라이언트와 운영자가 실패 원인을 식별합니다."),
        ("HTTP Status", "프로토콜 수준의 실패 의미를 전달합니다."),
        ("Problem Details", "표준화된 API 에러 응답 형식으로 확장할 수 있습니다."),
    ),
    "spring-transaction": (
        ("ACID", "트랜잭션이 보장해야 하는 성질입니다."),
        ("Isolation Level", "동시성 상황에서 읽기 일관성을 결정합니다."),
        ("AOP Proxy", "`@Transactional` 동작 방식을 이해하는 핵심입니다."),
        ("Persistence Context", "JPA 변경 감지와 flush 시점을 이해하는 데 필요합니다."),
        ("Propagation", "트랜잭션 전파 방식을 결정합니다."),
    ),
    "spring-jpa-basic": (
        ("Entity", "DB 테이블과 매핑되는 도메인 객체입니다."),
        ("Persistence Context", "JPA의 1차 캐시와 변경 감지를 제공합니다."),
        ("Fetch Join", "N+1 문제를 해결할 때 자주 사용합니다."),
        ("EntityGraph", "조회 시점의 fetch 계획을 선언적으로 조정합니다."),
        ("Querydsl", "복잡한 동적 쿼리를 타입 안정성 있게 작성합니다."),
    ),
    "spring-security-jwt": (
        ("Authentication", "사용자가 누구인지 확인한 결과입니다."),
        ("Authorization", "사용자가 무엇을 할 수 있는지 판단합니다."),
        ("SecurityContext", "현재 요청의 인증 정보를 저장합니다."),
        ("Refresh Token", "Access Token 재발급 정책과 연결됩니다."),
        ("CORS / CSRF", "브라우저 보안과 API 인증 설계에서 함께 고려합니다."),
    ),
}


SPRING_FALLBACK_CODE: dict[str, str] = {
    "spring-ioc-di": """```java
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private final OrderRepository orderRepository;

    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }
}
```""",
    "spring-mvc-dispatcher-servlet": """```java
@RestController
@RequestMapping("/api/orders")
class OrderController {

    @GetMapping("/{orderId}")
    OrderResponse findOrder(@PathVariable Long orderId) {
        return new OrderResponse(orderId);
    }
}
```""",
    "spring-validation-exception": """```java
record CreateUserRequest(
        @NotBlank String name,
        @Email String email
) {
}

@PostMapping("/users")
UserResponse create(@Valid @RequestBody CreateUserRequest request) {
    return userService.create(request);
}
```""",
    "spring-transaction": """```java
@Service
public class OrderService {

    @Transactional
    public Long createOrder(CreateOrderRequest request) {
        Order order = orderRepository.save(request.toEntity());
        paymentHistoryRepository.save(PaymentHistory.from(order));
        return order.getId();
    }
}
```""",
    "spring-jpa-basic": """```java
interface OwnerRepository extends JpaRepository<Owner, Long> {
    List<Owner> findByLastNameContaining(String lastName);
}
```""",
    "spring-security-jwt": """```java
String token = authorizationHeader.substring("Bearer ".length());
Authentication authentication = jwtProvider.getAuthentication(token);
SecurityContextHolder.getContext().setAuthentication(authentication);
```""",
}


def build_spring_operation(topic: SpringTopic) -> str:
    steps = SPRING_OPERATION_STEPS.get(topic.key)
    if not steps:
        steps = topic.details
    return "\n".join(f"{index}. {step}" for index, step in enumerate(steps, start=1))


def build_spring_components(topic: SpringTopic) -> list[tuple[str, str]]:
    rows = list(SPRING_COMPONENTS.get(topic.key, ()))
    if rows:
        return rows
    return [
        ("Spring Bean", "Spring 컨테이너가 생성하고 관리하는 객체입니다."),
        ("Service", "비즈니스 유스케이스를 처리합니다."),
        ("Repository", "데이터 접근을 담당합니다."),
    ]


def build_spring_implementation_rows(topic: SpringTopic) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in topic.implementation:
        if "는 " in line:
            situation, rest = line.split("는 ", maxsplit=1)
            rows.append((situation.strip(), rest.strip().rstrip("."), "책임과 변경 범위를 명확히 하기 위해서입니다."))
        else:
            rows.append(("실무 적용", line.rstrip("."), "일관된 구조와 유지보수성을 높이기 위해서입니다."))
    return rows[:5]


def build_spring_cautions(topic: SpringTopic) -> tuple[str, ...]:
    return SPRING_CAUTIONS.get(
        topic.key,
        (
            "기능 사용법만 외우지 말고 동작 원리와 적용 조건을 함께 확인합니다.",
            "실무에서는 테스트 가능성, 변경 가능성, 장애 상황을 함께 고려합니다.",
            "공통 설정은 팀 컨벤션과 운영 환경에 맞게 일관되게 관리합니다.",
        ),
    )


def build_spring_code_examples(topic: SpringTopic) -> str:
    if topic.code_examples:
        return "\n\n".join(example.strip() for example in topic.code_examples)
    return SPRING_FALLBACK_CODE.get(topic.key, "이 주제는 코드보다 동작 원리와 설계 기준을 중심으로 정리합니다.")


def build_spring_tail_questions(topic: SpringTopic) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for question in topic.questions:
        rows.append((question, infer_question_direction(question)))
    return rows


def infer_question_direction(question: str) -> str:
    if "차이" in question:
        return "책임, 동작 위치, 사용 시점을 기준으로 비교합니다."
    if "이유" in question or "왜" in question:
        return "해결하려는 문제와 얻는 장점을 함께 설명합니다."
    if "어떻게" in question or "흐름" in question:
        return "처리 순서와 관련 컴포넌트를 단계적으로 설명합니다."
    if "문제" in question or "단점" in question:
        return "발생 원인, 영향, 대안을 함께 설명합니다."
    return "정의, 동작 원리, 실무 주의점을 연결해 답변합니다."


def build_spring_answer_examples(topic: SpringTopic) -> str:
    first_question = topic.questions[0] if topic.questions else f"{topic.title}를 설명해주세요."
    return f"""### Q. {first_question}

{topic.answer}

### Q. 실무에서 {topic.title}을 적용할 때 무엇을 주의해야 하나요?

{build_spring_practical_answer(topic)}"""


def build_spring_practical_answer(topic: SpringTopic) -> str:
    cautions = build_spring_cautions(topic)
    return " ".join(cautions[:2])


def build_spring_related_concepts(topic: SpringTopic) -> list[tuple[str, str]]:
    rows = list(SPRING_RELATED.get(topic.key, ()))
    if rows:
        return rows
    return [
        ("테스트", "기능이 의도대로 동작하는지 검증하기 위해 필요합니다."),
        ("예외 처리", "실패 흐름을 안정적으로 운영하기 위해 필요합니다."),
        ("로깅", "운영 환경에서 문제를 추적하기 위해 필요합니다."),
    ]


def build_spring_detailed_explanation(topic: SpringTopic) -> str:
    details = "\n\n".join(f"- {line}" for line in topic.details)
    comparison = ""
    if topic.key == "spring-ioc-di":
        comparison = """

### DI 방식 비교

| 주입 방식 | 특징 | 실무 판단 |
| --- | --- | --- |
| 생성자 주입 | 생성 시점에 의존성을 전달합니다. | 필수 의존성에 권장합니다. |
| setter 주입 | 객체 생성 후 의존성을 변경할 수 있습니다. | 선택 의존성에 제한적으로 사용합니다. |
| 필드 주입 | 필드에 직접 주입합니다. | 테스트와 불변성 측면에서 비권장합니다. |"""
    if topic.key == "spring-transaction":
        comparison = """

### 트랜잭션 적용 시 확인할 점

| 확인 항목 | 이유 |
| --- | --- |
| 프록시 호출 여부 | self-invocation에서는 트랜잭션이 적용되지 않을 수 있습니다. |
| 롤백 예외 | checked exception은 기본 rollback 대상이 아닙니다. |
| 트랜잭션 범위 | 외부 API 호출을 오래 포함하면 락과 커넥션 점유가 길어질 수 있습니다. |"""
    return f"{details}{comparison}".strip()


def build_spring_topic_section(topic: SpringTopic) -> str:
    operation = build_spring_operation(topic)
    components = build_spring_components(topic)
    cautions = build_spring_cautions(topic)
    code_examples = build_spring_code_examples(topic)
    tail_questions = build_spring_tail_questions(topic)
    related = build_spring_related_concepts(topic)
    petclinic = f"\n- {topic.petclinic_hint}" if topic.petclinic_hint else ""

    return f"""# 오늘의 Spring 백엔드 지식

## 주제

{topic.title}

## Spring 핵심 요약

{bullet_lines(topic.summary)}

## 동작 원리

{operation}

## 내부 구성 요소

{markdown_table(("구성 요소", "역할"), components)}

## 실무 구현 포인트

{markdown_table(("상황", "권장 방식", "이유"), build_spring_implementation_rows(topic))}

## 주의사항

{bullet_lines(cautions)}

## 코드 예시

{code_examples}

## 자주 나오는 꼬리 질문

{markdown_table(("질문", "핵심 답변 방향"), tail_questions)}

## Spring 면접 답변 예시

{build_spring_answer_examples(topic)}

## 함께 알아야 하는 개념

{markdown_table(("개념", "함께 알아야 하는 이유"), related)}
{petclinic}

## 상세 설명

{build_spring_detailed_explanation(topic)}
"""


def note_relative_asset_path(source: Path, raw_src: str) -> str:
    src = raw_src.strip()
    if re.match(r"https?://", src):
        return src
    asset = (source.parent / src).resolve()
    return os.path.relpath(asset, DAILY_NOTES_DIR)


def clean_body_markdown(item: StudyItem) -> str:
    text = item.body.strip()
    if not text:
        return "_원본에 해설이 없으니 직접 답안을 작성해보세요._"

    def replace_img(match: re.Match[str]) -> str:
        attrs = match.group(1)
        src_match = re.search(r"src=[\"']([^\"']+)[\"']", attrs)
        if not src_match:
            return ""
        src = note_relative_asset_path(item.source, src_match.group(1))
        alt = Path(src_match.group(1)).stem.replace("_", " ").replace("-", " ")
        return f"\n\n![{alt}]({src})\n"

    text = re.sub(r"<img\s+([^>]*?)>", replace_img, text, flags=re.IGNORECASE)
    text = re.sub(r"</?div[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?p[^>]*>", "\n", text, flags=re.IGNORECASE)

    cleaned: list[str] = []
    previous_blank = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            if not previous_blank:
                cleaned.append("")
            previous_blank = True
            continue
        line = re.sub(r"^\s{4,}([-*+]\s+)", r"  \1", line)
        line = re.sub(r"^\s{4,}(\d+[.)]\s+)", r"  \1", line)
        cleaned.append(line)
        previous_blank = False

    text = "\n".join(cleaned).strip()
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for match in re.finditer(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", text, flags=re.DOTALL):
        language = match.group(1).strip() or "text"
        code = match.group(2).strip()
        if code:
            blocks.append((language, code))
    return blocks


def build_cs_practical_section(item: StudyItem) -> str:
    lowered = f"{item.title} {strip_markdown(item.body)}".lower()
    if "hash" in lowered or "해시" in lowered:
        lines = [
            "`HashMap`은 단건 조회, 집계, 중복 제거, 캐시성 데이터 관리에 자주 사용됩니다.",
            "`HashSet`은 중복 제거에 적합하고 내부적으로 해시 기반 구조를 사용합니다.",
            "직접 만든 객체를 key로 사용할 때는 `equals()`와 `hashCode()`를 일관되게 구현해야 합니다.",
            "멀티스레드 환경에서 공유 map이 필요하면 `ConcurrentHashMap` 같은 동시성 컬렉션을 검토합니다.",
        ]
    elif "index" in lowered or "인덱스" in lowered:
        lines = [
            "조회 조건과 정렬 조건을 기준으로 인덱스 설계를 검토합니다.",
            "인덱스는 조회를 빠르게 만들 수 있지만 쓰기 비용과 저장 공간을 증가시킬 수 있습니다.",
            "`EXPLAIN`으로 실제 실행 계획을 확인하고 인덱스를 타는지 검증합니다.",
        ]
    elif "transaction" in lowered or "트랜잭션" in lowered:
        lines = [
            "여러 데이터 변경이 하나의 작업 단위로 성공하거나 실패해야 할 때 사용합니다.",
            "격리 수준에 따라 동시성 문제와 성능 비용이 달라집니다.",
            "Spring에서는 보통 Service 계층에 트랜잭션 경계를 둡니다.",
        ]
    else:
        lines = [
            f"`{item.category}` 영역에서 {item.title}가 실제 시스템의 성능, 안정성, 유지보수성에 어떤 영향을 주는지 연결해 봅니다.",
            "비슷한 개념과 비교하면서 언제 이 개념을 선택하고 언제 다른 대안을 선택할지 정리합니다.",
            "운영 환경에서는 데이터 크기, 장애 상황, 보안 요구사항, 성능 병목을 함께 고려합니다.",
        ]
    return "\n".join(f"- {line}" for line in lines)


def build_cs_code_example(item: StudyItem) -> str:
    blocks = extract_code_blocks(item.body)
    if blocks:
        language, code = blocks[0]
        code_lines = code.splitlines()
        if len(code_lines) > 40:
            code = "\n".join(code_lines[:40]).rstrip() + "\n// ..."
        return f"```{language}\n{code}\n```"

    lowered = f"{item.title} {strip_markdown(item.body)}".lower()
    if "hash" in lowered or "해시" in lowered:
        return """```java
Map<String, Integer> countByName = new HashMap<>();

countByName.put("kim", 1);
countByName.put("lee", 2);

System.out.println(countByName.get("kim"));
```"""
    if "greedy" in lowered or "그리디" in lowered or "탐욕" in lowered:
        return """```java
meetings.sort(Comparator.comparingInt(Meeting::endTime));

int count = 0;
int lastEndTime = 0;
for (Meeting meeting : meetings) {
    if (meeting.startTime() >= lastEndTime) {
        count++;
        lastEndTime = meeting.endTime();
    }
}
```"""
    return "이 주제는 코드보다 개념의 동작 원리와 비교 기준을 중심으로 정리합니다."


def build_cs_detailed_explanation(item: StudyItem, body: str) -> str:
    lowered = f"{item.title} {strip_markdown(item.body)}".lower()
    if is_hash_topic(item):
        return """해시는 데이터를 고정된 크기의 값으로 변환하는 방식입니다. 같은 입력은 항상 같은 해시값을 만들고, 좋은 해시 함수는 입력이 조금만 달라져도 해시값이 크게 달라지도록 설계됩니다.

해시는 크게 두 맥락에서 자주 등장합니다. 하나는 자료구조 관점의 해시 테이블이고, 다른 하나는 보안 관점의 암호학적 해시입니다.

| 구분 | 자료구조용 해시 | 보안용 해시 |
| --- | --- | --- |
| 주요 목적 | 빠른 조회와 저장 위치 계산 | 무결성 검증, 원문 추측 방지 |
| 중요한 성질 | 빠른 계산, 균등 분포 | 역상 저항성, 충돌 저항성, 눈사태 효과 |
| 예시 | `HashMap`, `HashSet` | SHA-256, bcrypt, Argon2 |
| 주의점 | 충돌이 많으면 성능 저하 | 비밀번호에는 단순 해시만 사용하면 위험 |

### 해시 충돌 해결

| 구분 | 체이닝 | 개방 주소법 |
| --- | --- | --- |
| 저장 방식 | 같은 버킷에 여러 데이터를 연결 | 테이블 내부의 다른 빈 버킷을 탐색 |
| 장점 | 구현이 직관적이고 삭제가 비교적 쉬움 | 별도 연결 구조가 필요 없음 |
| 단점 | 특정 버킷에 몰리면 탐색 비용 증가 | 테이블이 찰수록 탐사 비용 증가 |
| 예시 | Java `HashMap`의 기본 충돌 처리 방식 | 선형 탐사, 제곱 탐사, 이중 해싱 |

### Load Factor와 재해싱

```text
Load Factor = 저장된 엔트리 수 / 버킷 배열 크기
```

Load Factor가 높아질수록 빈 버킷이 줄어들고 충돌 가능성이 커집니다. 충돌이 많아지면 해시 테이블의 평균 `O(1)` 성능을 기대하기 어려워지므로, 구현체는 일정 임계값을 넘었을 때 버킷 배열을 확장합니다.

재해싱은 기존 엔트리를 확장된 버킷 배열 기준으로 다시 배치하는 과정입니다. 버킷 수가 달라지면 같은 key라도 계산되는 인덱스가 달라질 수 있기 때문입니다.

### 함께 알아야 하는 개념

| 개념 | 이유 |
| --- | --- |
| 해시 함수 | key를 버킷 위치로 변환하는 핵심입니다. |
| 해시 충돌 | 서로 다른 key가 같은 버킷에 매핑되는 상황입니다. |
| 체이닝 | 같은 버킷에 여러 엔트리를 연결해 충돌을 처리합니다. |
| 개방 주소법 | 충돌 시 테이블 내부의 다른 빈 버킷을 찾습니다. |
| Load Factor | 테이블이 얼마나 찼는지 나타내며 resize 기준이 됩니다. |
| `equals()` / `hashCode()` | Java 해시 컬렉션의 key 동등성 판단에 필요합니다. |

면접에서는 해시를 "고유한 값으로 바꾼다"라고만 말하면 위험합니다. 실제로는 충돌 가능성이 존재하므로, 해시는 데이터를 빠르게 찾기 위한 인덱싱 도구이며 충돌을 어떻게 처리하느냐가 성능의 핵심이라고 설명하는 편이 더 정확합니다."""

    sections: list[str] = [body]
    if "hash" in lowered or "해시" in lowered:
        sections.append(
            """### 함께 알아야 하는 개념

| 개념 | 이유 |
| --- | --- |
| 해시 함수 | key를 버킷 위치로 변환하는 핵심입니다. |
| 해시 충돌 | 서로 다른 key가 같은 버킷에 매핑되는 상황입니다. |
| 체이닝 | 같은 버킷에 여러 엔트리를 연결해 충돌을 처리합니다. |
| 개방 주소법 | 충돌 시 테이블 내부의 다른 빈 버킷을 찾습니다. |
| Load Factor | 테이블이 얼마나 찼는지 나타내며 resize 기준이 됩니다. |
| `equals()` / `hashCode()` | Java 해시 컬렉션의 key 동등성 판단에 필요합니다. |"""
        )
    return "\n\n".join(section.strip() for section in sections if section.strip())


def build_note(item: StudyItem, spring_topic: SpringTopic, today: date) -> str:
    body = clean_body_markdown(item)
    title = display_title(item)
    return f"""# {today.isoformat()} 1일 2CS/면접 지식

---

# 오늘의 CS 지식

## 주제

{title}

## 카테고리

`{item.category}`

## 핵심 요약

{build_summary_section(item)}

## 면접 포인트

{build_interview_points(item)}

## 자주 나오는 면접 질문

{build_related_questions(item)}

## 면접 답변 예시

{build_interview_answer_examples(item)}

## 실무 관점

{build_cs_practical_section(item)}

## 코드 예시

{build_cs_code_example(item)}

## 상세 설명

{build_cs_detailed_explanation(item, body)}

---

{build_spring_topic_section(spring_topic)}
"""


def append_study_log(item: StudyItem, spring_topic: SpringTopic, today: date, output_path: Path) -> None:
    entries = load_study_log()
    entry = {
        "date": today.isoformat(),
        "key": item.key,
        "title": item.title,
        "category": item.category,
        "source": item.source.relative_to(ROOT).as_posix(),
        "note": output_path.relative_to(ROOT).as_posix(),
        "github_url": item.github_url or "",
        "spring_key": spring_topic.key,
        "spring_title": spring_topic.title,
    }
    entries = [old for old in entries if old.get("date") != entry["date"] and old.get("key") != entry["key"]]
    entries.append(entry)
    save_study_log(entries)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one daily CS/interview prep note.")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD, default: today")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing daily note")
    parser.add_argument("--category", help="Filter by category, e.g. os, network, db, java, spring")
    parser.add_argument("--list-categories", action="store_true", help="Show available categories and exit")
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date)
    category = normalize_category(args.category)
    DAILY_NOTES_DIR.mkdir(parents=True, exist_ok=True)
    STUDY_STATE_DIR.mkdir(parents=True, exist_ok=True)

    if args.list_categories:
        print("\n".join(sorted(CATEGORY_ALIASES)))
        return

    output_path = DAILY_NOTES_DIR / f"yonghun-cs-interview-{target_date.isoformat()}.md"
    if output_path.exists() and not args.force:
        print(f"Already exists: {output_path}")
        return

    items = collect_items(category=category)
    if not items:
        hint = f" for category '{category}'" if category else ""
        raise SystemExit(f"No study items found{hint}. Add .md or .txt files to my_materials/.")

    used = load_used()
    spring_used = load_spring_used()
    item = choose_item_for_date(items, used, target_date, args.force)
    spring_topic = choose_spring_topic_for_date(spring_used, target_date, args.force)
    output_path.write_text(build_note(item, spring_topic, target_date), encoding="utf-8")

    if item.key not in used:
        used.append(item.key)
        save_used(used)
    if spring_topic.key not in spring_used:
        spring_used.append(spring_topic.key)
        save_spring_used(spring_used)
    append_study_log(item, spring_topic, target_date, output_path)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
