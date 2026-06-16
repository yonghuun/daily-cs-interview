#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DAILY_NOTES_DIR = ROOT / "daily_notes"
STUDY_STATE_DIR = ROOT / "study_state"
STUDY_LOG_FILE = STUDY_STATE_DIR / "study_log.json"


def load_study_log() -> list[dict[str, str]]:
    if not STUDY_LOG_FILE.exists():
        return []
    try:
        data = json.loads(STUDY_LOG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def week_bounds(day: date) -> tuple[date, date]:
    start = day - timedelta(days=day.weekday())
    end = start + timedelta(days=6)
    return start, end


def build_review(entries: list[dict[str, str]], start: date, end: date) -> str:
    weekly = [
        entry
        for entry in entries
        if start <= date.fromisoformat(entry["date"]) <= end
    ]
    weekly.sort(key=lambda entry: (entry["date"], entry["category"], entry["title"]))

    if not weekly:
        questions = "- 이번 주 기록된 학습 노트가 없습니다."
        categories = "- 기록 없음"
    else:
        questions = "\n".join(
            f"- {entry['date']} `{entry['category']}` {entry['title']}" for entry in weekly
        )
        counts = Counter(entry["category"] for entry in weekly)
        categories = "\n".join(f"- `{category}`: {count}개" for category, count in sorted(counts.items()))

    return f"""# {start.isoformat()} ~ {end.isoformat()} CS/면접 주간 리뷰

## 이번 주 질문

{questions}

## 카테고리 분포

{categories}

## 다시 답해볼 질문

- 가장 막혔던 질문:
- 설명이 길어진 질문:
- 실무 예시가 부족했던 질문:

## 다음 주 집중 주제

- 
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a weekly CS/interview review note.")
    parser.add_argument("--date", default=date.today().isoformat(), help="Any date in the target week")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing weekly review")
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date)
    start, end = week_bounds(target_date)
    DAILY_NOTES_DIR.mkdir(parents=True, exist_ok=True)

    output_path = DAILY_NOTES_DIR / f"yonghun-cs-weekly-review-{start.isoformat()}.md"
    if output_path.exists() and not args.force:
        print(f"Already exists: {output_path}")
        return

    output_path.write_text(build_review(load_study_log(), start, end), encoding="utf-8")
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()

