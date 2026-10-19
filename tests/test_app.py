import hashlib
import tempfile
import unittest
from pathlib import Path

from app import crack_hash_file, password_strength


class PasswordStrengthTests(unittest.TestCase):
    def test_short_password_is_not_strong(self):
        strength, feedback = password_strength("Ab1!")
        self.assertIn(strength, ("Weak 🔴", "Moderate 🟡"))
        self.assertTrue(feedback)

    def test_category_complete_password_scores_strong(self):
        strength, _ = password_strength("Train!ngPass2026")
        self.assertEqual(strength, "Strong 🟢")

    def test_common_password_is_flagged(self):
        strength, feedback = password_strength("password")
        self.assertEqual(strength, "Weak 🔴")
        self.assertTrue(any("common password" in item.lower() for item in feedback))


class DictionaryHashTests(unittest.TestCase):
    def test_sha256_candidate_is_found(self):
        candidate = "lab-only-password"
        digest = hashlib.sha256(candidate.encode()).hexdigest()

        with tempfile.TemporaryDirectory() as temp_dir:
            wordlist = Path(temp_dir) / "wordlist.txt"
            wordlist.write_text("not-the-password\nlab-only-password\n", encoding="utf-8")
            found, message = crack_hash_file(digest, wordlist)

        self.assertEqual(found, candidate)
        self.assertIn("SHA-256 match", message)

    def test_unsupported_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            wordlist = Path(temp_dir) / "wordlist.txt"
            wordlist.write_text("example\n", encoding="utf-8")
            found, message = crack_hash_file("not-a-supported-hash", wordlist)

        self.assertIsNone(found)
        self.assertIn("Unsupported hash format", message)


if __name__ == "__main__":
    unittest.main()
