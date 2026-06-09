from __future__ import annotations

import unittest

from vibe2blog.validator import validate_markdown


class MarkdownValidatorTest(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
