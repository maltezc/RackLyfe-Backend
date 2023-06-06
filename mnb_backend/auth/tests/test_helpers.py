"""Tests helpers for auth routes"""

# FLASK_DEBUG=test python3 -m unittest discover -s mnb_backend/users/tests -k class
# EXAMPLE: FLASK_DEBUG=test python3 -m unittest discover -s mnb_backend/users/tests -k UpdateSpecificUserTestCase

# FLASK_DEBUG=test python3 -m unittest discover -s mnb_backend/auth/tests -> runs all tests in file

from unittest import TestCase
from mnb_backend.auth.auth_helpers import is_valid_email, is_valid_name


class TestNameValidation(TestCase):
    def test_valid_names(self):
        self.assertTrue(is_valid_name("John"))
        self.assertTrue(is_valid_name("john doe"))
        self.assertTrue(is_valid_name("John Doe"))
        self.assertTrue(is_valid_name("John-Doe"))
        self.assertTrue(is_valid_name("O'Brien"))
        self.assertTrue(is_valid_name("John, Doe"))
        self.assertTrue(is_valid_name("john.doe"))

    def test_invalid_names(self):
        self.assertFalse(is_valid_name("1234"))  # numbers
        self.assertFalse(is_valid_name("john_doe"))  # underscores
        self.assertFalse(is_valid_name("john@doe"))  # @ symbol
        self.assertFalse(is_valid_name("john!"))  # exclamation point

    def test_edge_cases(self):
        self.assertFalse(is_valid_name(""))  # Empty string
        self.assertFalse(is_valid_name(None))  # None


class TestEmailValidation(TestCase):
    def test_valid_emails(self):
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertTrue(is_valid_email("john.doe@example.co.uk"))
        self.assertTrue(is_valid_email("user.name+tag+sorting@example.com"))
        self.assertTrue(is_valid_email("x@example.com"))  # One-letter local-parts are allowed

    def test_invalid_emails(self):
        self.assertFalse(is_valid_email("test@"))
        self.assertFalse(is_valid_email("@example.com"))
        self.assertFalse(is_valid_email("test@.com"))
        self.assertFalse(is_valid_email("test@com"))
        self.assertFalse(is_valid_email("test@example"))  # .com, .net, etc. is missing

    def test_edge_cases(self):
        self.assertFalse(is_valid_email(""))  # Empty string
        self.assertFalse(is_valid_email(None))  # None
