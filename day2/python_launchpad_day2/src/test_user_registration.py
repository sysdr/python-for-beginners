"""Tests for user_registration.py (Day 2)."""
import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
class TestUserRegistration(unittest.TestCase):
    def test_user_id_type(self):
        import user_registration
        self.assertIsInstance(user_registration.new_user_id, int)
    def test_email_type(self):
        import user_registration
        self.assertIsInstance(user_registration.new_user_email, str)
if __name__ == "__main__":
    unittest.main()
