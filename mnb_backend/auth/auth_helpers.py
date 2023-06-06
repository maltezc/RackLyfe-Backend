"""Helpers for the Auth module."""

import typing
import re
from mnb_backend.general_helpers import is_string


def is_valid_name(name):
    """
    Testing for if the name is valid"""
    # if name is None:
    #     return False
    if is_string(name) is False:
        return False

    regex_name_pattern = r"^[a-z ,.'-]+$"
    return bool(re.match(regex_name_pattern, name, re.IGNORECASE))  # add the re.IGNORECASE flag


def is_valid_email(email):
    """
    Validate email input."""
    if email is None:
        return False

    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))
