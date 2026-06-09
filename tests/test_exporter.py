from __future__ import annotations

import unittest

from vibe2blog.exporter import build_filename, slugify


class MarkdownExporterTest(unittest.TestCase):
    def test_slugify_and_filename(self) -> None:
        self.assertEqual(slugify("Hello, Vibe2Blog!"), "hello-vibe2blog")
        self.assertTrue(build_filename("Hello, Vibe2Blog!").endswith("hello-vibe2blog.md"))


if __name__ == "__main__":
    unittest.main()
