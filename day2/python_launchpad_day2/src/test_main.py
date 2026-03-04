"""Tests for main.py (Day 2)."""
import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Test that main module has expected constants (no network)
class TestMainConstants(unittest.TestCase):
    def test_app_name_defined(self):
        import main
        self.assertEqual(main.APP_NAME, "UserProfileService")
    def test_user_name_type(self):
        import main
        self.assertIsInstance(main.user_name, str)
        self.assertIsInstance(main.user_age, int)
if __name__ == "__main__":
    unittest.main()
