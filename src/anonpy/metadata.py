#!/usr/bin/env python3

from importlib.metadata import metadata

from .internals import unique

__meta_data = metadata("anonpy")
__package__ = __meta_data["Name"]
__version__ = __meta_data["Version"]
__license__ = __meta_data["License"]
__credits__ = unique([
    __meta_data["Author"],
    __meta_data["Maintainer"],
])
