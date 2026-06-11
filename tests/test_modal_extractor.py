from __future__ import annotations

import json
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from vibe2blog.modal_extractor import (
    build_chat_completions_url,
    build_system_prompt,
    parse_chat_completion_content,
    post_json_with_modal_redirect,
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

    def test_post_json_preserves_post_body_across_modal_303_redirect(self) -> None:
        redirect = urllib.error.HTTPError(
            "https://example.modal.run/v1/chat/completions",
            303,
            "See Other",
            {"Location": "https://example.modal.run/call-id/v1/chat/completions"},
            None,
        )
        final = MagicMock()
        final.__enter__.return_value.read.return_value = b'{"ok": true}'
        final.__exit__.return_value = False
        opener = MagicMock()
        opener.open.side_effect = [redirect, final]

        with patch("vibe2blog.modal_extractor.urllib.request.build_opener", return_value=opener):
            body = post_json_with_modal_redirect(
                "https://example.modal.run/v1/chat/completions",
                {"model": "llm"},
                {"Content-Type": "application/json"},
                timeout=10,
            )

        self.assertEqual(body, '{"ok": true}')
        first_request = opener.open.call_args_list[0].args[0]
        second_request = opener.open.call_args_list[1].args[0]
        self.assertEqual(first_request.get_method(), "POST")
        self.assertEqual(second_request.get_method(), "POST")
        self.assertEqual(first_request.data, second_request.data)
        self.assertEqual(second_request.full_url, "https://example.modal.run/call-id/v1/chat/completions")


if __name__ == "__main__":
    unittest.main()
