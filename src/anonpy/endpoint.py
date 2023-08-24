#!/usr/bin/env python3

from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Endpoint:
    upload: str
    download: str
    preview: str
