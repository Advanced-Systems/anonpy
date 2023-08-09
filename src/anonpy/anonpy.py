#!/usr/bin/env python3

from .internals import RequestHandler, LogHandler

class AnonPy(RequestHandler, LogHandler):
    def __init__(self) -> None:
        super().__init__()
        print("anonpy ok!")
