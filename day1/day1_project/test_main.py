"""Tests for main application."""
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure main is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main

class TestFetchPost(unittest.TestCase):
    @patch("main.requests.get")
    def test_fetch_post_success(self, mock_get):
        mock_get.return_value.json.return_value = {"id": 1, "title": "Test", "body": "Body"}
        mock_get.return_value.raise_for_status = MagicMock()
        result = main.fetch_post(1)
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["title"], "Test")

    @patch("main.requests.get")
    def test_fetch_post_http_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.exceptions.HTTPError("404")
        result = main.fetch_post(999)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
