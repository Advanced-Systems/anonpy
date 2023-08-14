#!/usr/bin/env python3

from typing import Self

class SecurityWarning(Warning):
    def __init__(self: Self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return repr(self.message)
