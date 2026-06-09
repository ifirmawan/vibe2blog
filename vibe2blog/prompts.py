from __future__ import annotations

from .context import SessionContext


LANGUAGE_LABELS = {
    "id": {
        "name": "Indonesian",
        "sections": [
            "Masalah",
            "Konteks Sesi",
            "Proses Implementasi",
            "Keputusan Teknis",
            "Verifikasi",
            "Pelajaran",
            "Kesimpulan",
        ],
    },
    "en": {
        "name": "English",
        "sections": [
            "Problem",
            "Session Context",
            "Implementation Story",
            "Technical Decisions",
            "Verification",
            "Lessons Learned",
            "Conclusion",
        ],
    },
}


def build_article_prompt(context: SessionContext) -> str:
    labels = LANGUAGE_LABELS[context.language]
    snippets_instruction = (
        "Include short, selected code snippets only when they clarify the story."
        if context.include_code_snippets
        else "Do not include code snippets."
    )
    frontmatter_instruction = (
        "Start with YAML frontmatter."
        if context.include_frontmatter
        else "Do not include YAML frontmatter."
    )

    sections = "\n".join(f"- {section}" for section in labels["sections"])
    return f"""Write a polished Markdown blog draft in {labels["name"]}.

Topic: {context.safe_topic}
Tone: {context.tone}
Audience: {context.audience}

Requirements:
- {frontmatter_instruction}
- Use concrete details from the coding session.
- Avoid generic AI phrasing and empty motivational language.
- Preserve technical tradeoffs, decisions, and verification.
- {snippets_instruction}
- Keep the post editable and honest; do not invent facts.

Expected sections:
{sections}

Session summary:
{context.session_summary}

Transcript excerpt:
{context.transcript_excerpt or "(not provided)"}

Git diff excerpt:
{context.git_diff or "(not provided)"}

Verification notes:
{context.verification_notes or "(not provided)"}
"""


def build_quality_prompt(markdown: str, context: SessionContext) -> str:
    labels = LANGUAGE_LABELS[context.language]
    return f"""Improve this Markdown draft in {labels["name"]}.

Quality rubric:
- Specific to the supplied coding session.
- Natural engineering narrative.
- Concrete technical detail.
- Clear transitions.
- No generic AI phrases.
- No invented facts.
- Keep valid Markdown and frontmatter if present.

Return only the improved Markdown.

Draft:
{markdown}
"""

