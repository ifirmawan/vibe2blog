from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from vibe2blog.extractor import maybe_extract_session_summary


RAW_CLAUDE_TRANSCRIPT = """
> Fix modal bottom sheet overlaps with native navigation bottom bar

⏺ I'll inspect the bottom sheet implementation.
⏺ Read(src/screens/HomeScreen.tsx)
⎿ Read 100 lines
⏺ I found the issue. The bottom sheet padding doesn't account for safe area insets.
⏺ Update(src/screens/HomeScreen.tsx)
⎿ Updated src/screens/HomeScreen.tsx with 2 additions
+ import { useSafeAreaInsets } from 'react-native-safe-area-context';
+ paddingBottom: 24 + insets.bottom + 70,
⏺ Bash(npm run type-check)
⎿ Found pre-existing type errors
⏺ Bash(npx eslint src/screens/HomeScreen.tsx)
⎿ ESLint completed with existing warnings
⏺ Done. The branch is now focused on the advanced filters fix.
"""


class TranscriptExtractorTest(unittest.TestCase):
    def test_extracts_claude_code_raw_transcript_into_summary(self) -> None:
        summary = maybe_extract_session_summary(RAW_CLAUDE_TRANSCRIPT, language="id")

        self.assertIn("Masalah awal", summary)
        self.assertIn("bottom sheet overlaps", summary)
        self.assertIn("Temuan utama", summary)
        self.assertIn("safe area insets", summary)
        self.assertIn("Perubahan yang dilakukan", summary)
        self.assertIn("useSafeAreaInsets", summary)
        self.assertIn("Verifikasi", summary)
        self.assertIn("type-check", summary)
        self.assertIn("File terkait", summary)
        self.assertIn("src/screens/HomeScreen.tsx", summary)
        self.assertNotIn("⏺", summary)
        self.assertNotIn("Bash(", summary)
        self.assertIn("Command: npm run type-check", summary)

    def test_uses_modal_summary_when_endpoint_is_configured(self) -> None:
        modal_summary = "Masalah awal: Modal returned a compact extraction."
        with patch.dict(os.environ, {"MODAL_VLLM_BASE_URL": "https://example.modal.run"}):
            with patch("vibe2blog.extractor.summarize_with_modal_vllm", return_value=modal_summary):
                summary = maybe_extract_session_summary(RAW_CLAUDE_TRANSCRIPT, language="id")

        self.assertEqual(summary, modal_summary)

    def test_falls_back_to_deterministic_extraction_when_modal_fails(self) -> None:
        with patch.dict(os.environ, {"MODAL_VLLM_BASE_URL": "https://example.modal.run"}):
            with patch("vibe2blog.extractor.summarize_with_modal_vllm", return_value=""):
                summary = maybe_extract_session_summary(RAW_CLAUDE_TRANSCRIPT, language="id")

        self.assertIn("Masalah awal", summary)
        self.assertIn("src/screens/HomeScreen.tsx", summary)


if __name__ == "__main__":
    unittest.main()
