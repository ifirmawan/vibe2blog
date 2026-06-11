from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from vibe2blog.context import normalize_context
from vibe2blog.modal_polisher import (
    build_polish_system_prompt,
    build_polish_user_prompt,
    maybe_polish_markdown,
    modal_polish_enabled,
    polish_markdown_with_modal,
    should_polish_with_modal,
)


class ModalPolisherTest(unittest.TestCase):
    def test_modal_polish_is_disabled_by_default(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(modal_polish_enabled())
            self.assertFalse(should_polish_with_modal())

    def test_modal_polish_requires_flag_and_base_url(self) -> None:
        with patch.dict(
            os.environ,
            {
                "MODAL_POLISH_ENABLED": "true",
                "MODAL_VLLM_BASE_URL": "https://example.modal.run",
            },
            clear=True,
        ):
            self.assertTrue(modal_polish_enabled())
            self.assertTrue(should_polish_with_modal())

    def test_indonesian_prompt_preserves_facts_and_markdown(self) -> None:
        prompt = build_polish_system_prompt("id")

        self.assertIn("Pertahankan semua klaim faktual", prompt)
        self.assertIn("YAML frontmatter", prompt)
        self.assertIn("code block", prompt)
        self.assertIn("Jangan mengarang", prompt)
        self.assertIn("Jangan memberi contoh", prompt)

    def test_user_prompt_includes_style_context(self) -> None:
        context = normalize_context(
            session_summary="We fixed a bug.",
            language="en",
            tone="tutorial",
            audience="maintainers",
        )

        prompt = build_polish_user_prompt("## Draft", context)

        self.assertIn("Language: en", prompt)
        self.assertIn("Tone: tutorial", prompt)
        self.assertIn("Audience: maintainers", prompt)
        self.assertIn("Return the edited version of this exact draft only.", prompt)
        self.assertIn("## Draft", prompt)

    def test_polish_markdown_calls_openai_compatible_endpoint(self) -> None:
        context = normalize_context(session_summary="We fixed a bug.", language="en")
        response_body = (
            '{"choices":[{"message":{"content":"---\\ntitle: \\"Draft\\"\\n---'
            '\\n\\n## Problem\\nPolished draft."}}]}'
        )

        with patch.dict(
            os.environ,
            {
                "MODAL_VLLM_BASE_URL": "https://example.modal.run",
                "MODAL_VLLM_MODEL": "llm",
                "MODAL_POLISH_TIMEOUT": "12",
            },
            clear=True,
        ):
            with patch("vibe2blog.modal_polisher.post_json_with_modal_redirect", return_value=response_body) as post:
                polished = polish_markdown_with_modal("## Problem\nDraft.", context)

        self.assertIn("Polished draft", polished)
        endpoint, payload, headers = post.call_args.args
        self.assertEqual(endpoint, "https://example.modal.run/v1/chat/completions")
        self.assertEqual(payload["model"], "llm")
        self.assertEqual(payload["temperature"], 0.35)
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_maybe_polish_falls_back_to_original_when_modal_fails(self) -> None:
        context = normalize_context(session_summary="We fixed a bug.", language="en")
        original = "## Problem\nOriginal draft."

        with patch.dict(
            os.environ,
            {
                "MODAL_POLISH_ENABLED": "true",
                "MODAL_VLLM_BASE_URL": "https://example.modal.run",
            },
            clear=True,
        ):
            with patch("vibe2blog.modal_polisher.polish_markdown_with_modal", return_value=""):
                self.assertEqual(maybe_polish_markdown(original, context), original)


if __name__ == "__main__":
    unittest.main()
