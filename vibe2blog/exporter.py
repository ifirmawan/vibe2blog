from __future__ import annotations

import re
from datetime import date
from pathlib import Path


def slugify(value: str) -> str:
    """Convert a generated title into a filesystem-friendly Markdown slug."""
    lowered = value.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "vibe2blog-draft"


def build_filename(title: str, *, today: date | None = None) -> str:
    """Create a deterministic date-prefixed filename for exported drafts."""
    current = today or date.today()
    return f"{current.isoformat()}-{slugify(title)}.md"


def write_markdown(markdown: str, title: str, output_dir: str | Path = "/tmp") -> str:
    """Write Markdown to disk and return the path Gradio can expose for download."""
    path = Path(output_dir) / build_filename(title)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    return str(path)
