#!/usr/bin/env python3

import sys

from anonpy import AnonPy
from .cli import build_parser
from .internals import ConfigHandler
from .metadata import __package__, __version__


def cli() -> None:
    print(f"{__package__}, {__version__}")
    sys.exit(0)

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        pass
