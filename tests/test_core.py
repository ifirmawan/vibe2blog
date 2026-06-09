from __future__ import annotations

import tempfile
import unittest

from vibe2blog.context import normalize_context
from vibe2blog.exporter import build_filename, slugify
from vibe2blog.pipeline import generate_article
from vibe2blog.prompts import build_article_prompt
from vibe2blog.redactor import redact_secrets
from vibe2blog.validator import validate_markdown


class Vibe2BlogCoreTest(unittest.TestCase):
    def test_requires_session_summary(self) -> None:
        with self.assertRaises(ValueError):
            normalize_context(session_summary="")

    def test_rejects_unsupported_language(self) -> None:
        with self.assertRaises(ValueError):
            normalize_context(session_summary="hello", language="jp")

    def test_redacts_common_secret_patterns(self) -> None:
        text = "api_key=abc123 sk-abcdefghijklmnopqrstuvwxyz123456 hf_abcdefghijklmnopqrstuvwxyz"
        redacted = redact_secrets(text)
        self.assertIn("[REDACTED]", redacted)
        self.assertIn("[REDACTED_SECRET]", redacted)
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz123456", redacted)

    def test_prompt_uses_indonesian_sections(self) -> None:
        context = normalize_context(session_summary="Membangun aplikasi Gradio.", language="id")
        prompt = build_article_prompt(context)
        self.assertIn("Masalah", prompt)
        self.assertIn("Keputusan Teknis", prompt)

    def test_prompt_uses_english_sections(self) -> None:
        context = normalize_context(session_summary="Build a Gradio app.", language="en")
        prompt = build_article_prompt(context)
        self.assertIn("Problem", prompt)
        self.assertIn("Technical Decisions", prompt)

    def test_markdown_validation(self) -> None:
        markdown = """---
title: "A Draft"
---

## One
## Two
## Three
## Four
"""
        result = validate_markdown(markdown)
        self.assertTrue(result.valid)

    def test_slugify_and_filename(self) -> None:
        self.assertEqual(slugify("Hello, Vibe2Blog!"), "hello-vibe2blog")
        self.assertTrue(build_filename("Hello, Vibe2Blog!").endswith("hello-vibe2blog.md"))

    def test_pipeline_generates_downloadable_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_article(
                topic="Vibe2Blog",
                session_summary="We built a Gradio app for turning coding sessions into Markdown.",
                language="en",
                output_dir=tmpdir,
            )
        self.assertIn("Vibe2Blog", result.generation.markdown)
        self.assertTrue(result.validation.valid)

    def test_tutorial_tone_changes_indonesian_template_structure(self) -> None:
        result = generate_article(
            topic="Customer unable to update their own data via WooCommerce API",
            session_summary="WooCommerce passed object_type user, while the code checked customer.",
            git_diff="- if ( $object_type === 'customer' )\n+ if ( $object_type === 'user' )",
            verification_notes="Retested PUT /wc/v3/customers/3 and the customer could update their own first_name.",
            language="id",
            tone="tutorial",
        )
        markdown = result.generation.markdown
        self.assertIn("## Tujuan", markdown)
        self.assertIn("## Langkah Perbaikan", markdown)
        self.assertIn("## Cara Menguji", markdown)
        self.assertIn("object_type", markdown)
        self.assertNotIn("## Proses Implementasi", markdown)

    def test_reflective_tone_keeps_narrative_structure(self) -> None:
        result = generate_article(
            topic="Vibe2Blog",
            session_summary="We built a Gradio app for turning coding sessions into Markdown.",
            language="en",
            tone="reflective",
        )
        markdown = result.generation.markdown
        self.assertIn("## Implementation Story", markdown)
        self.assertNotIn("## Fix Steps", markdown)


if __name__ == "__main__":
    unittest.main()
