#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "reference_repos.json"
REFERENCE_REPOS_DIR = ROOT / "reference_repos"


def run(command: list[str], cwd: Path | None = None) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def load_repos() -> list[dict[str, str]]:
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def main() -> None:
    REFERENCE_REPOS_DIR.mkdir(parents=True, exist_ok=True)
    for repo in load_repos():
        name = repo["name"]
        url = repo["url"]
        target = REFERENCE_REPOS_DIR / name
        if target.exists():
            run(["git", "pull", "--ff-only"], cwd=target)
        else:
            run(["git", "clone", "--depth", "1", url, str(target)])

    print(f"Synced repositories into: {REFERENCE_REPOS_DIR}")


if __name__ == "__main__":
    main()
