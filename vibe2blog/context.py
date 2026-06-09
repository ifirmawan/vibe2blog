from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_LANGUAGES = {"id", "en"}


@dataclass(frozen=True)
class SessionContext:
    topic: str
    session_summary: str
    transcript_excerpt: str
    git_diff: str
    verification_notes: str
    language: str
    tone: str
    audience: str
    include_code_snippets: bool
    include_frontmatter: bool
    editorial_quality_pass: bool

    @property
    def safe_topic(self) -> str:
        """Return the user title, or a stable fallback inferred from the session."""
        return self.topic.strip() or self.inferred_topic

    @property
    def inferred_topic(self) -> str:
        """Use the first summary line as a lightweight title when no topic is provided."""
        first_line = self.session_summary.strip().splitlines()[0]
        for prefix in ("Masalah awal:", "Initial problem:"):
            if first_line.lower().startswith(prefix.lower()):
                first_line = first_line[len(prefix) :].strip()
        return first_line[:72].strip(" .") or "Vibe Coding Field Notes"


def normalize_context(
    *,
    topic: str = "",
    session_summary: str,
    transcript_excerpt: str = "",
    git_diff: str = "",
    verification_notes: str = "",
    language: str = "id",
    tone: str = "reflective",
    audience: str = "developers",
    include_code_snippets: bool = True,
    include_frontmatter: bool = True,
    editorial_quality_pass: bool = True,
) -> SessionContext:
    """Validate UI/API inputs and collapse optional blanks into safe defaults."""
    summary = session_summary.strip()
    if not summary:
        raise ValueError("Session summary is required.")

    normalized_language = language.strip().lower()
    if normalized_language not in SUPPORTED_LANGUAGES:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
        raise ValueError(f"Unsupported language '{language}'. Supported values: {supported}.")

    return SessionContext(
        topic=topic.strip(),
        session_summary=summary,
        transcript_excerpt=transcript_excerpt.strip(),
        git_diff=git_diff.strip(),
        verification_notes=verification_notes.strip(),
        language=normalized_language,
        tone=tone.strip() or "reflective",
        audience=audience.strip() or "developers",
        include_code_snippets=include_code_snippets,
        include_frontmatter=include_frontmatter,
        editorial_quality_pass=editorial_quality_pass,
    )
