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
REFERENCE_REPOS_DIR = ROOT / "reference_repos"
DAILY_NOTES_DIR = ROOT / "daily_notes"
STUDY_STATE_DIR = ROOT / "study_state"
STUDIED_ITEMS_FILE = STUDY_STATE_DIR / "studied_items.json"
STUDY_LOG_FILE = STUDY_STATE_DIR / "study_log.json"
REFERENCE_REPOS_FILE = ROOT / "reference_repos.json"
REVIEW_INTERVALS = (1, 3, 7)
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
        raw = f"{self.source.as_posix()}\n{self.title}\n{self.body}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


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


def load_reference_repos() -> dict[str, dict[str, str]]:
    if not REFERENCE_REPOS_FILE.exists():
        return {}
    data = json.loads(REFERENCE_REPOS_FILE.read_text(encoding="utf-8"))
    return {repo["name"]: repo for repo in data}


def build_github_url(path: Path, repos: dict[str, dict[str, str]]) -> str | None:
    try:
        relative = path.relative_to(REFERENCE_REPOS_DIR)
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
    if REFERENCE_REPOS_DIR.exists():
        search_roots.append(REFERENCE_REPOS_DIR)

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


def choose_item(items: list[StudyItem], used: list[str]) -> StudyItem:
    unused = [item for item in items if item.key not in used]
    if unused:
        return unused[0]
    return items[0]


def review_items_due(log_entries: list[dict[str, str]], today: date) -> list[dict[str, str]]:
    due: list[dict[str, str]] = []
    seen_keys: set[str] = set()
    for entry in reversed(log_entries):
        studied_at = date.fromisoformat(entry["date"])
        days_since = (today - studied_at).days
        if days_since not in REVIEW_INTERVALS or entry["key"] in seen_keys:
            continue
        due.append({**entry, "days_since": str(days_since)})
        seen_keys.add(entry["key"])
    return list(reversed(due))


def build_review_section(items: list[dict[str, str]]) -> str:
    if not items:
        return "- 오늘 예정된 간격 복습은 없습니다."
    lines = []
    for item in items:
        lines.append(f"- D+{item['days_since']} `{item['category']}` {item['title']}")
    return "\n".join(lines)



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


def build_note(item: StudyItem, today: date, due_reviews: list[dict[str, str]]) -> str:
    body = clean_body_markdown(item)
    return f"""# {today.isoformat()} 1일 1CS/면접 지식

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

## 오늘의 복습

{build_review_section(due_reviews)}
"""


def append_study_log(item: StudyItem, today: date, output_path: Path) -> None:
    entries = load_study_log()
    entry = {
        "date": today.isoformat(),
        "key": item.key,
        "title": item.title,
        "category": item.category,
        "source": item.source.relative_to(ROOT).as_posix(),
        "note": output_path.relative_to(ROOT).as_posix(),
        "github_url": item.github_url or "",
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
    item = choose_item(items, used)
    due_reviews = review_items_due(load_study_log(), target_date)
    output_path.write_text(build_note(item, target_date, due_reviews), encoding="utf-8")

    if item.key not in used:
        used.append(item.key)
        save_used(used)
    append_study_log(item, target_date, output_path)

    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
