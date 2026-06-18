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
    if "greedy" in lowered or "그리디" in lowered or "탐욕" in lowered:
        points = [
            "그리디 알고리즘: 매 순간의 최선 선택으로 전체 해답을 구성하는 방식이라고 설명할 수 있어야 합니다.",
            "핵심 키워드: 탐욕 선택 속성, 최적 부분 구조, 정렬, 반례, 시간 복잡도",
            "완전탐색/동적 계획법과 비교해 탐색 범위를 줄이는 대신 정당성 증명이 필요하다는 점을 말할 수 있어야 합니다.",
            "회의실 배정, 거스름돈처럼 어떤 선택 기준이 전체 최적해로 이어지는지 예시로 설명하면 좋습니다.",
        ]
        return "\n".join(f"- {point}" for point in points)

    keywords = extract_keywords(item.title, item.body, limit=5)
    if not keywords:
        keywords = ["정의", "동작 방식", "장단점", "실무 적용", "주의점"]
    points = [
        f"{item.title}: 무엇인지 한 문장으로 설명할 수 있어야 합니다.",
        f"핵심 키워드: {', '.join(keywords)}",
        "비슷한 개념과 비교했을 때 어떤 차이가 있는지 정리해두면 좋습니다.",
        "실무에서 성능, 안정성, 확장성 중 무엇에 영향을 주는지 연결해서 생각해봅니다.",
    ]
    return "\n".join(f"- {point}" for point in points)


def is_likely_interview_question(text: str) -> bool:
    if len(text) < 8 or len(text) > 120:
        return False
    if re.search(r"[🙎🙋💁🤷🤦🙍🙆💰]", text):
        return False
    if ":" in text and not re.search(r"(차이|설명|무엇|왜|어떻게|이유|장단점|특징)", text):
        return False
    return bool(re.search(r"(\?|설명|차이|무엇|왜|어떻게|이유|장단점|특징)", text))


def build_related_questions(item: StudyItem) -> str:
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
    return "\n".join(f"- {question}" for question in deduped[:6])


def concept_name(title: str) -> str:
    name = re.sub(r"^\s*\[|\]\s*$", "", title).strip()
    return name


def build_interview_answer_examples(item: StudyItem) -> str:
    title = concept_name(item.title)
    lowered = f"{title} {strip_markdown(item.body)}".lower()

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


def build_spring_topic_section(topic: SpringTopic) -> str:
    petclinic = ""
    if topic.petclinic_hint:
        petclinic = f"""
### PetClinic 참고 포인트

- {topic.petclinic_hint}
"""
    code_examples = ""
    if topic.code_examples:
        code_examples = "\n## Spring 코드 예시\n\n" + "\n".join(topic.code_examples).rstrip() + "\n"
    return f"""## 오늘의 Spring 백엔드 지식

{topic.title}

## Spring 핵심 요약

{bullet_lines(topic.summary)}

## Spring 조금 더 자세히

{bullet_lines(topic.details)}

## Spring 구현 체크리스트

{bullet_lines(topic.implementation)}
{code_examples}
{petclinic}
## Spring 면접 질문

{bullet_lines(topic.questions)}

## Spring 면접 답변 예시

{topic.answer}
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


def build_note(item: StudyItem, spring_topic: SpringTopic, today: date) -> str:
    body = clean_body_markdown(item)
    return f"""# {today.isoformat()} 1일 2CS/면접 지식

## 오늘의 CS 지식

{item.title}

## 카테고리

`{item.category}`

## 핵심 요약

{build_summary_section(item)}

## 조금 더 자세히

{body}

## 면접 포인트

{build_interview_points(item)}

## 연관되어 자주 나오는 면접 질문

{build_related_questions(item)}

## 면접 답변 예시

{build_interview_answer_examples(item)}

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
