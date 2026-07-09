"""Text cleanup helpers for upstream market data."""


def repair_mojibake_text(value: str) -> str:
    """Repair UTF-8 text that was decoded as a single-byte Windows encoding."""
    if not isinstance(value, str) or not value:
        return value

    original_cjk = _count_cjk(value)
    for encoding in ("latin1", "cp1252"):
        try:
            repaired = value.encode(encoding).decode("utf-8")
        except UnicodeError:
            continue
        if _count_cjk(repaired) > original_cjk:
            return repaired

    return value


def _count_cjk(value: str) -> int:
    return sum(1 for char in value if "\u4e00" <= char <= "\u9fff")
