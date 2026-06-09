from __future__ import annotations

import os
import re
from dataclasses import dataclass

from .context import SessionContext
from .prompts import build_article_prompt, build_quality_prompt


GENERIC_PHRASES = [
    "in today's fast-paced world",
    "game changer",
    "revolutionize",
    "unlock the power",
    "seamlessly",
]


@dataclass(frozen=True)
class GenerationResult:
    markdown: str
    title: str
    quality_notes: str
    prompt: str
    provider: str


class ArticleGenerator:
    def generate(self, context: SessionContext) -> GenerationResult:
        raise NotImplementedError


class TemplateArticleGenerator(ArticleGenerator):
    provider_name = "template-fallback"

    def generate(self, context: SessionContext) -> GenerationResult:
        prompt = build_article_prompt(context)
        markdown = build_template_article(context)
        quality_notes = score_quality(markdown)
        if context.editorial_quality_pass:
            markdown = editorial_rewrite(markdown, context)
            quality_notes = score_quality(markdown)
        return GenerationResult(
            markdown=markdown,
            title=extract_title(markdown) or context.safe_topic,
            quality_notes=quality_notes,
            prompt=prompt,
            provider=self.provider_name,
        )


class HuggingFaceInferenceGenerator(ArticleGenerator):
    provider_name = "huggingface-inference"

    def __init__(self, model: str, token: str | None = None):
        self.model = model
        self.token = token or os.getenv("HF_TOKEN")

    def generate(self, context: SessionContext) -> GenerationResult:
        try:
            from huggingface_hub import InferenceClient
        except ImportError as exc:
            raise RuntimeError("huggingface_hub is required for hosted inference.") from exc

        if not self.token:
            raise RuntimeError("HF_TOKEN is required for hosted inference.")

        client = InferenceClient(model=self.model, token=self.token)
        prompt = build_article_prompt(context)
        response = client.text_generation(
            prompt,
            max_new_tokens=1400,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.08,
        )
        markdown = response.strip()

        if context.editorial_quality_pass:
            quality_prompt = build_quality_prompt(markdown, context)
            markdown = client.text_generation(
                quality_prompt,
                max_new_tokens=1400,
                temperature=0.55,
                top_p=0.9,
                repetition_penalty=1.08,
            ).strip()

        return GenerationResult(
            markdown=markdown,
            title=extract_title(markdown) or context.safe_topic,
            quality_notes=score_quality(markdown),
            prompt=prompt,
            provider=f"{self.provider_name}:{self.model}",
        )


def get_default_generator() -> ArticleGenerator:
    model = os.getenv("VIBE2BLOG_MODEL", "").strip()
    if model and os.getenv("HF_TOKEN"):
        return HuggingFaceInferenceGenerator(model=model)
    return TemplateArticleGenerator()


def build_template_article(context: SessionContext) -> str:
    title = context.safe_topic
    if context.language == "id":
        return build_indonesian_template(context, title)
    return build_english_template(context, title)


def build_indonesian_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "id") if context.include_frontmatter else ""
    code_section = (
        "\n\nContoh potongan konteks teknis yang paling relevan:\n\n```diff\n"
        f"{trim_text(context.git_diff, 900)}\n```"
        if context.include_code_snippets and context.git_diff
        else ""
    )
    return f"""{frontmatter}## Masalah

Sesi ini berangkat dari kebutuhan untuk mengubah aktivitas vibe coding menjadi draft artikel Markdown yang bisa dibaca ulang, diedit, dan dibagikan.

## Konteks Sesi

{context.session_summary}

## Proses Implementasi

Fokus implementasi diarahkan pada alur yang praktis: pengguna memberi ringkasan sesi, memilih bahasa dan gaya tulisan, lalu Vibe2Blog menyusun cerita teknis dari konteks tersebut. Transkrip dan diff diperlakukan sebagai bahan pendukung, bukan sesuatu yang harus ditempel utuh.

## Keputusan Teknis

- Gradio menjadi antarmuka utama untuk demo hackathon.
- Output tetap Markdown agar mudah dipindahkan ke blog atau dokumentasi.
- Bahasa `{context.language}` dipilih agar heading, frontmatter, dan narasi konsisten.
- Redaksi secret dilakukan sebelum konteks dipakai untuk membuat draft.
- Editorial quality pass dipakai untuk mengurangi tulisan generik dan memperkuat detail konkret.{code_section}

## Verifikasi

{context.verification_notes or "Draft ini perlu diverifikasi lewat sample data, validasi Markdown, dan smoke test di Hugging Face Space."}

## Pelajaran

Sesi ini menunjukkan bahwa hasil kerja dengan AI agent tidak harus berhenti sebagai percakapan. Dengan struktur yang tepat, keputusan kecil, tradeoff, dan hasil verifikasi bisa berubah menjadi catatan lapangan yang berguna.

## Kesimpulan

Vibe2Blog membantu menjaga pengetahuan dari sesi agentic coding tetap hidup: bukan sebagai log mentah, tetapi sebagai draft tulisan yang siap diedit oleh manusia.
"""


def build_english_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "en") if context.include_frontmatter else ""
    code_section = (
        "\n\nRelevant technical context:\n\n```diff\n"
        f"{trim_text(context.git_diff, 900)}\n```"
        if context.include_code_snippets and context.git_diff
        else ""
    )
    return f"""{frontmatter}## Problem

This session started from a practical need: turning vibe coding activity into an editable Markdown article that preserves the reasoning behind the work.

## Session Context

{context.session_summary}

## Implementation Story

The implementation focuses on a direct workflow: provide session context, choose language and tone, then let Vibe2Blog shape the material into a technical narrative. Transcript excerpts and diffs are supporting material, not raw content dumps.

## Technical Decisions

- Gradio is the primary interface for the hackathon demo.
- Markdown remains the main output because it is portable.
- Language `{context.language}` keeps headings, frontmatter, and prose consistent.
- Likely secrets are redacted before draft generation.
- The editorial quality pass reduces generic prose and strengthens concrete detail.{code_section}

## Verification

{context.verification_notes or "This draft should be verified with sample data, Markdown validation, and a Hugging Face Space smoke test."}

## Lessons Learned

Agentic coding sessions contain more than code changes. With the right structure, decisions, tradeoffs, and validation steps can become useful field notes.

## Conclusion

Vibe2Blog keeps the knowledge from an AI-assisted coding session alive as a human-editable article draft rather than a raw conversation log.
"""


def build_frontmatter(title: str, language: str) -> str:
    escaped_title = title.replace('"', '\\"')
    return f"""---
title: "{escaped_title}"
tags: ["agentic-ai", "vibe-coding", "gradio"]
language: "{language}"
---

"""


def editorial_rewrite(markdown: str, context: SessionContext) -> str:
    if context.transcript_excerpt and "## Konteks Sesi" in markdown:
        return markdown.replace(
            "## Proses Implementasi",
            f"Catatan konkret dari percakapan: {trim_text(context.transcript_excerpt, 320)}\n\n## Proses Implementasi",
            1,
        )
    if context.transcript_excerpt and "## Implementation Story" in markdown:
        return markdown.replace(
            "## Implementation Story",
            f"Concrete note from the conversation: {trim_text(context.transcript_excerpt, 320)}\n\n## Implementation Story",
            1,
        )
    return markdown


def score_quality(markdown: str) -> str:
    lower = markdown.lower()
    found = [phrase for phrase in GENERIC_PHRASES if phrase in lower]
    if found:
        return "Needs editorial pass: generic phrases detected."
    if len(markdown.split()) < 180:
        return "Needs expansion: draft is short."
    return "Looks specific enough for a first editable draft."


def extract_title(markdown: str) -> str:
    frontmatter_match = re.search(r'^title:\s*"(.+?)"', markdown, re.MULTILINE)
    if frontmatter_match:
        return frontmatter_match.group(1)
    heading_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    return heading_match.group(1).strip() if heading_match else ""


def trim_text(text: str, limit: int) -> str:
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 3].rstrip() + "..."

