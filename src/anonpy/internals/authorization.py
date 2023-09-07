#!/usr/bin/env python3

from enum import Enum, unique, auto

@unique
class Authorization(Enum):
    Basic: auto()
    Digest: auto()
