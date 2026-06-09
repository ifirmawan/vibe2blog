from __future__ import annotations

import re


SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*([^\s\"']+)"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
]


def redact_secrets(text: str) -> str:
    """Mask common API token patterns before content is sent to any model provider."""
    redacted = text

    def key_value_replacer(match: re.Match[str]) -> str:
        """Preserve the key name so users can see which field was redacted."""
        return f"{match.group(1)}=[REDACTED]"

    redacted = SECRET_PATTERNS[0].sub(key_value_replacer, redacted)
    for pattern in SECRET_PATTERNS[1:]:
        redacted = pattern.sub("[REDACTED_SECRET]", redacted)
    return redacted
