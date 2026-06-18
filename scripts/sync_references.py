#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_FILE = ROOT / "reference_repos.json"
REFERENCE_REPOS_CACHE_DIR = ROOT / "reference_repos"
REFERENCE_SNAPSHOT_DIR = ROOT / "references" / "sources"


def run(command: list[str], cwd: Path | None = None) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def load_repos() -> list[dict[str, str]]:
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def main() -> None:
    REFERENCE_REPOS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    REFERENCE_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    for repo in load_repos():
        name = repo["name"]
        url = repo["url"]
        cache_target = REFERENCE_REPOS_CACHE_DIR / name
        snapshot_target = REFERENCE_SNAPSHOT_DIR / name
        if cache_target.exists():
            run(["git", "pull", "--ff-only"], cwd=cache_target)
        else:
            run(["git", "clone", "--depth", "1", url, str(cache_target)])

        if snapshot_target.exists():
            shutil.rmtree(snapshot_target)
        shutil.copytree(
            cache_target,
            snapshot_target,
            ignore=shutil.ignore_patterns(".git"),
        )

    print(f"Synced repository cache into: {REFERENCE_REPOS_CACHE_DIR}")
    print(f"Updated tracked reference snapshots in: {REFERENCE_SNAPSHOT_DIR}")


if __name__ == "__main__":
    main()
