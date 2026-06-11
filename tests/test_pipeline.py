from __future__ import annotations

import tempfile
import unittest
from unittest.mock import patch

from vibe2blog.pipeline import generate_article


class ArticlePipelineTest(unittest.TestCase):
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

    def test_pipeline_generates_article_from_raw_claude_code_input(self) -> None:
        raw_transcript = """
        > Fix modal bottom sheet overlaps with native navigation bottom bar
        ⏺ Read(src/screens/HomeScreen.tsx)
        ⏺ I found the issue. The modal uses fixed padding and ignores safe area insets.
        ⏺ Update(src/screens/HomeScreen.tsx)
        + const insets = useSafeAreaInsets();
        + paddingBottom: 24 + insets.bottom + 70,
        ⏺ Bash(npm run type-check)
        ⏺ Done. The fix is complete.
        """

        result = generate_article(
            session_summary=raw_transcript,
            language="id",
            tone="concise",
            include_frontmatter=False,
        )

        markdown = result.generation.markdown
        self.assertIn("## Ringkasan", markdown)
        self.assertIn("Masalah awal", markdown)
        self.assertIn("useSafeAreaInsets", markdown)
        self.assertIn("src/screens/HomeScreen.tsx", markdown)
        self.assertNotIn("⏺", markdown)
        self.assertTrue(result.validation.valid)

    def test_pipeline_applies_modal_polish_when_configured(self) -> None:
        polished = """---
title: "Vibe2Blog"
---

## Problem
Polished draft.

## Context
Specific context.

## Change
Specific change.

## Verification
Specific verification.
"""

        with patch("vibe2blog.pipeline.should_polish_with_modal", return_value=True):
            with patch("vibe2blog.pipeline.maybe_polish_markdown", return_value=polished):
                result = generate_article(
                    topic="Vibe2Blog",
                    session_summary="We built a Gradio app for turning coding sessions into Markdown.",
                    language="en",
                )

        self.assertIn("Polished draft", result.generation.markdown)
        self.assertIn("+modal-polish", result.generation.provider)
        self.assertIn("Modal polish applied.", result.generation.quality_notes)
        self.assertTrue(result.validation.valid)


if __name__ == "__main__":
    unittest.main()
