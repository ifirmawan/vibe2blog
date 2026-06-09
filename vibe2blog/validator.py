from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    issues: list[str]


def validate_markdown(markdown: str, *, require_frontmatter: bool = True) -> ValidationResult:
    """Check generated drafts for the minimum structure expected by the UI."""
    issues: list[str] = []
    content = markdown.strip()
    if not content:
        issues.append("Markdown output is empty.")
    if require_frontmatter and not content.startswith("---"):
        issues.append("YAML frontmatter is missing.")
    if require_frontmatter and not re.search(r'^title:\s*".+?"', content, re.MULTILINE):
        issues.append("Frontmatter title is missing.")
    if len(re.findall(r"^##\s+", content, re.MULTILINE)) < 4:
        issues.append("Markdown output should include at least four body sections.")
    if "[placeholder]" in content.lower() or "lorem ipsum" in content.lower():
        issues.append("Placeholder text detected.")
    return ValidationResult(valid=not issues, issues=issues)
