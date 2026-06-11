from __future__ import annotations

from dataclasses import dataclass

from .context import SessionContext, normalize_context
from .exporter import write_markdown
from .extractor import maybe_extract_session_summary
from .generator import ArticleGenerator, GenerationResult, get_default_generator
from .modal_polisher import should_polish_with_modal, maybe_polish_markdown
from .redactor import redact_secrets
from .validator import ValidationResult, validate_markdown


@dataclass(frozen=True)
class PipelineResult:
    generation: GenerationResult
    validation: ValidationResult
    download_path: str


def build_context_with_redaction(**kwargs: object) -> SessionContext:
    """Normalize inputs, redact secrets, then summarize raw transcripts if needed."""
    context = normalize_context(**kwargs)
    redacted_summary = redact_secrets(context.session_summary)
    extracted_summary = maybe_extract_session_summary(
        redacted_summary,
        language=context.language,
    )
    return SessionContext(
        topic=redact_secrets(context.topic),
        session_summary=extracted_summary,
        transcript_excerpt=redact_secrets(context.transcript_excerpt),
        git_diff=redact_secrets(context.git_diff),
        verification_notes=redact_secrets(context.verification_notes),
        language=context.language,
        tone=context.tone,
        audience=context.audience,
        include_code_snippets=context.include_code_snippets,
        include_frontmatter=context.include_frontmatter,
        editorial_quality_pass=context.editorial_quality_pass,
    )


def generate_article(
    *,
    generator: ArticleGenerator | None = None,
    output_dir: str = "/tmp",
    **kwargs: object,
) -> PipelineResult:
    """Run the full article flow: context prep, generation, validation, and export."""
    context = build_context_with_redaction(**kwargs)
    active_generator = generator or get_default_generator()
    generation = active_generator.generate(context)
    if should_polish_with_modal():
        polished_markdown = maybe_polish_markdown(generation.markdown, context)
        if polished_markdown != generation.markdown:
            generation = GenerationResult(
                markdown=polished_markdown,
                title=generation.title,
                quality_notes=f"{generation.quality_notes} Modal polish applied.",
                prompt=generation.prompt,
                provider=f"{generation.provider}+modal-polish",
            )
    validation = validate_markdown(
        generation.markdown,
        require_frontmatter=context.include_frontmatter,
    )
    download_path = write_markdown(generation.markdown, generation.title, output_dir=output_dir)
    return PipelineResult(
        generation=generation,
        validation=validation,
        download_path=download_path,
    )
