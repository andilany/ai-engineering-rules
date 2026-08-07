from __future__ import annotations

from ai_rules.errors import ConfigurationError

START = "<!-- ai-engineering-rules:start -->"
END = "<!-- ai-engineering-rules:end -->"


def _validate(existing: str) -> tuple[int, int]:
    starts = existing.count(START)
    ends = existing.count(END)
    if starts == 0 and ends == 0:
        return -1, -1
    if starts != 1 or ends != 1:
        raise ConfigurationError("Invalid ai-engineering-rules managed block markers")
    start = existing.index(START)
    end = existing.index(END)
    if end < start:
        raise ConfigurationError("Invalid ai-engineering-rules managed block markers")
    return start, end


def _block(generated: str) -> str:
    body = generated.strip("\n")
    return f"{START}\n{body}\n{END}\n"


def upsert_managed_block(existing: str, generated: str) -> str:
    start, end = _validate(existing)
    block = _block(generated)
    if start < 0:
        if not existing:
            return block
        prefix = existing if existing.endswith("\n") else existing + "\n"
        return prefix + block
    end_after = end + len(END)
    if end_after < len(existing) and existing[end_after] == "\n":
        end_after += 1
    return existing[:start] + block + existing[end_after:]


def remove_managed_block(existing: str) -> str:
    start, end = _validate(existing)
    if start < 0:
        return existing
    end_after = end + len(END)
    if end_after < len(existing) and existing[end_after] == "\n":
        end_after += 1
    return existing[:start] + existing[end_after:]
