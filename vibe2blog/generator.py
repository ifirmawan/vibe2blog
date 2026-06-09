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
        """Generate a Markdown article from normalized session context."""
        raise NotImplementedError


class TemplateArticleGenerator(ArticleGenerator):
    provider_name = "template-fallback"

    def generate(self, context: SessionContext) -> GenerationResult:
        """Generate deterministic drafts so tests and demos work without a model key."""
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
        """Store the hosted model name and optional Hugging Face token override."""
        self.model = model
        self.token = token or os.getenv("HF_TOKEN")

    def generate(self, context: SessionContext) -> GenerationResult:
        """Generate article Markdown through Hugging Face hosted inference."""
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
    """Select hosted inference when configured, otherwise use deterministic fallback."""
    model = os.getenv("VIBE2BLOG_MODEL", "").strip()
    if model and os.getenv("HF_TOKEN"):
        return HuggingFaceInferenceGenerator(model=model)
    return TemplateArticleGenerator()


def build_template_article(context: SessionContext) -> str:
    """Route deterministic generation to the selected language and tone template."""
    title = context.safe_topic
    tone = normalized_tone(context)
    if context.language == "id":
        if tone == "tutorial":
            return build_indonesian_tutorial_template(context, title)
        if tone == "concise":
            return build_indonesian_concise_template(context, title)
        if tone == "narrative":
            return build_indonesian_narrative_template(context, title)
        return build_indonesian_reflective_template(context, title)
    if tone == "tutorial":
        return build_english_tutorial_template(context, title)
    if tone == "concise":
        return build_english_concise_template(context, title)
    if tone == "narrative":
        return build_english_narrative_template(context, title)
    return build_english_reflective_template(context, title)


def build_indonesian_reflective_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "id") if context.include_frontmatter else ""
    code_section = build_code_section(context, language="id")
    verification = context.verification_notes or "Perbaikan perlu diuji ulang pada skenario yang sebelumnya gagal, lalu dibandingkan dengan perilaku sebelum perubahan."
    return f"""{frontmatter}## Masalah

Sesi ini berangkat dari masalah berikut: {title}.

## Apa yang Ditemukan

{as_quote_block(context.session_summary)}

## Keputusan Perbaikan

Bagian penting dari sesi ini adalah memperbaiki asumsi yang tidak sesuai dengan perilaku nyata di runtime. Alih-alih mengubah banyak area sekaligus, perubahan diarahkan ke titik yang benar-benar menyebabkan workflow gagal.

{code_section}

## Verifikasi

{verification}

## Refleksi

Perbaikan ini menarik karena akar masalahnya bukan pada keseluruhan fitur, melainkan pada detail kecil yang menghubungkan asumsi kode dengan perilaku framework atau platform. Detail semacam ini mudah terlewat ketika kita hanya melihat gejala dari luar.

## Kesimpulan

Pelajaran utamanya: ketika sebuah workflow gagal, verifikasi dulu nilai, state, atau kondisi yang benar-benar terjadi di runtime sebelum memperbesar cakupan perubahan. Perubahan kecil yang tepat sering lebih aman daripada patch yang terlalu luas.
"""


def build_indonesian_concise_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "id") if context.include_frontmatter else ""
    code_section = build_code_section(context, language="id")
    verification = context.verification_notes or "Uji ulang skenario yang sebelumnya gagal dan pastikan jalur akses lain tidak ikut terbuka."
    return f"""{frontmatter}## Ringkasan

- Masalah: {title}
- Inti temuan: ada perbedaan antara asumsi kode dan kondisi runtime.
- Arah perbaikan: ubah titik yang keliru tanpa memperbesar cakupan patch.

## Konteks Penting

{as_quote_block(context.session_summary)}

## Perubahan

- Fokus pada titik kode yang memicu gejala utama.
- Cocokkan state, nilai, atau constraint yang dicek kode dengan kondisi yang benar-benar dipakai framework.
- Tambahkan catatan singkat agar alasan perubahan jelas untuk maintainer berikutnya.{code_section}

## Verifikasi

{verification}

## Catatan Lanjutan

- Jangan mengabaikan diagnostic IDE begitu saja, tetapi bedakan false positive dari error runtime.
- Simpan test manual atau automated test untuk skenario yang sebelumnya gagal.
"""


def build_indonesian_narrative_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "id") if context.include_frontmatter else ""
    code_section = build_code_section(context, language="id")
    verification = context.verification_notes or "Setelah perubahan, skenario yang sama perlu dijalankan lagi untuk memastikan gejalanya hilang."
    return f"""{frontmatter}## Pembuka

Bug ini terlihat sederhana dari luar: {title}. Tetapi sesi coding menunjukkan bahwa kegagalannya tersembunyi di detail kecil antara asumsi kode dan perilaku framework atau platform.

## Momen Menemukan Akar Masalah

{as_quote_block(context.session_summary)}

## Perubahan Kecil yang Menentukan

Yang membuat perbaikan ini penting adalah ukurannya kecil tetapi tepat sasaran. Alih-alih mengubah seluruh fitur, perubahan diarahkan ke kondisi yang salah membaca kebutuhan runtime.

{code_section}

## Setelah Diuji

{verification}

## Penutup

Sesi ini mengingatkan bahwa debugging sering berjalan dari gejala besar ke detail kecil. Ketika detail itu akhirnya cocok dengan kenyataan runtime, masalah yang tampak rumit bisa selesai dengan perubahan yang sangat terukur.
"""


def build_indonesian_tutorial_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "id") if context.include_frontmatter else ""
    code_section = build_code_section(context, language="id")
    verification = context.verification_notes or "Uji kembali endpoint atau workflow yang bermasalah dengan skenario yang sama seperti sebelum perbaikan."
    return f"""{frontmatter}## Tujuan

Tutorial ini menjelaskan cara menelusuri dan memperbaiki masalah dari sesi coding berikut: {title}.

## Gejala

Masalah yang terlihat dari sesi ini:

{as_quote_block(context.session_summary)}

## Akar Masalah

Berdasarkan catatan sesi, penyebab utamanya adalah mismatch antara asumsi kode dan kondisi yang benar-benar terjadi saat runtime. Dalam kasus seperti ini, langkah pentingnya adalah membaca file yang terlibat, mencari kondisi yang memicu gejala, lalu membandingkan logika kode dengan nilai, state, atau constraint aktual dari framework.

## Langkah Perbaikan

1. Buka file yang paling dekat dengan gejala yang dilaporkan.
2. Cari kondisi, state, atau perhitungan layout/data yang menentukan perilaku tersebut.
3. Cocokkan asumsi kode dengan nilai yang dipakai framework saat workflow berjalan.
4. Ubah hanya bagian yang salah, tanpa memperluas patch ke area yang tidak terkait.
5. Simpan catatan singkat agar pembaca berikutnya memahami alasan perubahan.{code_section}

## Cara Menguji

{verification}

## Kenapa Perbaikan Ini Bekerja

Perbaikan ini bekerja karena kode kembali selaras dengan kondisi runtime yang sebenarnya. Setelah logika memakai nilai atau state yang benar, skenario yang sah dapat berjalan tanpa mengubah area lain yang tidak terkait.

## Catatan Penutup

Bug sering terlihat lebih besar dari akar masalahnya. Selalu verifikasi nilai, state, dan constraint yang dikirim framework sebelum memperluas cakupan perubahan.
"""


def build_english_reflective_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "en") if context.include_frontmatter else ""
    code_section = build_code_section(context, language="en")
    verification = context.verification_notes or "The fix should be retested against the scenario that failed before and compared with the previous behavior."
    return f"""{frontmatter}## Problem

This session focused on the following problem: {title}.

## What We Found

{as_quote_block(context.session_summary)}

## Fix Decision

The important move was to correct the assumption that did not match runtime behavior. Instead of changing broad areas at once, the fix targets the condition that caused the workflow to fail.

{code_section}

## Verification

{verification}

## Reflection

The interesting part of this fix is that the visible symptom looked broader than the actual cause. The problem was not the whole feature, but a small mismatch between the code's assumption and the framework or platform behavior.

## Conclusion

When a workflow fails, verify the real runtime values, state, and constraints before widening the patch. A small, precise change is usually safer than a broad workaround.
"""


def build_english_concise_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "en") if context.include_frontmatter else ""
    code_section = build_code_section(context, language="en")
    verification = context.verification_notes or "Retest the failing scenario and confirm unrelated access paths remain constrained."
    return f"""{frontmatter}## Summary

- Problem: {title}
- Key finding: the code assumption did not match the runtime condition.
- Fix direction: change the incorrect condition without widening the patch.

## Important Context

{as_quote_block(context.session_summary)}

## Change

- Inspect the code path closest to the visible symptom.
- Match the checked value, state, or constraint with what the framework actually uses.
- Add a short code note so the reason stays visible to future maintainers.{code_section}

## Verification

{verification}

## Follow-up Notes

- Keep the failing request as a regression scenario.
- Treat IDE diagnostics separately from runtime behavior when working inside a framework environment.
"""


def build_english_narrative_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "en") if context.include_frontmatter else ""
    code_section = build_code_section(context, language="en")
    verification = context.verification_notes or "After the change, rerun the same scenario to confirm the symptom is gone."
    return f"""{frontmatter}## Opening

From the outside, the bug looked straightforward: {title}. The session showed that the real failure lived in a small gap between the code's assumption and the framework or platform call path.

## Finding the Root Cause

{as_quote_block(context.session_summary)}

## The Small Change That Mattered

The useful part of the fix was its precision. Instead of rewriting the whole feature, the change corrected the condition that was reading the wrong runtime signal.

{code_section}

## After Testing

{verification}

## Closing

This is the kind of debugging session where a small detail changes the whole outcome. Once the code matched what the framework actually required, the failing scenario could succeed without loosening unrelated behavior.
"""


def build_english_tutorial_template(context: SessionContext, title: str) -> str:
    frontmatter = build_frontmatter(title, "en") if context.include_frontmatter else ""
    code_section = build_code_section(context, language="en")
    verification = context.verification_notes or "Retest the failing endpoint or workflow with the same scenario that failed before the fix."
    return f"""{frontmatter}## Goal

This tutorial walks through how to diagnose and fix the issue from this coding session: {title}.

## Symptom

The session showed this failure mode:

{as_quote_block(context.session_summary)}

## Root Cause

The core issue was a mismatch between what the code expected and what the framework actually did at runtime. For this kind of bug, the useful path is to read the closest code path, find the condition that triggers the symptom, and compare the code's assumptions with the framework's real values or constraints.

## Fix Steps

1. Open the file closest to the reported symptom.
2. Find the condition, state, or calculation that controls the behavior.
3. Compare the checked value with what the framework uses during the workflow.
4. Update only the incorrect condition, without expanding the patch beyond the intended behavior.
5. Leave a short note explaining the runtime value so the old assumption does not return.{code_section}

## How to Test

{verification}

## Why This Works

The fix works because the code now uses the runtime signal that the framework actually provides. Once the condition matches reality, the failing scenario can pass while unrelated behavior stays constrained.

## Closing Notes

Bugs often look larger than they are, but sometimes the root cause is a small mismatch in naming, state, layout, or data shape. Verify framework-provided values before broadening the fix.
"""


def build_frontmatter(title: str, language: str) -> str:
    """Create minimal YAML frontmatter compatible with static blog engines."""
    escaped_title = title.replace('"', '\\"')
    return f"""---
title: "{escaped_title}"
tags: ["agentic-ai", "vibe-coding", "gradio"]
language: "{language}"
---

"""


def build_code_section(context: SessionContext, *, language: str) -> str:
    """Include a bounded diff excerpt only when the user enables code snippets."""
    if not context.include_code_snippets or not context.git_diff:
        return ""
    label = (
        "Potongan perubahan yang relevan"
        if language == "id"
        else "Relevant change excerpt"
    )
    return f"\n\n### {label}\n\n```diff\n{trim_text(context.git_diff, 900)}\n```"


def as_quote_block(text: str) -> str:
    """Display extracted context as a Markdown quote without dumping unlimited text."""
    lines = trim_text(text, 1400).splitlines()
    return "\n".join(f"> {line}" if line else ">" for line in lines)


def normalized_tone(context: SessionContext) -> str:
    """Normalize tone values from UI/CLI-style inputs before template routing."""
    return context.tone.strip().lower()


def editorial_rewrite(markdown: str, context: SessionContext) -> str:
    """Inject concrete transcript notes into legacy template sections when present."""
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
    """Return lightweight rubric feedback for the generated draft metadata panel."""
    lower = markdown.lower()
    found = [phrase for phrase in GENERIC_PHRASES if phrase in lower]
    if found:
        return "Needs editorial pass: generic phrases detected."
    if len(markdown.split()) < 180:
        return "Needs expansion: draft is short."
    return "Looks specific enough for a first editable draft."


def extract_title(markdown: str) -> str:
    """Prefer frontmatter title, then fall back to a top-level Markdown heading."""
    frontmatter_match = re.search(r'^title:\s*"(.+?)"', markdown, re.MULTILINE)
    if frontmatter_match:
        return frontmatter_match.group(1)
    heading_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    return heading_match.group(1).strip() if heading_match else ""


def trim_text(text: str, limit: int) -> str:
    """Bound prompt-visible snippets so long transcripts stay manageable."""
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 3].rstrip() + "..."
