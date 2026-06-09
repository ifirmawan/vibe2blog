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
        if normalized_tone(context) == "tutorial":
            return build_indonesian_tutorial_template(context, title)
        return build_indonesian_template(context, title)
    if normalized_tone(context) == "tutorial":
        return build_english_tutorial_template(context, title)
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

Berdasarkan catatan sesi, penyebab utamanya adalah mismatch antara asumsi kode dan nilai yang benar-benar dikirim oleh sistem saat runtime. Dalam kasus seperti ini, langkah pentingnya adalah membaca helper/controller yang terlibat, mencari kondisi permission yang gagal, lalu membandingkan nama object/context yang dicek kode dengan nilai aktual dari framework.

## Langkah Perbaikan

1. Buka file atau helper yang menangani permission/authentication.
2. Cari kondisi yang membedakan object type, context, atau user role.
3. Cocokkan nilai yang dicek kode dengan nilai yang dipakai framework saat request berjalan.
4. Ubah kondisi hanya pada bagian yang salah, tanpa memperluas permission lebih dari kebutuhan.
5. Simpan catatan mengapa nilai tersebut benar agar pembaca berikutnya tidak mengulang asumsi lama.{code_section}

## Cara Menguji

{verification}

## Kenapa Perbaikan Ini Bekerja

Perbaikan ini bekerja karena kode tidak lagi mengecek nilai object type yang keliru. Setelah kondisi permission memakai nilai runtime yang benar, pengguna yang memang berhak dapat melewati pengecekan tanpa membuka akses untuk skenario lain.

## Catatan Penutup

Bug permission sering terlihat seperti masalah token atau role, padahal akar masalahnya bisa sesederhana nama object type yang berbeda dari asumsi awal. Selalu verifikasi nilai yang dikirim framework sebelum memperluas aturan akses.
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

The core issue was a mismatch between what the code expected and what the framework actually passed at runtime. For this kind of bug, the useful path is to read the permission or authentication helper, find the condition that blocks the request, and compare the object/context names in code with the framework's real values.

## Fix Steps

1. Open the helper or controller that handles permissions/authentication.
2. Find the condition that checks object type, context, or user role.
3. Compare the checked value with the value the framework passes during the request.
4. Update only the incorrect condition, without widening permissions beyond the intended user action.
5. Leave a short note in code explaining the framework value so the old assumption does not return.{code_section}

## How to Test

{verification}

## Why This Works

The fix works because the permission check now uses the runtime object type that the framework actually sends. Once the condition matches reality, the legitimate user action can pass while unrelated access paths stay constrained.

## Closing Notes

Permission bugs can look like token or role problems, but sometimes the root cause is a naming mismatch. Verify the framework-provided values before broadening access rules.
"""


def build_frontmatter(title: str, language: str) -> str:
    escaped_title = title.replace('"', '\\"')
    return f"""---
title: "{escaped_title}"
tags: ["agentic-ai", "vibe-coding", "gradio"]
language: "{language}"
---

"""


def build_code_section(context: SessionContext, *, language: str) -> str:
    if not context.include_code_snippets or not context.git_diff:
        return ""
    label = (
        "Potongan perubahan yang relevan"
        if language == "id"
        else "Relevant change excerpt"
    )
    return f"\n\n### {label}\n\n```diff\n{trim_text(context.git_diff, 900)}\n```"


def as_quote_block(text: str) -> str:
    lines = trim_text(text, 1400).splitlines()
    return "\n".join(f"> {line}" if line else ">" for line in lines)


def normalized_tone(context: SessionContext) -> str:
    return context.tone.strip().lower()


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
