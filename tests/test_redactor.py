from __future__ import annotations

import unittest

from vibe2blog.redactor import redact_secrets


class SecretRedactorTest(unittest.TestCase):
    def test_redacts_common_secret_patterns(self) -> None:
        text = "api_key=abc123 sk-abcdefghijklmnopqrstuvwxyz123456 hf_abcdefghijklmnopqrstuvwxyz"

        redacted = redact_secrets(text)

        self.assertIn("[REDACTED]", redacted)
        self.assertIn("[REDACTED_SECRET]", redacted)
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz123456", redacted)


if __name__ == "__main__":
    unittest.main()
