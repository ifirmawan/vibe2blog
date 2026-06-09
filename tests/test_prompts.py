from __future__ import annotations

import unittest

from vibe2blog.context import normalize_context
from vibe2blog.prompts import build_article_prompt


class PromptBuilderTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
