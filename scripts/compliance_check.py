"""Pre-push compliance checks for tracked files."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BANNED_TRACKED_PREFIXES = (
    ".claude/",
    ".codex/",
    "data/",
    "api/data/",
    "logs/",
    "api/logs/",
    "reports/",
    "frontend/.next/",
    "frontend/node_modules/",
    "frontend-design/",
    "landing-page-guide-v2/",
)

BANNED_TRACKED_SUFFIXES = (
    ".env",
    ".env.local",
    ".parquet",
    ".pyc",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".tsbuildinfo",
)

SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(api[_-]?key|secret|token|password|passwd|private[_-]?key|jwt_secret_key)\b"
    r"\s*[:=]\s*['\"]?([^'\"\s`]+)"
)

ALLOWED_PLACEHOLDER_MARKERS = (
    "your",
    "change",
    "example",
    "placeholder",
    "localhost",
    "username",
    "password",
    "<",
    "generate",
)

SKIP_TEXT_SCAN_SUFFIXES = (
    ".lock",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".parquet",
)


def git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def is_placeholder(value: str) -> bool:
    normalized = value.strip().strip("\"'").lower()
    if normalized in {"none", "null", "str", "optional[str]", "string"}:
        return True
    if "(" in normalized or "[" in normalized:
        return True
    return not normalized or any(marker in normalized for marker in ALLOWED_PLACEHOLDER_MARKERS)


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return None


def main() -> int:
    problems: list[str] = []
    tracked = git_ls_files()

    for rel in tracked:
        lowered = rel.lower()
        exists = (ROOT / rel).exists()
        if lowered.endswith(BANNED_TRACKED_SUFFIXES) and not lowered.endswith(".env.example"):
            suffix = " (stage the deletion with git add -A)" if not exists else ""
            problems.append(f"Tracked local/build/data file: {rel}{suffix}")
        if lowered.startswith(BANNED_TRACKED_PREFIXES):
            suffix = " (stage the deletion with git add -A)" if not exists else ""
            problems.append(f"Tracked local/build/data directory entry: {rel}{suffix}")

    for rel in tracked:
        if rel.lower().endswith(SKIP_TEXT_SCAN_SUFFIXES):
            continue
        text = read_text(ROOT / rel)
        if text is None:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            for match in SECRET_ASSIGNMENT.finditer(line):
                value = match.group(2)
                if len(value) < 12 or is_placeholder(value):
                    continue
                problems.append(f"Possible secret in {rel}:{line_no} ({match.group(1)})")

    if problems:
        print("Compliance check failed:")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print("Compliance check passed: no obvious tracked secrets or local artifacts found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
