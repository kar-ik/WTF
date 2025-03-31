import unittest
from unittest.mock import patch
from framework import sql_injection_test, xss_test, csrf_test, insecure_headers_test, directory_bruteforce
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class TestSecurityFramework(unittest.TestCase):
    
    @patch('requests.get')
    def test_sql_injection_detection(self, mock_get):
        mock_get.return_value.text = "You have an error in your SQL syntax"
        mock_get.return_value.status_code = 200

        vulnerable_url = "http://example.com/search?query="
        non_vulnerable_url = "http://safe.com/"

        is_vulnerable, message = sql_injection_test(vulnerable_url)
        self.assertTrue(is_vulnerable)
        self.assertIn("SQL Injection vulnerability detected", message)

        mock_get.return_value.text = "No vulnerabilities found"
        
        is_vulnerable, message = sql_injection_test(non_vulnerable_url)
        self.assertFalse(is_vulnerable)
        self.assertIn("No SQL Injection vulnerability detected", message)

    @patch('requests.get')
    def test_xss_detection(self, mock_get):
        xss_payload = "<script>alert('XSS')</script>"
        mock_get.return_value.text = xss_payload

        vulnerable_url = "http://example.com/comment?message="
        non_vulnerable_url = "http://safe.com/"

        is_vulnerable, message = xss_test(vulnerable_url)
        self.assertTrue(is_vulnerable)
        self.assertIn("XSS vulnerability detected", message)

        mock_get.return_value.text = "No vulnerabilities found"
        
        is_vulnerable, message = xss_test(non_vulnerable_url)
        self.assertFalse(is_vulnerable)
        self.assertIn("No XSS vulnerability detected", message)

    @patch('requests.get')
    def test_csrf_detection(self, mock_get):
        mock_get.return_value.text = '<form action="/submit"></form>'

        vulnerable_url = "http://example.com/form"

        is_vulnerable, message = csrf_test(vulnerable_url)
        self.assertTrue(is_vulnerable)
        self.assertIn("Potential CSRF vulnerability detected!", message)

        mock_get.return_value.text = '<form action="/submit"><input type="hidden" name="csrf_token" value="token"></form>'

        is_vulnerable, message = csrf_test(vulnerable_url)
        self.assertFalse(is_vulnerable)
        self.assertIn("CSRF protection found", message)

    @patch('requests.get')
    def test_insecure_headers_detection(self, mock_get):
        mock_get.return_value.headers = {}

        vulnerable_url = "http://example.com/"

        is_vulnerable, message = insecure_headers_test(vulnerable_url)
        self.assertTrue(is_vulnerable)
        self.assertIn("X-Frame-Options missing", message)

        mock_get.return_value.headers = {
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'"
        }

        is_vulnerable, message = insecure_headers_test(vulnerable_url)
        self.assertFalse(is_vulnerable)
        self.assertIn("No insecure headers detected", message)

    @patch('requests.get')
    def test_directory_bruteforce(self, mock_get):
        mock_get.return_value.status_code = 200
        
        target_url = "http://example.com"
        
        is_vulnerable, message = directory_bruteforce(target_url)
        self.assertTrue(is_vulnerable)
        self.assertIn("Accessible directories", message)

        mock_get.return_value.status_code = 404
        
        is_vulnerable, message = directory_bruteforce(target_url)
        self.assertFalse(is_vulnerable)
        self.assertIn("No accessible directories found", message)


if __name__ == '__main__':
    unittest.main()
