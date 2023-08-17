#!/usr/bin/env python3

import base64
import os


def generate_random_password(length: int, encoding: str="utf-8") -> str:
    """
    Generate a cryptographically secure random password with a predefined length.
    """
    salt = os.urandom(length)
    return base64.b64encode(salt).decode(encoding)
