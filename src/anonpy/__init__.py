#!/usr/bin/env python3
"""
anonpy
======

See https://github.com/advanced-systems/anonpy/ for documentation.

:copyright: (c) 2023 by Stefan Greve
:license: MIT License, see LICENSE for more details
"""

from .anonpy import AnonPy
from .endpoint import Endpoint
import sys

import sys

python_major, python_minor = (3,11)

try:
    assert sys.version_info >= (python_major, python_minor)
except AssertionError:
    raise RuntimeError(f"{__package__!r} requires Python {python_major}.{python_minor}+ (You have Python {sys.version})")
