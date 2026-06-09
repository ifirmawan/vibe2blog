from __future__ import annotations

import json
import unittest

from vibe2blog.modal_extractor import (
    build_chat_completions_url,
    build_system_prompt,
    parse_chat_completion_content,
)


class ModalExtractorTest(unittest.TestCase):
    def test_builds_openai_compatible_chat_url(self) -> None:
        self.assertEqual(
            build_chat_completions_url("https://workspace--app-serve.modal.run"),
            "https://workspace--app-serve.modal.run/v1/chat/completions",
        )
        self.assertEqual(
            build_chat_completions_url("https://workspace--app-serve.modal.run/v1"),
            "https://workspace--app-serve.modal.run/v1/chat/completions",
        )

    def test_indonesian_system_prompt_requests_extraction_headings(self) -> None:
        prompt = build_system_prompt("id")

        self.assertIn("Masalah awal", prompt)
        self.assertIn("File terkait", prompt)
        self.assertIn("Jangan menyalin marker tool mentah", prompt)

    def test_parses_chat_completion_content(self) -> None:
        body = json.dumps({"choices": [{"message": {"content": "Initial problem: fixed"}}]})

        self.assertEqual(parse_chat_completion_content(body), "Initial problem: fixed")


if __name__ == "__main__":
    unittest.main()
