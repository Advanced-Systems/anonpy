#!/usr/bin/env python3

import sys
from importlib.metadata import metadata

from .cli import build_parser
from .internals import ConfigHandler, unique

__meta_data = metadata("anonpy")
__package__ = __meta_data["Name"]
__version__ = __meta_data["Version"]
__license__ = __meta_data["License"]
__credits__ = unique([
    __meta_data["Author"],
    __meta_data["Maintainer"],
])

def cli() -> None:
    print(f"{__package__}, {__version__}")
    sys.exit(0)

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        pass
