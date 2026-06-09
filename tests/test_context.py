from __future__ import annotations

import unittest

from vibe2blog.context import normalize_context


class SessionContextTest(unittest.TestCase):
    def test_requires_session_summary(self) -> None:
        with self.assertRaises(ValueError):
            normalize_context(session_summary="")

    def test_rejects_unsupported_language(self) -> None:
        with self.assertRaises(ValueError):
            normalize_context(session_summary="hello", language="jp")

    def test_inferred_topic_ignores_extraction_prefixes(self) -> None:
        context = normalize_context(session_summary="Masalah awal: Fix modal bottom sheet overlap.")

        self.assertEqual(context.inferred_topic, "Fix modal bottom sheet overlap")


if __name__ == "__main__":
    unittest.main()
