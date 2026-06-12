from __future__ import annotations

import unittest

from vibe2blog.pipeline import generate_article


class ToneTemplateTest(unittest.TestCase):
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

    def test_reflective_tone_keeps_reflective_structure(self) -> None:
        result = generate_article(
            topic="Vibe2Blog",
            session_summary="We built a Gradio app for turning coding sessions into Markdown.",
            language="en",
            tone="reflective",
        )
        markdown = result.generation.markdown

        self.assertIn("## Problem", markdown)
        self.assertIn("## Reflection", markdown)
        self.assertNotIn("## Fix Steps", markdown)

    def test_each_indonesian_tone_has_distinct_section_structure(self) -> None:
        common_input = {
            "topic": "Customer unable to update their own data via WooCommerce API",
            "session_summary": "WooCommerce passed object_type user, while the code checked customer.",
            "language": "id",
            "include_frontmatter": False,
        }

        outputs = {
            tone: generate_article(tone=tone, **common_input).generation.markdown
            for tone in ["reflective", "tutorial", "concise", "narrative"]
        }

        self.assertIn("## Masalah", outputs["reflective"])
        self.assertIn("## Refleksi", outputs["reflective"])
        self.assertIn("## Tujuan", outputs["tutorial"])
        self.assertIn("## Langkah Perbaikan", outputs["tutorial"])
        self.assertIn("## Ringkasan", outputs["concise"])
        self.assertIn("- Masalah:", outputs["concise"])
        self.assertIn("## Pembuka", outputs["narrative"])
        self.assertIn("## Momen Menemukan Akar Masalah", outputs["narrative"])
        self.assertEqual(len(set(outputs.values())), 4)

    def test_non_permission_bug_does_not_receive_permission_specific_template_copy(self) -> None:
        result = generate_article(
            topic="Fix modal bottom sheet overlaps with native navigation bottom bar",
            session_summary=(
                "The bottom sheet used fixed padding. The fix added useSafeAreaInsets "
                "and included insets.bottom in the bottom sheet padding calculation."
            ),
            language="id",
            tone="tutorial",
            include_frontmatter=False,
        )
        markdown = result.generation.markdown.lower()

        self.assertIn("safeareainsets", markdown)
        self.assertNotIn("permission", markdown)
        self.assertNotIn("autentikasi", markdown)
        self.assertNotIn("token", markdown)
        self.assertNotIn("role", markdown)

    def test_storytelling_internal_tone_uses_narrative_seed_structure(self) -> None:
        result = generate_article(
            topic="Fixing a Login Button That Stayed Disabled",
            session_summary="The login button used stale validity state and stayed disabled after valid input.",
            language="en",
            tone="human storytelling technical blog",
            include_frontmatter=False,
        )
        markdown = result.generation.markdown

        self.assertIn("## Opening", markdown)
        self.assertIn("## Finding the Root Cause", markdown)
        self.assertNotIn("## Goal", markdown)


if __name__ == "__main__":
    unittest.main()
