#!/usr/bin/env python3
"""
anonpy
======

See https://github.com/advanced-systems/anonpy/ for documentation.

:copyright: (c) 2023 by Stefan Greve
:license: MIT License, see LICENSE for more details
"""

import sys

from .anonpy import AnonPy
from .internals.metadata import __package__
from .endpoint import Endpoint

python_major, python_minor = (3, 11)

try:
    assert sys.version_info >= (python_major, python_minor)
except AssertionError:
    raise RuntimeError(f"{__package__} requires {python_major}.{python_minor}+, but found {sys.version}")
